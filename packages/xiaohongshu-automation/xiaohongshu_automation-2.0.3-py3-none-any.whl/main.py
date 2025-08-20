# local_api.py
from fastapi import FastAPI, Query, Body, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from pydantic import BaseModel
import subprocess
from xiaohongshu_tools import XiaohongshuTools, multi_account_manager
import logging
import time
import threading
from unti import get_news,get_comments_and_reply
from license_manager import LicenseManager
from template_loader import load_template, template_exists
import sys
from pathlib import Path
import os
import json
import uuid
from datetime import datetime
import requests
import hashlib
import shutil

# 定义请求模型
class PublishRequest(BaseModel):
    pic_urls: List[str]
    title: str
    content: str
    labels: Optional[List[str]] = None  # 添加可选的labels字段
    phone_number: Optional[str] = None  # 添加手机号字段用于多账号支持

class PrePublishRequest(BaseModel):
    pic_urls: List[str]
    title: str
    content: str
    labels: Optional[List[str]] = None
    phone_number: Optional[str] = None

class PrePublishUpdateRequest(BaseModel):
    pre_publish_id: str
    pic_urls: List[str]
    title: str
    content: str
    labels: Optional[List[str]] = None

class ActivationRequest(BaseModel):
    activation_code: str

class CommentRequest(BaseModel):
    comment: str
    metions_lists: Optional[List[str]] = None  # 添加可选的@提及列表字段
    phone_number: Optional[str] = None  # 添加手机号字段用于多账号支持

class AccountRequest(BaseModel):
    phone_number: str

class LoginRequest(BaseModel):
    phone_number: str
    verification_code: Optional[str] = None

class StatusRequest(BaseModel):
    phone_number: Optional[str] = None

class HistoryRequest(BaseModel):
    phone_number: Optional[str] = None
    history_type: Optional[str] = "all"  # all, publish, comment
    limit: Optional[int] = 50

class ImageDownloadRequest(BaseModel):
    pre_publish_id: str
    pic_urls: List[str]

class ProxyConfigRequest(BaseModel):
    phone_number: str
    proxy_config: dict  # 包含type, host, port, username, password等字段

class ProxyHistoryDeleteRequest(BaseModel):
    proxy_id: str

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 初始化许可证管理器
license_manager = LicenseManager()

# 预发布数据内存存储
# 数据结构: {phone_number: {pre_publish_id: pre_publish_data}}
pre_publish_storage = {}

# 预发布图片下载状态存储
# 数据结构: {pre_publish_id: {filename: {downloaded: bool, local_path: str, original_url: str, file_size: int, error: str}}}
pre_publish_images = {}

# 代理配置历史存储文件路径
proxy_history_file = Path("proxy_history.json")

# 创建静态文件目录
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# 创建预发布图片存储目录
pre_publish_images_dir = Path("pre_publish_images")
pre_publish_images_dir.mkdir(exist_ok=True)

# 添加静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# 在应用启动时检查许可证
@app.on_event("startup")
async def startup_event():
    """应用启动时的许可证检查"""
    print("\n" + "="*60)
    print("🚀 小红书自动化工具启动中...")
    print("="*60)
    
    # 检查许可证有效性
    if not license_manager.is_valid():
        expiry_info = license_manager.get_expiry_info()
        print(f"❌ 许可证验证失败: {expiry_info['message']}")
        print("💡 请使用激活码激活软件")
        print("📧 如需获取激活码，请联系软件提供商")
        print("="*60)
        
        # 显示激活码接口信息
        print("🔑 激活方式:")
        print("   方法1: 访问 http://localhost:8000/activate 网页激活")
        print("   方法2: 访问 http://localhost:8000/docs 使用API激活")
        print("   方法3: 使用命令行工具激活")
        print("="*60)
    else:
        expiry_info = license_manager.get_expiry_info()
        print(f"✅ 许可证验证成功")
        print(f"📅 有效期至: {expiry_info['expiry_date']}")
        print(f"⏰ 剩余时间: {expiry_info['remaining_days']} 天")
        print(f"🏷️ 许可证类型: {expiry_info['license_type']}")
        
        # 检查是否即将过期
        warning = license_manager.check_and_warn_expiry()
        if warning:
            print(f"⚠️ {warning}")
        
        print("="*60)

# 许可证中间件
@app.middleware("http")
async def license_middleware(request, call_next):
    """许可证验证中间件"""
    # 跳过许可证相关的接口
    license_exempt_paths = ["/", "/docs", "/openapi.json", "/license/status", "/license/activate", "/activate", "/static"]
    
    if any(request.url.path.startswith(path) for path in license_exempt_paths):
        response = await call_next(request)
        return response
    
    # 检查许可证
    if not license_manager.is_valid():
        raise HTTPException(status_code=403, detail={
            "error": "许可证无效或已过期",
            "message": "请激活软件后重试",
            "license_info": license_manager.get_expiry_info()
        })
    
    response = await call_next(request)
    return response

# 移除单一工具实例，改用多账号管理器
# tools = XiaohongshuTools()  # 注释掉原来的单账号实例

# ==================== 代理历史管理工具函数 ====================

def load_proxy_history():
    """
    加载代理配置历史记录
    :return: 代理配置历史列表
    """
    try:
        if proxy_history_file.exists():
            with open(proxy_history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"加载代理历史失败: {str(e)}")
        return []

def save_proxy_history(proxy_history):
    """
    保存代理配置历史记录
    :param proxy_history: 代理配置历史列表
    """
    try:
        with open(proxy_history_file, 'w', encoding='utf-8') as f:
            json.dump(proxy_history, f, ensure_ascii=False, indent=2)
        logger.info(f"代理历史已保存，共 {len(proxy_history)} 条记录")
    except Exception as e:
        logger.error(f"保存代理历史失败: {str(e)}")

def add_proxy_to_history(proxy_config):
    """
    将代理配置添加到历史记录
    :param proxy_config: 代理配置字典
    """
    try:
        if not proxy_config or not proxy_config.get('type'):
            return  # 空配置不保存
        
        proxy_history = load_proxy_history()
        
        # 生成代理的唯一标识
        proxy_key = f"{proxy_config['type']}://{proxy_config['host']}:{proxy_config['port']}"
        
        # 检查是否已经存在相同的代理配置
        for existing_proxy in proxy_history:
            existing_key = f"{existing_proxy['config']['type']}://{existing_proxy['config']['host']}:{existing_proxy['config']['port']}"
            if existing_key == proxy_key:
                # 更新最后使用时间
                existing_proxy['last_used'] = datetime.now().isoformat()
                existing_proxy['use_count'] = existing_proxy.get('use_count', 0) + 1
                save_proxy_history(proxy_history)
                logger.info(f"更新代理历史记录: {proxy_key}")
                return
        
        # 生成唯一ID
        proxy_id = str(uuid.uuid4())
        
        # 创建新的历史记录
        new_proxy_entry = {
            "id": proxy_id,
            "config": proxy_config.copy(),
            "name": f"{proxy_config['type'].upper()} {proxy_config['host']}:{proxy_config['port']}",
            "created_at": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat(),
            "use_count": 1
        }
        
        # 添加到历史记录开头（最新的在前面）
        proxy_history.insert(0, new_proxy_entry)
        
        # 限制历史记录数量（最多保存50条）
        if len(proxy_history) > 50:
            proxy_history = proxy_history[:50]
        
        save_proxy_history(proxy_history)
        logger.info(f"添加新代理到历史记录: {proxy_key}")
        
    except Exception as e:
        logger.error(f"添加代理到历史记录失败: {str(e)}")

def remove_proxy_from_history(proxy_id):
    """
    从历史记录中删除代理配置
    :param proxy_id: 代理配置ID
    :return: 是否删除成功
    """
    try:
        proxy_history = load_proxy_history()
        
        # 找到并删除指定ID的代理配置
        for i, proxy_entry in enumerate(proxy_history):
            if proxy_entry['id'] == proxy_id:
                deleted_proxy = proxy_history.pop(i)
                save_proxy_history(proxy_history)
                logger.info(f"删除代理历史记录: {deleted_proxy['name']}")
                return True
        
        logger.warning(f"未找到ID为 {proxy_id} 的代理历史记录")
        return False
        
    except Exception as e:
        logger.error(f"删除代理历史记录失败: {str(e)}")
        return False

