
from abc import ABC, abstractmethod
from typing import Any, Optional

class AbstractLocalCache(ABC):

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        raise NotImplementedError