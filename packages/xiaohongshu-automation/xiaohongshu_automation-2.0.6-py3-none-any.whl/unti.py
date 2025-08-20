import os
from datetime import datetime
import requests
import logging

logger = logging.getLogger(__name__)

def get_publish_date(content, index):
    # 获取今天的日期并格式化为年-月-日
    today = datetime.now().strftime('%Y-%m-%d')
    return today


def download_images(urls):
    """
    从URL数组下载图片并保存到指定目录
    Args:
        urls: 图片URL列表
    Returns:
        保存的图片文件路径列表
    Raises:
        Exception: 下载失败时抛出详细错误信息
    """
    # 获取今天的日期作为文件夹名
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 创建保存目录
    save_dir = os.path.abspath(os.path.join('pic', today))
    try:
        os.makedirs(save_dir, exist_ok=True)
    except Exception as e:
        raise Exception(f"创建图片保存目录失败: {save_dir} - {str(e)}")
    
    saved_files = []
    failed_downloads = []
    
    for i, url in enumerate(urls):
        try:
            # 生成文件名
            file_ext = os.path.splitext(url.split('?')[0])[1] or '.jpg'
            filename = f'image_{i+1}{file_ext}'
            filepath = os.path.abspath(os.path.join(save_dir, filename))
            
            logger.info(f'开始下载第{i+1}张图片: {url}')
            
            # 下载图片
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            response.raise_for_status()
            
            # 检查内容类型是否为图片
            content_type = response.headers.get('content-type', '').lower()
            if not any(img_type in content_type for img_type in ['image/', 'jpeg', 'png', 'gif', 'webp']):
                logger.warning(f'第{i+1}张图片的内容类型可能不是图片: {content_type}')
            
            # 检查文件大小
            if len(response.content) == 0:
                raise Exception(f"第{i+1}张图片下载内容为空")
            
            # 保存图片
            with open(filepath, 'wb') as f:
                f.write(response.content)
                
            logger.info(f'成功保存第{i+1}张图片: {filename} (大小: {len(response.content)} 字节)')
            saved_files.append(filepath)
            
        except requests.exceptions.Timeout:
            error_msg = f"第{i+1}张图片下载超时: {url}"
            logger.error(error_msg)
            failed_downloads.append(error_msg)
            
        except requests.exceptions.ConnectionError:
            error_msg = f"第{i+1}张图片连接失败: {url}"
            logger.error(error_msg)
            failed_downloads.append(error_msg)
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"第{i+1}张图片HTTP错误 {e.response.status_code}: {url}"
            logger.error(error_msg)
            failed_downloads.append(error_msg)
            
        except Exception as e:
            error_msg = f"第{i+1}张图片下载失败: {url} - {str(e)}"
            logger.error(error_msg)
            failed_downloads.append(error_msg)
    
    # 如果有下载失败的图片，抛出异常
    if failed_downloads:
        # 不管是全部失败还是部分失败，都直接抛出异常，表示发布失败
        if len(saved_files) == 0:
            # 全部下载失败
            raise Exception(f"图片下载完全失败，发布操作已终止:\n" + "\n".join(failed_downloads))
        else:
            # 部分下载失败 - 也要失败，不允许部分成功的发布
            raise Exception(f"图片下载部分失败，发布操作已终止 (失败: {len(failed_downloads)}/{len(urls)}):\n" + "\n".join(failed_downloads))
    
    logger.info(f'所有{len(saved_files)}张图片下载完成')
    return saved_files
        

def parse_string_to_array(string_array):
    """
    将字符串化的数组还原成Python数组
    Args:
        string_array: 字符串化的数组
    Returns:
        还原后的Python数组
    """
    try:
        # 移除可能存在的空格和换行符
        string_array = string_array.strip()
        
        # 如果是空字符串,返回空数组
        if not string_array:
            return []
            
        # 使用eval安全地将字符串转换为数组
        # 确保输入字符串是一个合法的数组表示
        if string_array.startswith('[') and string_array.endswith(']'):
            array = eval(string_array)
            if isinstance(array, list):
                return array
            else:
                logger.error('输入字符串不是有效的数组格式')
                return []
        else:
            logger.error('输入字符串不是有效的数组格式')
            return []
            
    except Exception as e:
        logger.error(f'解析字符串到数组失败: {str(e)}')
        return []
    
def get_news():
    """
    This example describes how to use the workflow interface to chat.
    """

    import os
    # Our official coze sdk for Python [cozepy](https://github.com/coze-dev/coze-py)
    from cozepy import COZE_CN_BASE_URL

    # Get an access_token through personal access token or oauth.
    coze_api_token = 'pat_rNoHsU1aTkXYZguxsZQGXhO6BVOADSm54cVwllYXRRuwdadhQWaSCNVQWuT1XngQ'
    # The default access is api.coze.com, but if you need to access api.coze.cn,
    # please use base_url to configure the api endpoint to access
    coze_api_base = COZE_CN_BASE_URL

    from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType  # noqa

    # Init the Coze client through the access_token.
    coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

    # Create a workflow instance in Coze, copy the last number from the web link as the workflow's ID.
    workflow_id = '7471272337510498331'

    # Call the coze.workflows.runs.create method to create a workflow run. The create method
    # is a non-streaming chat and will return a WorkflowRunResult class.
    workflow = coze.workflows.runs.create(
        workflow_id=workflow_id,
    )

    print("workflow.data", workflow.data)
    return workflow.data

def get_comments_and_reply(url):
    """
    This example describes how to use the workflow interface to chat.
    """

    import os
    # Our official coze sdk for Python [cozepy](https://github.com/coze-dev/coze-py)
    from cozepy import COZE_CN_BASE_URL

    # Get an access_token through personal access token or oauth.
    coze_api_token = 'pat_UcMjjnnTxsg9rT4ytdZ1CdAtmN81sQGhEK2uP5rQrEKPdlqUIJmWhtAWvshMkNDP'
    # The default access is api.coze.com, but if you need to access api.coze.cn,
    # please use base_url to configure the api endpoint to access
    coze_api_base = COZE_CN_BASE_URL

    from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType  # noqa

    # Init the Coze client through the access_token.
    coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

    # Create a workflow instance in Coze, copy the last number from the web link as the workflow's ID.
    workflow_id = '7472797132777553960'

    # Call the coze.workflows.runs.create method to create a workflow run. The create method
    # is a non-streaming chat and will return a WorkflowRunResult class.
    workflow = coze.workflows.runs.create(
        workflow_id=workflow_id,
        parameters={
            "input": url
        }
    )

    print("workflow.data", workflow.data)
    return workflow.data