# ==================== 工具函数 ====================

def extract_phone_numbers_from_cookies():
    """
    从cookies文件夹中提取手机号信息
    :return: 手机号列表和详细信息
    """
    cookies_dir = "cookies"
    phone_numbers = []
    cookie_files_info = []
    
    if not os.path.exists(cookies_dir):
        logger.info("cookies文件夹不存在")
        return phone_numbers, cookie_files_info
    
    try:
        # 遍历cookies文件夹中的所有文件
        for filename in os.listdir(cookies_dir):
            if filename.endswith('_xiaohongshu_cookies.json'):
                # 从文件名提取手机号 (格式: 手机号_xiaohongshu_cookies.json)
                phone_number = filename.replace('_xiaohongshu_cookies.json', '')
                if phone_number and phone_number.isdigit():
                    phone_numbers.append(phone_number)
                    
                    # 获取文件详细信息
                    file_path = os.path.join(cookies_dir, filename)
                    file_stat = os.stat(file_path)
                    file_size = file_stat.st_size
                    file_mtime = file_stat.st_mtime
                    
                    # 尝试读取cookies内容以获取更多信息
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            cookies_data = json.load(f)
                            cookies_count = len(cookies_data) if isinstance(cookies_data, list) else 0
                    except:
                        cookies_count = 0
                    
                    cookie_files_info.append({
                        'phone_number': phone_number,
                        'filename': filename,
                        'file_size': file_size,
                        'last_modified': file_mtime,
                        'cookies_count': cookies_count,
                        'file_path': file_path
                    })
            elif filename == 'xiaohongshu_cookies.json':
                # 处理没有手机号前缀的默认cookies文件
                file_path = os.path.join(cookies_dir, filename)
                file_stat = os.stat(file_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        cookies_data = json.load(f)
                        cookies_count = len(cookies_data) if isinstance(cookies_data, list) else 0
                except:
                    cookies_count = 0
                
                cookie_files_info.append({
                    'phone_number': 'default',
                    'filename': filename,
                    'file_size': file_stat.st_size,
                    'last_modified': file_stat.st_mtime,
                    'cookies_count': cookies_count,
                    'file_path': file_path
                })
        
        # 按手机号排序
        phone_numbers.sort()
        cookie_files_info.sort(key=lambda x: x['phone_number'])
        
        logger.info(f"从cookies文件夹中发现 {len(phone_numbers)} 个有效手机号")
        return phone_numbers, cookie_files_info
        
    except Exception as e:
        logger.error(f"读取cookies文件夹失败: {str(e)}")
        return [], []

def run_get_comments_and_reply():
    retry_count = 0
    max_retries = 5
    reply_count = 0
    while True:
        # 在后台任务中也检查许可证
        if not license_manager.is_valid():
            logger.warning("许可证已过期，停止后台任务")
            break
            
        try:
            url= "https://www.xiaohongshu.com/explore/67b94551000000002902b506?xsec_token=AB6AsqCQ2ck6I6ANbnEuEPHjAxMwvYCAm00BiLxfjU9o8=&xsec_source=pc_user"
            comments_data = get_comments_and_reply(url)
            logger.info("Successfully executed get_comments_and_reply()")
            reply_count += 1
            logger.info(f"Successfully executed get_comments_and_reply() {reply_count} times")
            retry_count = 0
        except Exception as e:
            if "[Errno 11001] getaddrinfo failed" or "network connectivity" in str(e):
                retry_count += 1
                if retry_count < max_retries:
                    logger.warning(f"getaddrinfo failed, retrying {retry_count}/{max_retries}...")
                    time.sleep(2)
                    continue
                else:
                    logger.error(f"Max retries ({max_retries}) reached. Continuing main loop...")
            logger.error(f"Error executing get_comments_and_reply(): {str(e)}")
            # Don't break the loop on error, continue to next iteration
        logger.info("等待3分钟，准备下次执行")
        time.sleep(3 * 60)  # Sleep for 3 minutes before next iteration

# Start the background thread
#comments_thread = threading.Thread(target=run_get_comments_and_reply, daemon=True)
#comments_thread.start()
#logger.info("Comments thread started successfully")

# ==================== 许可证管理接口 ====================

@app.get("/")
def read_root():
    """根路径，显示应用信息和许可证状态"""
    expiry_info = license_manager.get_expiry_info()
    
    # 获取当前账号信息
    try:
        accounts = multi_account_manager.list_accounts()
        current_account = multi_account_manager.current_account
        account_info = {
            "total_accounts": len(accounts),
            "current_account": current_account,
            "available_accounts": accounts[:3]  # 只显示前3个账号
        }
    except:
        account_info = {
            "total_accounts": 0,
            "current_account": None,
            "available_accounts": []
        }
    
    return {
        "app": "小红书自动化工具",
        "version": "2.0.0",
        "features": {
            "multi_account": True,
            "batch_operations": True,
            "account_isolation": True,
            "backward_compatible": True,
            "real_time_monitoring": True,
            "heartbeat_detection": True,
            "history_tracking": True
        },
        "account_info": account_info,
        "license_status": expiry_info,
        "pages": {
            "api_docs": "/docs",
            "activation_page": "/activate",
            "account_management": "/account/manage"
        },
        "guides": {
            "multi_account_guide": "查看 MULTI_ACCOUNT_GUIDE.md 了解多账号功能",
            "account_management": "访问 /account/manage 进行可视化账号管理"
        }
    }

@app.get("/activate", response_class=HTMLResponse)
async def activation_page():
    """许可证激活网页"""
    expiry_info = license_manager.get_expiry_info()
    machine_id = license_manager._get_machine_id()
    
    try:
        # 准备模板变量
        status_color = '#28a745' if expiry_info['valid'] else '#dc3545'
        license_status = '✅ 有效' if expiry_info['valid'] else '❌ ' + expiry_info['message']
        license_type = expiry_info.get('license_type', 'unknown')
        
        # 构建过期信息行
        expiry_rows = ""
        if expiry_info['valid']:
            expiry_rows += f'<div class="status-row"><span class="status-label">📅 有效期至:</span><span class="status-value">{expiry_info["expiry_date"]}</span></div>'
            expiry_rows += f'<div class="status-row"><span class="status-label">⏰ 剩余时间:</span><span class="status-value">{expiry_info["remaining_days"]} 天</span></div>'
        
        # 使用模板加载器
        html_content = load_template(
            "activate.html",
            status_color=status_color,
            license_status=license_status,
            license_type=license_type,
            machine_id=machine_id,
            expiry_rows=expiry_rows
        )
        
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        # 如果模板文件不存在，返回错误信息
        return HTMLResponse(content="<h1>模板文件未找到</h1><p>请确保 templates/activate.html 文件存在</p>", status_code=500)

@app.get("/license/status")
def get_license_status():
    """获取许可证状态"""
    try:
        expiry_info = license_manager.get_expiry_info()
        warning = license_manager.check_and_warn_expiry()
        
        return {
            "license_info": expiry_info,
            "warning": warning,
            "machine_id": license_manager._get_machine_id()
        }
    except Exception as e:
        return {"error": f"获取许可证状态失败: {str(e)}"}

@app.post("/license/activate")
def activate_license(request: ActivationRequest):
    """激活许可证"""
    try:
        result = license_manager.activate_with_code(request.activation_code)
        
        if result["success"]:
            logger.info(f"许可证激活成功: {result['message']}")
            return {
                "success": True,
                "message": result["message"],
                "new_expiry": result["new_expiry"],
                "extended_days": result["extended_days"]
            }
        else:
            logger.warning(f"许可证激活失败: {result['message']}")
            return {
                "success": False,
                "message": result["message"]
            }
    except Exception as e:
        error_msg = f"激活过程中发生错误: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "message": error_msg
        }

# ==================== 多账号管理接口 ====================

@app.post("/account/add")
def add_account(request: AccountRequest):
    """
    添加新账号
    """
    try:
        logger.info(f"添加新账号: {request.phone_number}")
        account = multi_account_manager.add_account(request.phone_number)
        return {
            "success": True,
            "message": f"账号 {request.phone_number} 添加成功",
            "phone_number": request.phone_number
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"添加账号失败: {request.phone_number} - {error_msg}")
        return {
            "success": False,
            "message": f"添加账号失败: {error_msg}"
        }

