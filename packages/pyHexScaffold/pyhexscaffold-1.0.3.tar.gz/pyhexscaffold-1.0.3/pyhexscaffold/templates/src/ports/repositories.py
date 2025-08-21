from abc import abstractmethod
from typing import Generic, List, TypeVar

T = TypeVar("T")


class Repository(Generic[T]):
    """
    CURD仓储接口
    """

    @abstractmethod
    def all(self) -> List[T]:
        pass

    @abstractmethod
    def add(self, entity: T):
        pass

    @abstractmethod
    def update(self, entity: T):
        pass

    @abstractmethod
    def delete(self, id: str):
        pass

    @abstractmethod
    def find_by_id(self, id: str) -> T:
        pass
