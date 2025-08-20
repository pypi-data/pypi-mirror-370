# 小红书自动化工具 - 许可证使用指南

## 📋 概述

本工具采用离线许可证验证系统，提供7天免费试用期，之后需要使用激活码进行激活。许可证文件安全存储在系统目录中，不会因软件更新而丢失。

## 🔧 许可证管理

### 查看许可证状态

#### 1. 命令行查看

```bash
# 查看基本状态
python license_cli.py --status

# 查看详细信息
python license_cli.py --info

# JSON格式输出
python license_cli.py --status --json
```

#### 2. 网页查看

访问 `http://localhost:8000/activate` 可以在网页上查看许可证状态并进行激活。

#### 3. API查看

```bash
curl http://localhost:8000/license/status
```

### 激活许可证

#### 1. 网页激活（推荐）

1. 启动软件：`python main.py`
2. 打开浏览器访问：`http://localhost:8000/activate`
3. 在激活页面输入激活码
4. 点击"激活许可证"按钮

#### 2. 命令行激活

```bash
python license_cli.py --activate YOUR_ACTIVATION_CODE
```

#### 3. API激活

```bash
curl -X POST http://localhost:8000/license/activate \
  -H "Content-Type: application/json" \
  -d '{"activation_code": "YOUR_ACTIVATION_CODE"}'
```

## 🎫 激活码类型

- **WEEK**: 延长7天
- **MONTH**: 延长30天  
- **QUARTER**: 延长90天（季度）
- **YEAR**: 延长365天

### 激活码格式

正式激活码格式：
```
MONTH-UNIVERSAL-1749061547-a63d68d0f99d1a327045
  ↑       ↑         ↑              ↑
类型   通用标识    时间戳         20位签名
```

支持两种类型：
- **通用激活码**：可在任何机器上使用（UNIVERSAL）
- **机器专用激活码**：只能在指定机器上使用（机器ID）

## 🔄 许可证文件位置

### 系统存储位置（v2.0）

- **Windows**: `%APPDATA%\XiaohongshuTools\license.json`
- **macOS**: `~/Library/Application Support/XiaohongshuTools/license.json`  
- **Linux**: `~/.config/XiaohongshuTools/license.json`

### 自动迁移

软件会自动检测并迁移旧版本的许可证文件：
1. 检测项目目录下的 `license.json`
2. 自动迁移到系统目录
3. 备份旧文件为 `license.backup`

## ⚙️ 备份和恢复

### 备份许可证

```bash
# 自动生成备份文件名
python license_cli.py --backup

# 指定备份文件名
python license_cli.py --backup my_license_backup.json
```

### 恢复许可证

```bash
python license_cli.py --restore my_license_backup.json
```

## 🔍 故障排除

### 常见问题

#### Q: 激活码无效
A: 请检查：
1. 激活码格式是否正确
2. 是否已经使用过该激活码  
3. 机器专用激活码是否与当前机器匹配

#### Q: 软件更新后许可证丢失
A: v2.0版本许可证存储在系统目录中，不会因更新丢失。如果遇到问题，软件会自动迁移许可证文件。

#### Q: 网页激活页面无法访问
A: 请确保：
1. 软件已启动（`python main.py`）
2. 端口8000未被占用
3. 防火墙允许访问

#### Q: 许可证过期怎么办？
A: 请联系软件提供商获取新的激活码。

## 📊 许可证信息查看

### 详细信息字段

- **有效期**: 许可证过期时间
- **剩余时间**: 距离过期的天数和小时数
- **许可证类型**: trial（试用）或 activated（已激活）
- **机器ID**: 当前设备的唯一标识
- **存储位置**: 许可证文件的完整路径
- **创建时间**: 许可证首次创建时间
- **最后激活**: 最近一次激活时间
- **已使用激活码数量**: 累计使用的激活码数量

### JSON输出示例

```json
{
  "license_info": {
    "valid": true,
    "expiry_date": "2025-09-17 02:00:17",
    "license_type": "activated", 
    "remaining_days": 103,
    "remaining_hours": 23,
    "message": "许可证有效，剩余 103 天",
    "storage_location": "C:\\Users\\...\\XiaohongshuTools\\license.json",
    "license_version": "2.0"
  },
  "warning": null,
  "machine_id": "cf7e15843b7ad608"
}
```

## 🚀 启动流程

### 首次运行
1. 创建7天试用期许可证
2. 显示许可证状态和机器ID
3. 提供激活方式说明

### 日常使用
1. 自动检查许可证有效性
2. 显示剩余时间
3. 过期前7天和3天时自动提醒

### 许可证过期
1. 软件进入受限模式
2. 仅许可证相关功能可用
3. 其他API需要重新激活后访问

## 📞 技术支持

如需获取激活码或遇到技术问题，请联系软件提供商并提供以下信息：

- **机器ID**: 通过 `python license_cli.py --status` 获取
- **错误信息**: 具体的错误提示
- **操作系统**: Windows/macOS/Linux版本
- **软件版本**: 2.0.0

---

**注意**: 激活码仅限授权用户使用，请勿泄露给他人。 