@app.get("/account/list")
def list_accounts():
    """
    获取所有账号列表
    """
    try:
        accounts = multi_account_manager.list_accounts()
        current_account = multi_account_manager.current_account
        return {
            "success": True,
            "accounts": accounts,
            "current_account": current_account,
            "total": len(accounts)
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"获取账号列表失败: {error_msg}")
        return {
            "success": False,
            "message": f"获取账号列表失败: {error_msg}",
            "accounts": []
        }

@app.post("/account/set_current")
def set_current_account(request: AccountRequest):
    """
    设置当前默认账号
    """
    try:
        multi_account_manager.set_current_account(request.phone_number)
        return {
            "success": True,
            "message": f"当前账号已设置为: {request.phone_number}",
            "current_account": request.phone_number
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"设置当前账号失败: {request.phone_number} - {error_msg}")
        return {
            "success": False,
            "message": f"设置当前账号失败: {error_msg}"
        }

@app.delete("/account/remove")
def remove_account(phone_number: str = Query(...)):
    """
    移除账号，同时关闭浏览器并删除cookies文件
    """
    try:
        logger.info(f"开始删除账号: {phone_number}")
        multi_account_manager.remove_account(phone_number)
        return {
            "success": True,
            "message": f"账号 {phone_number} 已移除，浏览器已关闭，cookies已删除"
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"移除账号失败: {phone_number} - {error_msg}")
        return {
            "success": False,
            "message": f"移除账号失败: {error_msg}"
        }

@app.post("/account/clear_cookies")
def clear_account_cookies(phone_number: str = Query(...)):
    """
    清理指定账号的cookies文件（不删除账号）
    """
    try:
        logger.info(f"开始清理账号 {phone_number} 的cookies")
        result = multi_account_manager.clear_account_cookies(phone_number)
        return {
            "success": True,
            "message": result
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"清理账号 {phone_number} cookies失败: {error_msg}")
        return {
            "success": False,
            "message": f"清理cookies失败: {error_msg}"
        }

@app.post("/account/stop_refresh")
def stop_account_refresh(phone_number: str = Query(...)):
    """
    停止指定账号的自动刷新任务
    """
    try:
        logger.info(f"开始停止账号 {phone_number} 的自动刷新任务")
        account = multi_account_manager.get_account(phone_number)
        account.stop_auto_refresh()
        return {
            "success": True,
            "message": f"账号 {phone_number} 自动刷新任务已停止"
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"停止账号 {phone_number} 自动刷新任务失败: {error_msg}")
        return {
            "success": False,
            "message": f"停止自动刷新任务失败: {error_msg}"
        }

@app.post("/account/start_refresh")
def start_account_refresh(phone_number: str = Query(...)):
    """
    启动指定账号的自动刷新任务
    """
    try:
        logger.info(f"开始启动账号 {phone_number} 的自动刷新任务")
        account = multi_account_manager.get_account(phone_number)
        account.auto_refresh()
        return {
            "success": True,
            "message": f"账号 {phone_number} 自动刷新任务已启动"
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"启动账号 {phone_number} 自动刷新任务失败: {error_msg}")
        return {
            "success": False,
            "message": f"启动自动刷新任务失败: {error_msg}"
        }

@app.post("/account/login")
def login_account(request: LoginRequest):
    """
    登录指定账号
    """
    try:
        account = multi_account_manager.get_account(request.phone_number)
        
        if request.verification_code:
            # 使用验证码登录
            result = account.login_with_verification_code(request.verification_code)
        else:
            # 无验证码登录
            result = account.login_without_verification_code()
        
        return {
            "success": True,
            "message": result,
            "phone_number": request.phone_number
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"账号登录失败: {request.phone_number} - {error_msg}")
        return {
            "success": False,
            "message": f"账号登录失败: {error_msg}"
        }

# ==================== 预发布管理接口 ====================

@app.post("/pre_publish/add")
def add_pre_publish(request: PrePublishRequest):
    """
    添加预发布内容
    """
    try:
        phone_number = request.phone_number or multi_account_manager.current_account
        if not phone_number:
            return {
                "success": False,
                "message": "未指定账号且无默认账号"
            }
        
        # 生成唯一ID
        pre_publish_id = str(uuid.uuid4())
        
        # 创建预发布数据
        pre_publish_data = {
            "id": pre_publish_id,
            "pic_urls": request.pic_urls,
            "title": request.title,
            "content": request.content,
            "labels": request.labels or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 初始化账号的预发布存储
        if phone_number not in pre_publish_storage:
            pre_publish_storage[phone_number] = {}
        
        # 保存预发布数据
        pre_publish_storage[phone_number][pre_publish_id] = pre_publish_data
        
        logger.info(f"账号 {phone_number} 添加预发布内容: {request.title}")
        return {
            "success": True,
            "message": "预发布内容添加成功",
            "pre_publish_id": pre_publish_id,
            "phone_number": phone_number
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"添加预发布内容失败: {error_msg}")
        return {
            "success": False,
            "message": f"添加预发布内容失败: {error_msg}"
        }

@app.get("/pre_publish/list")
def list_pre_publish(phone_number: Optional[str] = Query(None)):
    """
    获取预发布内容列表
    """
    try:
        if phone_number:
            # 获取指定账号的预发布内容
            pre_publishes = pre_publish_storage.get(phone_number, {})
            return {
                "success": True,
                "phone_number": phone_number,
                "pre_publishes": list(pre_publishes.values()),
                "count": len(pre_publishes)
            }
        else:
            # 获取所有账号的预发布内容
            all_pre_publishes = {}
            total_count = 0
            for acc_phone, pre_publishes in pre_publish_storage.items():
                all_pre_publishes[acc_phone] = list(pre_publishes.values())
                total_count += len(pre_publishes)
            
            return {
                "success": True,
                "all_pre_publishes": all_pre_publishes,
                "total_count": total_count
            }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"获取预发布内容失败: {error_msg}")
        return {
            "success": False,
            "message": f"获取预发布内容失败: {error_msg}"
        }

@app.put("/pre_publish/update")
def update_pre_publish(request: PrePublishUpdateRequest):
    """
    更新预发布内容
    """
    try:
        # 在所有账号中查找该预发布ID
        found_phone = None
        for phone_number, pre_publishes in pre_publish_storage.items():
            if request.pre_publish_id in pre_publishes:
                found_phone = phone_number
                break
        
        if not found_phone:
            return {
                "success": False,
                "message": "预发布内容不存在"
            }
        
        # 更新预发布数据
        pre_publish_data = pre_publish_storage[found_phone][request.pre_publish_id]
        pre_publish_data.update({
            "pic_urls": request.pic_urls,
            "title": request.title,
            "content": request.content,
            "labels": request.labels or [],
            "updated_at": datetime.now().isoformat()
        })
        
        logger.info(f"账号 {found_phone} 更新预发布内容: {request.title}")
        return {
            "success": True,
            "message": "预发布内容更新成功",
            "phone_number": found_phone
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"更新预发布内容失败: {error_msg}")
        return {
            "success": False,
            "message": f"更新预发布内容失败: {error_msg}"
        }

@app.delete("/pre_publish/delete")
def delete_pre_publish(pre_publish_id: str = Query(...)):
    """
    删除预发布内容
    """
    try:
        # 在所有账号中查找该预发布ID
        found_phone = None
        for phone_number, pre_publishes in pre_publish_storage.items():
            if pre_publish_id in pre_publishes:
                found_phone = phone_number
                break
        
        if not found_phone:
            return {
                "success": False,
                "message": "预发布内容不存在"
            }
        
        # 删除预发布数据
        title = pre_publish_storage[found_phone][pre_publish_id].get("title", "")
        del pre_publish_storage[found_phone][pre_publish_id]
        
        # 自动清理相关图片
        try:
            cleaned_files = 0
            # 清理内存记录
            if pre_publish_id in pre_publish_images:
                cleaned_files = len(pre_publish_images[pre_publish_id])
                del pre_publish_images[pre_publish_id]
            
            # 清理本地文件夹
            pre_publish_dir = pre_publish_images_dir / pre_publish_id
            if pre_publish_dir.exists():
                shutil.rmtree(str(pre_publish_dir))
                logger.info(f"已自动清理预发布 {pre_publish_id} 的 {cleaned_files} 个图片文件")
        except Exception as e:
            logger.warning(f"清理图片文件时出错: {str(e)}")
        
        logger.info(f"账号 {found_phone} 删除预发布内容: {title}")
        return {
            "success": True,
            "message": "预发布内容删除成功",
            "phone_number": found_phone
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"删除预发布内容失败: {error_msg}")
        return {
            "success": False,
            "message": f"删除预发布内容失败: {error_msg}"
        }

