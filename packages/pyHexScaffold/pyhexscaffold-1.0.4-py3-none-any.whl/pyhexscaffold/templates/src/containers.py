"""应用程序依赖注入容器

使用dependency-injector库创建应用程序的依赖注入容器，管理服务和资源的生命周期。
"""

from dependency_injector import containers, providers
import redis
from src.config import config


class Container(containers.DeclarativeContainer):
    """应用程序依赖注入容器"""

    # Redis客户端提供器
    redis_client = providers.Singleton(
        redis.Redis,
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB,
        password=config.REDIS_PASSWORD,
        decode_responses=True,
    )


# 创建全局容器实例
container = Container()
