"""配置管理模块

负责从环境变量中读取配置并提供给应用程序使用。
"""

import os
from dotenv import load_dotenv
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

# 加载.env文件
# 获取当前文件的绝对路径
current_file = os.path.abspath(__file__)
# 获取当前文件所在的目录 (src/config)
config_dir = os.path.dirname(current_file)
# 获取项目根目录 (从 src/config 向上两层到达项目根目录)
project_root = os.path.dirname(os.path.dirname(config_dir))
# 构建 .env 文件的完整路径
dotenv_path = os.path.join(project_root, ".env")
# 加载 .env 文件
load_dotenv(dotenv_path=dotenv_path)


class Config(BaseSettings):
    """配置类，从环境变量中读取配置"""

    # 配置环境变量前缀，可选
    model_config = {"env_file": dotenv_path, "env_file_encoding": "utf-8"}

    # 应用程序配置 - 默认值与.env文件同步
    # NOTE: 此处配置项必须与 .env 一至，.env的配置只可以少不可以多,否则会引发错误
    APP_NAME: str = Field(default="data-svc", alias="APP_NAME")
    APP_ENV: str = Field(default="development", alias="APP_ENV")
    APP_DEBUG: bool = Field(default=True, alias="APP_DEBUG")
    APP_HOST: str = Field(default="0.0.0.0", alias="APP_HOST")
    APP_PORT: int = Field(default=10003, alias="APP_PORT")
    APP_VERSION: str = Field(default="1.0.5", alias="APP_VERSION")
    # gRPC服务配置
    GRPC_PORT: int = Field(default=50051, alias="GRPC_PORT")

    # Redis配置 - 默认值与.env文件同步
    REDIS_HOST: str = Field(default="localhost", alias="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, alias="REDIS_PORT")
    REDIS_DB: int = Field(default=3, alias="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")

    # 其他配置
    CORS_ORIGINS: str = Field(default="*", alias="CORS_ORIGINS")

    @property
    def redis_url(self) -> str:
        """生成Redis连接URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


# 创建全局配置实例
config = Config()
