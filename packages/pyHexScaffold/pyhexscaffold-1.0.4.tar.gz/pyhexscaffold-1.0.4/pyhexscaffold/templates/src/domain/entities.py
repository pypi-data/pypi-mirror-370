"""领域实体定义

实体是具有唯一标识符的领域对象，即使其属性发生变化，其身份也保持不变。

在此模块中定义您的领域实体。
"""

from enum import Enum
from typing import List, Optional
import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class BaseEntity(BaseModel):
    """所有实体的基类

    包含所有实体共有的属性和方法。
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def update_timestamp(self) -> None:
        """更新实体的更新时间戳"""
        self.updated_at = datetime.now()

    class Config:
        """Pydantic配置"""

        # 允许通过属性访问字段（Pydantic V2）
        from_attributes = True
        # 允许使用默认工厂函数
        validate_assignment = True