@app.post("/pre_publish/publish")
def publish_pre_publish(pre_publish_id: str = Query(...)):
    """
    发布预发布内容
    """
    try:
        # 在所有账号中查找该预发布ID
        found_phone = None
        pre_publish_data = None
        for phone_number, pre_publishes in pre_publish_storage.items():
            if pre_publish_id in pre_publishes:
                found_phone = phone_number
                pre_publish_data = pre_publishes[pre_publish_id]
                break
        
        if not found_phone or not pre_publish_data:
            return {
                "success": False,
                "message": "预发布内容不存在"
            }
        
        # 获取账号工具实例
        account = multi_account_manager.get_account(found_phone)
        
        # 发布内容
        logger.info(f"账号 {found_phone} 发布预发布内容: {pre_publish_data['title']}")
        urls = account.publish_xiaohongshu(
            pre_publish_data["pic_urls"],
            pre_publish_data["title"],
            pre_publish_data["content"],
            pre_publish_data["labels"]
        )
        
        if urls:
            # 发布成功，删除预发布数据
            del pre_publish_storage[found_phone][pre_publish_id]
            
            # 自动清理相关图片
            try:
                cleaned_files = 0
                # 清理内存记录
                if pre_publish_id in pre_publish_images:
                    cleaned_files = len(pre_publish_images[pre_publish_id])
                    del pre_publish_images[pre_publish_id]
                
                # 清理本地文件夹
                pre_publish_dir = pre_publish_images_dir / pre_publish_id
                if pre_publish_dir.exists():
                    shutil.rmtree(str(pre_publish_dir))
                    logger.info(f"发布后已自动清理预发布 {pre_publish_id} 的 {cleaned_files} 个图片文件")
            except Exception as e:
                logger.warning(f"发布后清理图片文件时出错: {str(e)}")
            
            logger.info(f"账号 {found_phone} 预发布内容发布成功: {pre_publish_data['title']}")
            return {
                "success": True,
                "message": "发布成功",
                "urls": urls,
                "phone_number": found_phone
            }
        else:
            logger.error(f"账号 {found_phone} 预发布内容发布失败: {pre_publish_data['title']}")
            return {
                "success": False,
                "message": "发布失败，未获得发布链接",
                "phone_number": found_phone
            }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"发布预发布内容失败: {error_msg}")
        return {
            "success": False,
            "message": f"发布失败: {error_msg}"
        }

@app.get("/pre_publish/get")
def get_pre_publish(pre_publish_id: str = Query(...)):
    """
    获取单个预发布内容详情
    """
    try:
        # 在所有账号中查找该预发布ID
        for phone_number, pre_publishes in pre_publish_storage.items():
            if pre_publish_id in pre_publishes:
                return {
                    "success": True,
                    "pre_publish": pre_publishes[pre_publish_id],
                    "phone_number": phone_number
                }
        
        return {
            "success": False,
            "message": "预发布内容不存在"
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"获取预发布内容详情失败: {error_msg}")
        return {
            "success": False,
            "message": f"获取预发布内容详情失败: {error_msg}"
        }

@app.get("/pre_publish/check_activity")
def check_pre_publish_activity(pre_publish_id: str = Query(...)):
    """
    检查预发布账号的最近活动状态
    """
    try:
        # 在所有账号中查找该预发布ID
        found_phone = None
        for phone_number, pre_publishes in pre_publish_storage.items():
            if pre_publish_id in pre_publishes:
                found_phone = phone_number
                break
        
        if not found_phone:
            return {
                "success": False,
                "message": "预发布内容不存在"
            }
        
        # 获取账号工具实例
        try:
            account = multi_account_manager.get_account(found_phone)
        except Exception as e:
            return {
                "success": False,
                "message": f"无法获取账号实例: {str(e)}"
            }
        
        # 检查最近活动状态
        is_recent, reason = account._check_recent_activity("发布")
        
        if is_recent:
            # 有最近活动，计算详细信息
            current_time = time.time()
            time_since_last_activity = current_time - account.last_activity
            remaining_time = account.operation_interval - time_since_last_activity
            
            # 格式化最后活动时间
            last_activity_datetime = datetime.fromtimestamp(account.last_activity)
            last_activity_time = last_activity_datetime.strftime("%Y-%m-%d %H:%M:%S")
            
            # 获取最近的历史记录来判断活动类型
            recent_history = account.get_history(limit=1)
            last_activity_type = "未知活动"
            if recent_history and len(recent_history) > 0:
                last_record = recent_history[0]
                if last_record.get("action_type") == "publish":
                    last_activity_type = f"发布笔记：《{last_record.get('title', '无标题')}》"
                elif last_record.get("action_type") == "comment":
                    last_activity_type = f"发布评论：{last_record.get('comment', '无内容')[:50]}..."
                else:
                    last_activity_type = f"{last_record.get('action_type', '未知')}操作"
            
            logger.info(f"账号 {found_phone} 检测到最近活动，距离上次活动 {time_since_last_activity:.1f} 秒")
            
            return {
                "success": True,
                "has_recent_activity": True,
                "phone_number": found_phone,
                "last_activity_time": last_activity_time,
                "last_activity_type": last_activity_type,
                "interval_seconds": account.operation_interval,
                "time_since_last_activity": round(time_since_last_activity, 1),
                "remaining_time": round(remaining_time, 1),
                "warning_message": reason
            }
        else:
            # 没有最近活动
            logger.info(f"账号 {found_phone} 无最近活动，可以安全发布")
            
            return {
                "success": True,
                "has_recent_activity": False,
                "phone_number": found_phone,
                "interval_seconds": account.operation_interval,
                "message": "账号活动状态正常，可以安全发布"
            }
    
    except Exception as e:
        error_msg = str(e)
        logger.error(f"检查预发布活动状态失败: {error_msg}")
        return {
            "success": False,
            "message": f"检查活动状态失败: {error_msg}"
        }

# ==================== 预发布图片管理接口 ====================

