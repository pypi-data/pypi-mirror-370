from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sparkden.models.knowledge import FetchDataResult, KnowledgeDataSource


class BaseDataFetcher(ABC):
    @abstractmethod
    def fetch(self, data_source: "KnowledgeDataSource") -> "FetchDataResult":
        pass
