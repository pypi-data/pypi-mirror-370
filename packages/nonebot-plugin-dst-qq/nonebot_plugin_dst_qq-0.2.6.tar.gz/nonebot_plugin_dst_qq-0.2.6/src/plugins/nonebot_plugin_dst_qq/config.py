from pydantic import BaseModel
import httpx


class Config(BaseModel):
    """Plugin Config Here"""
    
    # DMP API配置
    dmp_base_url: str
    dmp_token: str
    default_cluster: str
    
    async def get_first_cluster(self) -> str:
        """获取第一个可用的集群名称"""
        try:
            headers = {
                "Authorization": self.dmp_token,
                "X-I18n-Lang": "zh"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.dmp_base_url}/setting/clusters", headers=headers)
                response.raise_for_status()
                data = response.json()
                
                if data.get("code") == 200:
                    clusters = data.get("data", [])
                    if clusters:
                        # 返回第一个集群的名称
                        return clusters[0].get("clusterName", self.default_cluster)
                
                return self.default_cluster
        except Exception:
            # 如果获取失败，返回默认集群
            return self.default_cluster


def get_config() -> Config:
    """获取插件配置"""
    from nonebot import get_driver
    driver = get_driver()
    return driver.config


# 配置实例将通过 get_plugin_config(Config) 获取