def download_image(url: str, save_path: str) -> dict:
    """
    下载单个图片
    :param url: 图片URL
    :param save_path: 保存路径
    :return: 下载结果
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        # 创建保存目录
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # 保存图片
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # 获取文件信息
        file_size = os.path.getsize(save_path)
        
        return {
            "success": True,
            "file_size": file_size,
            "local_path": save_path
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_filename_from_url(url: str, index: int) -> str:
    """
    从URL生成文件名
    """
    # 获取URL的哈希值以避免重复和特殊字符问题
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    
    # 尝试从URL获取文件扩展名
    parsed_url = url.split('?')[0]  # 移除查询参数
    if '.' in parsed_url:
        ext = parsed_url.split('.')[-1]
        if ext.lower() in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            return f"image_{index}_{url_hash}.{ext}"
    
    # 默认使用jpg扩展名
    return f"image_{index}_{url_hash}.jpg"

@app.post("/pre_publish/download_images")
def download_pre_publish_images(request: ImageDownloadRequest):
    """
    下载预发布内容的所有图片
    """
    try:
        pre_publish_id = request.pre_publish_id
        pic_urls = request.pic_urls
        
        if not pic_urls:
            return {
                "success": False,
                "message": "没有图片需要下载"
            }
        
        # 初始化图片存储信息
        if pre_publish_id not in pre_publish_images:
            pre_publish_images[pre_publish_id] = {}
        
        # 创建预发布ID专用目录
        pre_publish_dir = pre_publish_images_dir / pre_publish_id
        pre_publish_dir.mkdir(exist_ok=True)
        
        downloaded_count = 0
        failed_count = 0
        
        for i, url in enumerate(pic_urls):
            try:
                filename = get_filename_from_url(url, i)
                save_path = pre_publish_dir / filename
                
                # 如果文件已存在且已记录，跳过下载
                if filename in pre_publish_images[pre_publish_id] and pre_publish_images[pre_publish_id][filename].get("downloaded"):
                    logger.info(f"图片已存在，跳过下载: {filename}")
                    continue
                
                logger.info(f"开始下载图片: {url} -> {filename}")
                result = download_image(url, str(save_path))
                
                if result["success"]:
                    pre_publish_images[pre_publish_id][filename] = {
                        "downloaded": True,
                        "local_path": str(save_path),
                        "original_url": url,
                        "file_size": result["file_size"],
                        "filename": filename,
                        "error": None
                    }
                    downloaded_count += 1
                    logger.info(f"图片下载成功: {filename}")
                else:
                    pre_publish_images[pre_publish_id][filename] = {
                        "downloaded": False,
                        "local_path": None,
                        "original_url": url,
                        "file_size": 0,
                        "filename": filename,
                        "error": result["error"]
                    }
                    failed_count += 1
                    logger.error(f"图片下载失败: {filename}, 错误: {result['error']}")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"处理图片失败: {url}, 错误: {str(e)}")
        
        return {
            "success": True,
            "message": f"图片下载完成，成功: {downloaded_count}, 失败: {failed_count}",
            "downloaded_count": downloaded_count,
            "failed_count": failed_count,
            "pre_publish_id": pre_publish_id
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"下载图片失败: {error_msg}")
        return {
            "success": False,
            "message": f"下载图片失败: {error_msg}"
        }

@app.get("/pre_publish/get_images")
def get_pre_publish_images(pre_publish_id: str = Query(...)):
    """
    获取预发布内容的图片下载状态和信息
    """
    try:
        if pre_publish_id not in pre_publish_images:
            return {
                "success": True,
                "images": [],
                "message": "暂无图片信息"
            }
        
        images_info = []
        for filename, info in pre_publish_images[pre_publish_id].items():
            images_info.append({
                "filename": info["filename"],
                "downloaded": info["downloaded"],
                "local_path": info["local_path"],
                "original_url": info["original_url"],
                "file_size": info["file_size"],
                "error": info["error"]
            })
        
        return {
            "success": True,
            "images": images_info,
            "total_count": len(images_info),
            "downloaded_count": sum(1 for info in images_info if info["downloaded"]),
            "pre_publish_id": pre_publish_id
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"获取图片信息失败: {error_msg}")
        return {
            "success": False,
            "message": f"获取图片信息失败: {error_msg}"
        }

@app.get("/pre_publish/image/{pre_publish_id}/{filename}")
async def get_pre_publish_image(pre_publish_id: str, filename: str):
    """
    提供预发布图片文件访问服务
    """
    try:
        # 检查文件是否存在于记录中
        if pre_publish_id not in pre_publish_images or filename not in pre_publish_images[pre_publish_id]:
            raise HTTPException(status_code=404, detail="图片不存在")
        
        image_info = pre_publish_images[pre_publish_id][filename]
        if not image_info["downloaded"] or not image_info["local_path"]:
            raise HTTPException(status_code=404, detail="图片文件不存在")
        
        file_path = Path(image_info["local_path"])
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="图片文件不存在")
        
        # 返回图片文件
        return FileResponse(
            path=str(file_path),
            filename=filename,
            headers={"Cache-Control": "public, max-age=3600"}  # 缓存1小时
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取图片文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取图片文件失败: {str(e)}")

@app.delete("/pre_publish/cleanup_images")
def cleanup_pre_publish_images(pre_publish_id: str = Query(...)):
    """
    清理预发布内容相关的所有图片文件
    """
    try:
        cleaned_files = 0
        
        # 清理内存记录
        if pre_publish_id in pre_publish_images:
            cleaned_files = len(pre_publish_images[pre_publish_id])
            del pre_publish_images[pre_publish_id]
        
        # 清理本地文件夹
        pre_publish_dir = pre_publish_images_dir / pre_publish_id
        if pre_publish_dir.exists():
            shutil.rmtree(str(pre_publish_dir))
            logger.info(f"已删除预发布图片目录: {pre_publish_dir}")
        
        return {
            "success": True,
            "message": f"已清理 {cleaned_files} 个图片文件",
            "cleaned_files": cleaned_files,
            "pre_publish_id": pre_publish_id
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"清理图片失败: {error_msg}")
        return {
            "success": False,
            "message": f"清理图片失败: {error_msg}"
        }

# ==================== 状态监控接口 ====================

@app.get("/account/status")
def get_account_status(phone_number: Optional[str] = Query(None)):
    """获取账号状态"""
    try:
        if phone_number:
            # 获取指定账号状态
            account = multi_account_manager.get_account(phone_number)
            status = account.get_status()
            return {
                "success": True,
                "account_status": status,
                "timestamp": time.time()
            }
        else:
            # 获取所有账号状态
            all_status = multi_account_manager.get_all_status()
            return {
                "success": True,
                "all_accounts_status": all_status,
                "total_accounts": len(all_status),
                "timestamp": time.time()
            }
    except Exception as e:
        logger.error(f"获取账号状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取账号状态失败: {str(e)}")

@app.get("/account/history")
def get_account_history(
    phone_number: Optional[str] = Query(None),
    history_type: str = Query("all", description="历史类型: all, publish, comment"),
    limit: int = Query(50, ge=1, le=200, description="返回记录数限制")
):
    """获取账号历史记录"""
    try:
        if phone_number:
            # 获取指定账号历史
            history = multi_account_manager.get_account_history(phone_number, history_type, limit)
            return {
                "success": True,
                "phone_number": phone_number,
                "history_type": history_type,
                "history": history,
                "count": len(history),
                "timestamp": time.time()
            }
        else:
            # 获取所有账号历史汇总
            all_history = multi_account_manager.get_all_history(history_type, limit)
            total_count = sum(len(history) for history in all_history.values())
            return {
                "success": True,
                "history_type": history_type,
                "all_accounts_history": all_history,
                "total_count": total_count,
                "accounts_count": len(all_history),
                "timestamp": time.time()
            }
    except Exception as e:
        logger.error(f"获取历史记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")

@app.get("/account/cookies_history")
def get_cookies_history():
    """获取cookies文件夹中的历史账号信息"""
    try:
        phone_numbers, cookie_files_info = extract_phone_numbers_from_cookies()
        
        # 格式化时间和文件大小
        formatted_info = []
        for info in cookie_files_info:
            formatted_info.append({
                'phone_number': info['phone_number'],
                'filename': info['filename'],
                'file_size_bytes': info['file_size'],
                'file_size_kb': round(info['file_size'] / 1024, 2),
                'last_modified_timestamp': info['last_modified'],
                'last_modified_date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info['last_modified'])),
                'cookies_count': info['cookies_count'],
                'is_active': info['phone_number'] in multi_account_manager.list_accounts()
            })
        
        return {
            "success": True,
            "message": f"发现 {len(phone_numbers)} 个历史账号",
            "phone_numbers": phone_numbers,
            "cookies_files": formatted_info,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"获取cookies历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取cookies历史失败: {str(e)}")

@app.post("/account/add_from_cookies")
def add_account_from_cookies(phone_number: str = Query(...)):
    """从cookies历史中添加账号"""
    try:
        # 检查cookies文件是否存在
        phone_numbers, cookie_files_info = extract_phone_numbers_from_cookies()
        
        if phone_number not in phone_numbers:
            return {
                "success": False,
                "message": f"未找到手机号 {phone_number} 的cookies文件"
            }
        
        # 添加账号
        account = multi_account_manager.add_account(phone_number)
        
        return {
            "success": True,
            "message": f"从cookies历史中成功添加账号 {phone_number}",
            "phone_number": phone_number
        }
    except Exception as e:
        logger.error(f"从cookies添加账号失败: {str(e)}")
        return {
            "success": False,
            "message": f"从cookies添加账号失败: {str(e)}"
        }

@app.post("/account/heartbeat")
def update_account_heartbeat(phone_number: Optional[str] = Query(None)):
    """手动更新账号心跳"""
    try:
        if phone_number:
            account = multi_account_manager.get_account(phone_number)
            account.update_heartbeat()
            return {
                "success": True,
                "message": f"账号 {phone_number} 心跳已更新",
                "timestamp": time.time()
            }
        else:
            # 更新所有账号心跳
            updated_accounts = []
            for account_phone in multi_account_manager.list_accounts():
                try:
                    account = multi_account_manager.get_account(account_phone)
                    account.update_heartbeat()
                    updated_accounts.append(account_phone)
                except:
                    pass
            return {
                "success": True,
                "message": f"已更新 {len(updated_accounts)} 个账号的心跳",
                "updated_accounts": updated_accounts,
                "timestamp": time.time()
            }
    except Exception as e:
        logger.error(f"更新心跳失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新心跳失败: {str(e)}")

@app.post("/account/set_default")
def set_default_account(phone_number: str = Query(...)):
    """设置默认账号"""
    try:
        multi_account_manager.set_current_account(phone_number)
        return {
            "success": True,
            "message": f"已设置 {phone_number} 为默认账号",
            "current_account": multi_account_manager.current_account,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"设置默认账号失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"设置默认账号失败: {str(e)}")

# ==================== 代理管理接口 ====================

@app.get("/account/get_proxy")
def get_account_proxy(phone_number: str = Query(...)):
    """获取账号当前代理配置"""
    try:
        account = multi_account_manager.get_account(phone_number)
        proxy_config = account.get_proxy_config() if hasattr(account, 'get_proxy_config') else None
        
        # 检查代理连接状态
        connection_status = "未知"
        if proxy_config and proxy_config.get('type'):
            try:
                # 尝试测试代理连接
                connection_status = account.test_proxy_connection() if hasattr(account, 'test_proxy_connection') else "未测试"
            except:
                connection_status = "连接失败"
        else:
            connection_status = "无代理"
        
        return {
            "success": True,
            "proxy_config": proxy_config,
            "connection_status": connection_status,
            "phone_number": phone_number,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"获取账号 {phone_number} 代理配置失败: {str(e)}")
        return {
            "success": False,
            "message": f"获取代理配置失败: {str(e)}",
            "proxy_config": None
        }

@app.get("/account/get_proxy_history")
def get_proxy_history():
    """获取代理配置历史记录"""
    try:
        proxy_history = load_proxy_history()
        
        # 按最后使用时间排序
        proxy_history.sort(key=lambda x: x.get('last_used', ''), reverse=True)
        
        return {
            "success": True,
            "proxy_history": proxy_history,
            "total_count": len(proxy_history),
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"获取代理历史失败: {str(e)}")
        return {
            "success": False,
            "message": f"获取代理历史失败: {str(e)}",
            "proxy_history": []
        }

@app.delete("/account/delete_proxy_history")
def delete_proxy_history(request: ProxyHistoryDeleteRequest):
    """删除代理配置历史记录"""
    try:
        success = remove_proxy_from_history(request.proxy_id)
        
        if success:
            return {
                "success": True,
                "message": "代理历史记录删除成功",
                "proxy_id": request.proxy_id
            }
        else:
            return {
                "success": False,
                "message": "未找到指定的代理历史记录"
            }
    except Exception as e:
        logger.error(f"删除代理历史记录失败: {str(e)}")
        return {
            "success": False,
            "message": f"删除代理历史记录失败: {str(e)}"
        }

@app.post("/account/set_proxy")
def set_account_proxy(request: ProxyConfigRequest):
    """设置账号代理配置"""
    try:
        account = multi_account_manager.get_account(request.phone_number)
        proxy_config = request.proxy_config
        
        # 验证代理配置
        if proxy_config.get('type') and proxy_config['type'] not in ['http', 'https', 'socks4', 'socks5']:
            return {
                "success": False,
                "message": "不支持的代理类型"
            }
        
        # 如果设置了代理类型，确保有必要的参数
        if proxy_config.get('type'):
            if not proxy_config.get('host') or not proxy_config.get('port'):
                return {
                    "success": False,
                    "message": "代理服务器地址和端口不能为空"
                }
            
            # 验证端口范围
            try:
                port = int(proxy_config['port'])
                if port < 1 or port > 65535:
                    return {
                        "success": False,
                        "message": "端口号必须在1-65535之间"
                    }
                proxy_config['port'] = port
            except (ValueError, TypeError):
                return {
                    "success": False,
                    "message": "端口号必须是有效的数字"
                }
        
        # 应用代理设置
        if hasattr(account, 'set_proxy_config'):
            result = account.set_proxy_config(proxy_config)
            if result:
                # 保存到历史记录（只有配置成功才保存）
                if proxy_config.get('type'):
                    add_proxy_to_history(proxy_config)
                
                logger.info(f"账号 {request.phone_number} 代理设置成功: {proxy_config.get('type', '无代理')}")
                return {
                    "success": True,
                    "message": "代理设置已应用",
                    "proxy_config": proxy_config,
                    "phone_number": request.phone_number
                }
            else:
                return {
                    "success": False,
                    "message": "代理设置应用失败"
                }
        else:
            # 如果账号工具类没有代理设置方法，返回提示
            return {
                "success": False,
                "message": "该账号工具版本不支持代理设置功能"
            }
            
    except Exception as e:
        logger.error(f"设置账号 {request.phone_number} 代理失败: {str(e)}")
        return {
            "success": False,
            "message": f"设置代理失败: {str(e)}"
        }

@app.post("/account/clear_proxy")
def clear_account_proxy(request: AccountRequest):
    """清除账号代理设置"""
    try:
        account = multi_account_manager.get_account(request.phone_number)
        
        # 清除代理设置（设置为空配置）
        empty_proxy_config = {
            "type": None,
            "host": None,
            "port": None,
            "username": None,
            "password": None
        }
        
        if hasattr(account, 'set_proxy_config'):
            result = account.set_proxy_config(empty_proxy_config)
            if result:
                logger.info(f"账号 {request.phone_number} 代理设置已清除")
                return {
                    "success": True,
                    "message": "代理设置已清除",
                    "phone_number": request.phone_number
                }
            else:
                return {
                    "success": False,
                    "message": "清除代理设置失败"
                }
        else:
            return {
                "success": False,
                "message": "该账号工具版本不支持代理设置功能"
            }
            
    except Exception as e:
        logger.error(f"清除账号 {request.phone_number} 代理失败: {str(e)}")
        return {
            "success": False,
            "message": f"清除代理失败: {str(e)}"
        }

@app.post("/account/restart_browser")
def restart_account_browser(request: AccountRequest):
    """重启账号浏览器以应用代理设置"""
    try:
        account = multi_account_manager.get_account(request.phone_number)
        
        logger.info(f"开始重启账号 {request.phone_number} 的浏览器")
        
        # 执行浏览器重启
        if hasattr(account, 'restart_browser'):
            result = account.restart_browser()
            if result:
                logger.info(f"账号 {request.phone_number} 浏览器重启成功")
                return {
                    "success": True,
                    "message": "浏览器重启成功，代理设置已生效",
                    "phone_number": request.phone_number
                }
            else:
                return {
                    "success": False,
                    "message": "浏览器重启失败"
                }
        elif hasattr(account, 'close_browser') and hasattr(account, 'init_browser'):
            # 如果没有直接的重启方法，尝试关闭后重新初始化
            try:
                account.close_browser()
                time.sleep(2)  # 等待浏览器完全关闭
                account.init_browser()
                logger.info(f"账号 {request.phone_number} 浏览器重启成功（通过关闭重开）")
                return {
                    "success": True,
                    "message": "浏览器重启成功，代理设置已生效",
                    "phone_number": request.phone_number
                }
            except Exception as e:
                logger.error(f"浏览器重启失败: {str(e)}")
                return {
                    "success": False,
                    "message": f"浏览器重启失败: {str(e)}"
                }
        else:
            return {
                "success": False,
                "message": "该账号工具版本不支持浏览器重启功能"
            }
            
    except Exception as e:
        logger.error(f"重启账号 {request.phone_number} 浏览器失败: {str(e)}")
        return {
            "success": False,
            "message": f"重启浏览器失败: {str(e)}"
        }

@app.post("/account/test_proxy")
def test_account_proxy(request: AccountRequest):
    """测试账号代理连接"""
    try:
        account = multi_account_manager.get_account(request.phone_number)
        
        logger.info(f"开始测试账号 {request.phone_number} 的代理连接")
        
        # 获取当前代理配置
        proxy_config = account.get_proxy_config() if hasattr(account, 'get_proxy_config') else None
        
        if not proxy_config or not proxy_config.get('type'):
            return {
                "success": True,
                "test_result": {
                    "connected": True,
                    "message": "当前未使用代理，直连网络正常",
                    "ip": "直连",
                    "latency": 0
                },
                "phone_number": request.phone_number
            }
        
        # 测试代理连接
        if hasattr(account, 'test_proxy_connection'):
            test_result = account.test_proxy_connection()
            logger.info(f"账号 {request.phone_number} 代理测试完成: {test_result}")
            return {
                "success": True,
                "test_result": test_result,
                "phone_number": request.phone_number
            }
        else:
            # 简单的连接测试
            try:
                import requests
                
                # 构建代理URL
                proxy_url = f"{proxy_config['type']}://"
                if proxy_config.get('username') and proxy_config.get('password'):
                    proxy_url += f"{proxy_config['username']}:{proxy_config['password']}@"
                proxy_url += f"{proxy_config['host']}:{proxy_config['port']}"
                
                proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                
                # 测试连接
                start_time = time.time()
                response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
                latency = int((time.time() - start_time) * 1000)
                
                if response.status_code == 200:
                    ip_info = response.json()
                    return {
                        "success": True,
                        "test_result": {
                            "connected": True,
                            "ip": ip_info.get('origin', '未知'),
                            "latency": latency,
                            "message": "代理连接正常"
                        },
                        "phone_number": request.phone_number
                    }
                else:
                    return {
                        "success": True,
                        "test_result": {
                            "connected": False,
                            "error": f"HTTP {response.status_code}",
                            "message": "代理服务器响应异常"
                        },
                        "phone_number": request.phone_number
                    }
                    
            except Exception as test_error:
                return {
                    "success": True,
                    "test_result": {
                        "connected": False,
                        "error": str(test_error),
                        "message": "代理连接测试失败"
                    },
                    "phone_number": request.phone_number
                }
                
    except Exception as e:
        logger.error(f"测试账号 {request.phone_number} 代理连接失败: {str(e)}")
        return {
            "success": False,
            "message": f"测试代理连接失败: {str(e)}"
        }

# ==================== 账号管理网页 ====================

@app.get("/account/manage", response_class=HTMLResponse)
async def account_management_page():
    """账号管理网页"""
    try:
        # 使用模板加载器
        html_content = load_template("account_manage.html")
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        # 如果模板文件不存在，返回错误信息
        return HTMLResponse(content="<h1>模板文件未找到</h1><p>请确保 templates/account_manage.html 文件存在</p>", status_code=500)

# ==================== 原有业务接口 ====================

@app.post("/publish")
def publish(request: PublishRequest):
    """
    发布内容到小红书
    支持 JSON 请求体，避免 URL 过长问题
    支持多账号发布，可指定phone_number参数选择发布账号
    """
    try:
        # 获取指定账号的工具实例
        account = multi_account_manager.get_account(request.phone_number)
        
        account_info = request.phone_number or multi_account_manager.current_account or "默认账号"
        logger.info(f"使用账号 {account_info} 发布内容: {request.title}")
        
        urls = account.publish_xiaohongshu(
            request.pic_urls, 
            request.title, 
            request.content, 
            request.labels  # 传递labels参数
        )
        if urls:    
            logger.info(f"账号 {account_info} 发布成功: {request.title}")
            return {
                "status": "success", 
                "urls": urls,
                 "account": account_info,
                "machine_id": license_manager._get_machine_id()
            }
        else:
            logger.error(f"账号 {account_info} 发布失败，未返回URL: {request.title}")
            return {
                "status": "error", 
                "message": "发布失败，未获得发布链接",
                "account": account_info,
                "machine_id": license_manager._get_machine_id()
            }
    except Exception as e:
        error_msg = str(e)
        account_info = request.phone_number or multi_account_manager.current_account or "默认账号"
        logger.error(f"账号 {account_info} 发布异常: {request.title} - {error_msg}")
        return {
            "status": "error", 
            "message": error_msg,
            "account": account_info,
            "machine_id": license_manager._get_machine_id()
        }
    
    
@app.post("/post_comments")
def post_comments(
    comments_response: dict[str,List[dict]] = Body(...),
    url: str = Query(...),
    phone_number: Optional[str] = Query(None)
):
    try:
        # 获取指定账号的工具实例
        account = multi_account_manager.get_account(phone_number)
        account_info = phone_number or multi_account_manager.current_account or "默认账号"
        
        logger.info(f"使用账号 {account_info} 回复评论")
        account.reply_comments(comments_response, url)
        return {
            "message": "success",
            "account": account_info
        }
    except Exception as e:
        account_info = phone_number or multi_account_manager.current_account or "默认账号"
        message = f"账号 {account_info} 评论回复失败: {str(e)}"
        logger.error(message)
        return {
            "message": message,
            "account": account_info
        }
    
@app.get("/get_comments")
def get_comments(url: str, phone_number: Optional[str] = Query(None)):
    try:
        # 获取指定账号的工具实例
        account = multi_account_manager.get_account(phone_number)
        account_info = phone_number or multi_account_manager.current_account or "默认账号"
        
        logger.info(f"使用账号 {account_info} 获取评论")
        comments = account.get_comments(url)
        if comments == "当前无评论":
            return {
                "status": "success", 
                "message": "当前无评论",
                "account": account_info
            }
        return {
            "status": "success", 
            "comments": comments,
            "account": account_info
        }
    except Exception as e:
        account_info = phone_number or multi_account_manager.current_account or "默认账号"
        message = f"账号 {account_info} 获取评论失败: {str(e)}"
        logger.error(message)
        return {
            "status": "error", 
            "message": message,
            "account": account_info
        }

@app.get("/search_notes")
def search_notes(
    keywords: str = Query(...), 
    limit: int = Query(5, ge=1, le=20),
    phone_number: Optional[str] = Query(None)
):
    """
    搜索小红书笔记
    
    Args:
        keywords: 搜索关键词
        limit: 返回结果数量限制，最多20条
        phone_number: 可选的账号手机号，用于多账号支持
    """
    try:
        # 获取指定账号的工具实例
        account = multi_account_manager.get_account(phone_number)
        account_info = phone_number or multi_account_manager.current_account or "默认账号"
        
        logger.info(f"使用账号 {account_info} 搜索: {keywords}, 限制: {limit}")
        result = account.search_notes(keywords, limit)
        logger.info(f"账号 {account_info} 搜索完成: {keywords} - 找到 {len(result.get('data', []))} 条结果")
        
        # 在结果中添加账号信息
        if isinstance(result, dict):
            result["account"] = account_info
        
        return result
    except Exception as e:
        account_info = phone_number or multi_account_manager.current_account or "默认账号"
        error_msg = str(e)
        logger.error(f"账号 {account_info} 搜索异常: {keywords} - {error_msg}")
        return {
            "success": False,
            "message": f"搜索失败: {error_msg}",
            "data": [],
            "account": account_info
        }

@app.get("/get_note_content")
def get_note_content(url: str = Query(...), phone_number: Optional[str] = Query(None)):
    """
    获取小红书笔记的详细内容
    
    Args:
        url: 小红书笔记URL
        phone_number: 可选的账号手机号，用于多账号支持
    """
    try:
        # 获取指定账号的工具实例
        account = multi_account_manager.get_account(phone_number)
        account_info = phone_number or multi_account_manager.current_account or "默认账号"
        
        logger.info(f"使用账号 {account_info} 获取笔记内容: {url}")
        result = account.get_note_content(url)
        
        # 在结果中添加账号信息
        if isinstance(result, dict):
            result["account"] = account_info
        
        if result.get("success"):
            logger.info(f"账号 {account_info} 笔记内容获取成功: {url}")
        else:
            logger.warning(f"账号 {account_info} 笔记内容获取失败: {url} - {result.get('message', '未知错误')}")
        return result
    except Exception as e:
        account_info = phone_number or multi_account_manager.current_account or "默认账号"
        error_msg = str(e)
        logger.error(f"账号 {account_info} 获取笔记内容异常: {url} - {error_msg}")
        return {
            "success": False,
            "message": f"获取笔记内容失败: {error_msg}",
            "data": {},
            "account": account_info
        }

@app.get("/analyze_note")
def analyze_note(url: str = Query(...), phone_number: Optional[str] = Query(None)):
    """
    分析小红书笔记内容，提取关键信息和领域标签
    
    Args:
        url: 小红书笔记URL
        phone_number: 可选的账号手机号，用于多账号支持
    """
    try:
        # 获取指定账号的工具实例
        account = multi_account_manager.get_account(phone_number)
        account_info = phone_number or multi_account_manager.current_account or "默认账号"
        
        logger.info(f"使用账号 {account_info} 分析笔记: {url}")
        result = account.analyze_note(url)
        
        # 在结果中添加账号信息
        if isinstance(result, dict):
            result["account"] = account_info
        
        if result.get("success"):
            logger.info(f"账号 {account_info} 笔记分析成功: {url} - 主要领域: {result.get('data', {}).get('领域分析', {}).get('主要领域', [])}")
        else:
            logger.warning(f"账号 {account_info} 笔记分析失败: {url} - {result.get('message', '未知错误')}")
        return result
    except Exception as e:
        account_info = phone_number or multi_account_manager.current_account or "默认账号"
        error_msg = str(e)
        logger.error(f"账号 {account_info} 笔记分析异常: {url} - {error_msg}")
        return {
            "success": False,
            "message": f"笔记分析失败: {error_msg}",
            "data": {},
            "account": account_info
        }

@app.post("/post_comment")
def post_comment(url: str = Query(...), request: CommentRequest = Body(...)):
    """
    发布评论到指定小红书笔记
    
    Args:
        url: 小红书笔记URL
        request: 评论请求体，包含评论内容和可选的@提及列表
            - comment: 要发布的评论内容
            - metions_lists: 可选的@提及用户名列表，例如 ["用户1", "用户2"]
            - phone_number: 可选的账号手机号，用于多账号支持
    """
    try:
        # 获取指定账号的工具实例
        account = multi_account_manager.get_account(request.phone_number)
        account_info = request.phone_number or multi_account_manager.current_account or "默认账号"
        
        logger.info(f"使用账号 {account_info} 发布评论: {url}")
        logger.info(f"评论内容: {request.comment}")
        if request.metions_lists:
            logger.info(f"@ 提及列表: {request.metions_lists}")
        
        result = account.post_comment(url, request.comment, request.metions_lists)
        
        # 在结果中添加账号信息和机器ID
        if isinstance(result, dict):
            result["account"] = account_info
            result["machine_id"] = license_manager._get_machine_id()
        
        if result.get("success"):
            logger.info(f"账号 {account_info} 评论发布成功: {url}")
            if request.metions_lists:
                logger.info(f"包含 {len(request.metions_lists)} 个 @ 提及")
        else:
            logger.warning(f"账号 {account_info} 评论发布失败: {url} - {result.get('message', '未知错误')}")
        return result
    except Exception as e:
        account_info = request.phone_number or multi_account_manager.current_account or "默认账号"
        error_msg = str(e)
        logger.error(f"账号 {account_info} 评论发布异常: {url} - {error_msg}")
        return {
            "success": False,
            "message": f"评论发布失败: {error_msg}",
            "data": {},
            "account": account_info,
            "machine_id": license_manager._get_machine_id()
        }

@app.post("/like_note")
def like_note(url: str = Query(...), phone_number: Optional[str] = Query(None)):
    """
    为指定小红书笔记点赞
    
    Args:
        url: 小红书笔记URL
        phone_number: 可选的账号手机号，用于多账号支持
    """
    try:
        # 获取指定账号的工具实例
        account = multi_account_manager.get_account(phone_number)
        account_info = phone_number or multi_account_manager.current_account or "默认账号"
        
        logger.info(f"使用账号 {account_info} 为笔记点赞: {url}")
        
        result = account.like_note(url)
        
        # 在结果中添加账号信息和机器ID
        if isinstance(result, dict):
            result["account"] = account_info
            result["machine_id"] = license_manager._get_machine_id()
        
        if result.get("success"):
            logger.info(f"账号 {account_info} 点赞成功: {url} - {result.get('data', {}).get('like_status', '未知状态')}")
        else:
            logger.warning(f"账号 {account_info} 点赞失败: {url} - {result.get('message', '未知错误')}")
        return result
    except Exception as e:
        account_info = phone_number or multi_account_manager.current_account or "默认账号"
        error_msg = str(e)
        logger.error(f"账号 {account_info} 点赞异常: {url} - {error_msg}")
        return {
            "success": False,
            "message": f"点赞失败: {error_msg}",
            "data": {},
            "account": account_info,
            "machine_id": license_manager._get_machine_id()
        }

@app.post("/collect_note")
def collect_note(url: str = Query(...), phone_number: Optional[str] = Query(None)):
    """
    收藏指定小红书笔记
    
    Args:
        url: 小红书笔记URL
        phone_number: 可选的账号手机号，用于多账号支持
    """
    try:
        # 获取指定账号的工具实例
        account = multi_account_manager.get_account(phone_number)
        account_info = phone_number or multi_account_manager.current_account or "默认账号"
        
        logger.info(f"使用账号 {account_info} 收藏笔记: {url}")
        
        result = account.collect_note(url)
        
        # 在结果中添加账号信息和机器ID
        if isinstance(result, dict):
            result["account"] = account_info
            result["machine_id"] = license_manager._get_machine_id()
        
        if result.get("success"):
            logger.info(f"账号 {account_info} 收藏成功: {url} - {result.get('data', {}).get('collect_status', '未知状态')}")
        else:
            logger.warning(f"账号 {account_info} 收藏失败: {url} - {result.get('message', '未知错误')}")
        return result
    except Exception as e:
        account_info = phone_number or multi_account_manager.current_account or "默认账号"
        error_msg = str(e)
        logger.error(f"账号 {account_info} 收藏异常: {url} - {error_msg}")
        return {
            "success": False,
            "message": f"收藏失败: {error_msg}",
            "data": {},
            "account": account_info,
            "machine_id": license_manager._get_machine_id()
        }

def check_license_on_startup():
    """启动时检查许可证"""
    print("\n" + "="*60)
    print("🔍 正在检查软件许可证...")
    print("="*60)
    
    if not license_manager.is_valid():
        expiry_info = license_manager.get_expiry_info()
        print(f"❌ 许可证验证失败: {expiry_info['message']}")
        print("💡 软件将以受限模式运行")
        print("🔑 请访问激活页面获取激活码")
        print("="*60)
        return False
    else:
        expiry_info = license_manager.get_expiry_info()
        print(f"✅ 许可证验证成功")
        print(f"📅 有效期至: {expiry_info['expiry_date']}")
        print(f"⏰ 剩余时间: {expiry_info['remaining_days']} 天")
        
        # 检查即将过期提醒
        warning = license_manager.check_and_warn_expiry()
        if warning:
            print(f"⚠️ {warning}")
        
        print("="*60)
        return True

def main():
    """主函数入口点，用于uvx调用"""
    import uvicorn
    import threading
    import time

    # 启动时检查许可证
    check_license_on_startup()

    def run_get_news():
        while True:
            # 在后台任务中也检查许可证
            if not license_manager.is_valid():
                logger.warning("许可证已过期，停止后台新闻任务")
                break
                
            try:
                time.sleep(10)
                get_news()
                logger.info("Successfully executed get_news()")
            except Exception as e:
                logger.error(f"Error executing get_news(): {str(e)}")
            time.sleep(6 * 60 * 60)  # Sleep for 6 hours

    # Start the background thread
    #news_thread = threading.Thread(target=run_get_news, daemon=True)
    #news_thread.start()

    logger.info("🚀 启动小红书自动化工具 FastAPI 服务器...")
    logger.info("📖 API 文档: http://localhost:8000/docs")
    logger.info("🔧 健康检查: http://localhost:8000/")
    logger.info("🔑 许可证激活: http://localhost:8000/activate")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


# 运行服务（默认端口 8000）
if __name__ == "__main__":
    main()