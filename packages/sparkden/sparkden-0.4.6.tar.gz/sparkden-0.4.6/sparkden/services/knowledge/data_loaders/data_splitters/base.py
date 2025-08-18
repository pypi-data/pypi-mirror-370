from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sparkden.models.knowledge import DataChunk


class BaseDataSplitter(ABC):
    @abstractmethod
    def split(self, data: Any) -> list["DataChunk"]:
        pass
