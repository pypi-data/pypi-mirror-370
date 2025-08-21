import pytest
from unittest.mock import MagicMock, patch
import redis
import uuid
from src.config import config
from datetime import datetime

# 忽略pydantic库级别的ConfigDict警告
pytestmark = pytest.mark.filterwarnings(
    "ignore::pydantic.errors.PydanticDeprecatedSince20"
)


@pytest.fixture
def redis_client():
    """创建一个真实的Redis客户端实例，用于集成测试"""
    # 连接到测试Redis实例
    client = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB,
        password=config.REDIS_PASSWORD,
        decode_responses=True,
    )

    # 清理测试前的所有数据
    client.flushdb()
    yield client

    # 测试结束后清理数据
    client.flushdb()
    client.close()
