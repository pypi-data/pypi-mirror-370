from pathlib import Path

import nonebot
from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="DMP 饥荒管理平台机器人",
    description="基于 NoneBot2 的饥荒管理平台 (DMP) QQ 机器人插件，支持游戏信息查询、命令执行和消息互通功能。",
    usage="""基础命令：
- /世界 <集群> 或 /world <集群> - 获取世界信息
- /房间 <集群> 或 /room <集群> - 获取房间信息  
- /系统 或 /sys - 获取系统信息
- /玩家 <集群> 或 /players <集群> - 获取在线玩家列表
- /直连 <集群> 或 /connection <集群> - 获取服务器直连信息
- /菜单 或 /help - 显示帮助信息

管理员命令：
- /管理命令 - 显示管理员功能菜单
- /查看备份 - 获取备份文件列表（自动选择集群）
- /执行命令 <命令> 或 /exec <命令> - 执行游戏命令
- /回滚世界 <天数> 或 /rollback <天数> - 回滚世界（1-5天）
- /重置世界 <集群> <世界> 或 /reset <集群> <世界> - 重置世界
- /聊天历史 <集群> <世界> <行数> 或 /chathistory <集群> <世界> <行数> - 获取聊天历史
- /聊天统计 <集群> 或 /chatstats <集群> - 获取聊天统计信息

消息互通功能：
- /消息互通 或 /exchange - 开启游戏内消息与QQ消息互通
- /关闭互通 或 /close_exchange - 关闭消息互通功能
- /互通状态 或 /exchange_status - 查看当前互通状态
- /最新消息 - 获取游戏内最新消息（自动选择集群和世界）

配置说明：
在 NoneBot2 配置文件中配置以下项：
- dmp_base_url: DMP服务器地址
- dmp_token: JWT认证令牌
- default_cluster: 默认集群名称

数据存储：
插件使用 localstore 插件自动管理数据存储目录，无需手动配置。

Alconna 特性：
- 支持参数类型检查
- 支持可选参数和必需参数
- 支持中英文命令别名
- 智能参数解析和验证""",
    
    type="application",
    homepage="https://github.com/uitok/nonebot-plugin-dst-qq",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

# 延迟配置获取，避免在导入时初始化 NoneBot
config = None

def get_config():
    """获取插件配置"""
    global config
    if config is None:
        config = get_plugin_config(Config)
    return config

# 导入子插件模块，确保Alconna命令被正确注册
try:
    # 导入子插件模块
    from .plugins import dmp_api, dmp_advanced, message_exchange
    print("✅ 所有子插件模块加载成功")
except Exception as e:
    print(f"⚠️ 子插件加载失败: {e}")

# 插件启动时的初始化
@nonebot.get_driver().on_startup
async def startup():
    """插件启动时初始化"""
    print("🚀 DMP 饥荒管理平台机器人插件启动中...")
    try:
        # 初始化配置
        config = get_config()
        print(f"✅ 配置加载成功: DMP服务器 {config.dmp_base_url}")
        
        # 启动消息同步（如果启用）
        try:
            from .plugins.message_exchange import message_manager
            await message_manager.start_sync()
            print("✅ 消息同步服务启动成功")
        except Exception as e:
            print(f"⚠️ 消息同步服务启动失败: {e}")
            
    except Exception as e:
        print(f"❌ 插件初始化失败: {e}")

# 插件关闭时的清理
@nonebot.get_driver().on_shutdown
async def shutdown():
    """插件关闭时清理"""
    print("🔄 DMP 饥荒管理平台机器人插件正在关闭...")
    try:
        # 停止消息同步
        try:
            from .plugins.message_exchange import message_manager
            await message_manager.stop_sync()
            print("✅ 消息同步服务停止成功")
        except Exception as e:
            print(f"⚠️ 停止消息同步服务失败: {e}")
            
    except Exception as e:
        print(f"❌ 插件关闭清理失败: {e}")
    
    print("👋 DMP 饥荒管理平台机器人插件已关闭")

