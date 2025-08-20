# nonebot-plugin-dst-qq 配置说明

本文档详细说明 `nonebot-plugin-dst-qq` 插件的配置方法和选项。

## 📋 配置概述

`nonebot-plugin-dst-qq` 插件需要以下配置项才能正常工作：

- **DMP 服务器配置**：连接饥荒管理平台
- **NoneBot2 基础配置**：机器人运行环境
- **权限配置**：管理员权限设置

## 🔧 配置方法

### 方法一：环境变量配置（推荐）

在项目根目录创建 `.env` 文件：

```env
# DMP 服务器配置
DMP_BASE_URL=http://your-dmp-server:port/v1
DMP_TOKEN=your-jwt-token
DEFAULT_CLUSTER=cx

# OneBot 配置
ONEBOT_WS_URLS=["ws://your-onebot-server:port"]
ONEBOT_ACCESS_TOKEN=your-access-token

# 超级用户配置
SUPERUSERS=["你的QQ号"]

# 调试模式（可选）
DEBUG=true
```

### 方法二：Python 配置文件

在项目根目录创建 `.env.py` 文件：

```python
# DMP 服务器配置
DMP_BASE_URL = "http://your-dmp-server:port/v1"
DMP_TOKEN = "your-jwt-token"
DEFAULT_CLUSTER = "cx"

# OneBot 配置
ONEBOT_WS_URLS = ["ws://your-onebot-server:port"]
ONEBOT_ACCESS_TOKEN = "your-access-token"

# 超级用户配置
SUPERUSERS = ["你的QQ号"]

# 调试模式（可选）
DEBUG = True
```

### 方法三：NoneBot2 配置文件

在 `bot.py` 或 `config.py` 中配置：

```python
from nonebot import get_driver

driver = get_driver()

# DMP 服务器配置
driver.config.dmp_base_url = "http://your-dmp-server:port/v1"
driver.config.dmp_token = "your-jwt-token"
driver.config.default_cluster = "cx"

# OneBot 配置
driver.config.onebot_ws_urls = ["ws://your-onebot-server:port"]
driver.config.onebot_access_token = "your-access-token"

# 超级用户配置
driver.config.superusers = ["你的QQ号"]
```

## 📝 配置项详解

### DMP 服务器配置

| 配置项 | 类型 | 必需 | 说明 | 示例 |
|--------|------|------|------|------|
| `DMP_BASE_URL` | string | ✅ | DMP 服务器 API 地址 | `http://192.168.1.100:8080/v1` |
| `DMP_TOKEN` | string | ✅ | JWT 认证令牌 | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `DEFAULT_CLUSTER` | string | ✅ | 默认集群名称 | `cx` |

**获取方法：**
1. 访问 DMP Web 界面
2. 使用用户名密码登录
3. 在开发者工具中查看网络请求，获取 JWT Token
4. 记录集群名称

### OneBot 配置

| 配置项 | 类型 | 必需 | 说明 | 示例 |
|--------|------|------|------|------|
| `ONEBOT_WS_URLS` | list | ✅ | OneBot 服务器 WebSocket 地址列表 | `["ws://127.0.0.1:6700"]` |
| `ONEBOT_ACCESS_TOKEN` | string | ✅ | 访问令牌 | `your-access-token` |

**获取方法：**
1. 在 NapCatQQ 中开启 WebSocket 服务器
2. 设置监听地址和端口
3. 生成访问令牌

### 权限配置

| 配置项 | 类型 | 必需 | 说明 | 示例 |
|--------|------|------|------|------|
| `SUPERUSERS` | list | ✅ | 超级用户 QQ 号列表 | `["123456789", "987654321"]` |

**说明：**
- 只有超级用户才能执行管理员命令
- 支持多个 QQ 号，用逗号分隔
- QQ 号必须是数字字符串

### 可选配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `DEBUG` | boolean | `false` | 启用调试模式，输出详细日志 |

## 🗂️ 数据存储配置

插件使用 `nonebot-plugin-localstore` 自动管理数据存储：

- **自动创建**：插件首次运行时会自动创建数据目录
- **路径管理**：数据存储在插件专用的目录中
- **无需配置**：用户无需手动配置存储路径

**数据目录结构：**
```
{插件数据根目录}/nonebot_plugin_dst_qq/
├── chat_history.db          # 聊天历史数据库
└── logs/                    # 日志文件目录
```

## ✅ 配置验证

### 1. 检查配置完整性

启动机器人后，检查控制台输出：

```
🚀 DMP 饥荒管理平台机器人插件启动中...
✅ 配置加载成功: DMP服务器 http://your-dmp-server:port/v1
✅ 消息同步服务启动成功
```

### 2. 测试基础功能

执行以下命令测试配置：

```bash
# 测试世界信息查询
世界

# 测试系统信息查询
系统
```

### 3. 测试管理员功能

```bash
# 测试备份查看（需要超级用户权限）
查看备份
```

## 🚨 常见配置错误

### 1. DMP 连接失败

**错误信息：** `DMP API 连接失败`
**可能原因：**
- `DMP_BASE_URL` 地址错误
- `DMP_TOKEN` 无效或过期
- DMP 服务器未启动
- 网络连接问题

**解决方案：**
- 检查 DMP 服务器状态
- 重新获取 JWT Token
- 验证网络连通性

### 2. OneBot 连接失败

**错误信息：** `WebSocket 连接失败`
**可能原因：**
- `ONEBOT_WS_URLS` 地址错误
- `ONEBOT_ACCESS_TOKEN` 不匹配
- NapCatQQ 未启动 WebSocket 服务

**解决方案：**
- 检查 NapCatQQ 配置
- 重新生成访问令牌
- 确认 WebSocket 服务已启动

### 3. 权限不足

**错误信息：** `权限不足`
**可能原因：**
- QQ 号不在 `SUPERUSERS` 列表中
- DMP 用户权限不足

**解决方案：**
- 检查 `SUPERUSERS` 配置
- 确认 DMP 用户权限

## 🔄 配置更新

### 修改配置后重启

配置修改后需要重启机器人才能生效：

```bash
# 停止机器人
Ctrl+C

# 重新启动
nb run
```

### 热重载配置

某些配置支持热重载，无需重启：

- 插件配置：支持热重载
- 环境变量：需要重启
- 权限配置：需要重启

## 📚 相关文档

- [NoneBot2 配置文档](https://nonebot.dev/docs/guides/configuration)
- [DMP 官方文档](https://miraclesses.top/)
- [NapCatQQ 配置文档](https://napneko.github.io/)

## 🆘 获取帮助

如果遇到配置问题，请：

1. 检查本文档的常见错误部分
2. 查看机器人启动日志
3. 在 [GitHub Issues](https://github.com/uitok/nonebot-plugin-dst-qq/issues) 中反馈问题
4. 提供详细的错误信息和配置内容


