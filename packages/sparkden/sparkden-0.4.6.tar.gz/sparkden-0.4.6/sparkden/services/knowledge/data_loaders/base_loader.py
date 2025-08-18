from abc import ABC, abstractmethod

from sparkden.models.knowledge import (
    DataSourceType,
    FetchDataType,
    KnowledgeCollection,
    KnowledgeDataSource,
)

from .data_fetchers import BaseDataFetcher, FileDataFetcher
from .data_splitters import BaseDataSplitter, MarkdownSplitter, TextSplitter


class BaseLoader(ABC):
    def __init__(
        self,
        data_source: KnowledgeDataSource,
        collection: KnowledgeCollection | None = None,
    ):
        from sparkden.assistants import assistants

        self.data_source = data_source
        self.collection = collection

        data_source_definition = assistants.get_data_source(
            self.data_source.definition_id
        )
        if not data_source_definition:
            raise ValueError("Data source definition not found")

        self.data_source_definition = data_source_definition

    def get_data_fetcher(self, data_source_type: DataSourceType) -> BaseDataFetcher:
        if self.data_source_definition.data_fetcher:
            return self.data_source_definition.data_fetcher
        if data_source_type == DataSourceType.UPLOAD:
            return FileDataFetcher()
        if data_source_type == DataSourceType.API:
            raise NotImplementedError("API data fetcher not implemented")

    def get_data_splitter(self, data_type: FetchDataType) -> BaseDataSplitter:
        if self.data_source_definition.data_splitter:
            return self.data_source_definition.data_splitter
        if data_type == FetchDataType.TEXT:
            return TextSplitter()
        if data_type == FetchDataType.MARKDOWN:
            return MarkdownSplitter()
        if data_type == FetchDataType.TABLE:
            raise NotImplementedError("Table data splitter not implemented")

    @abstractmethod
    async def load(self) -> None:
        pass

    @abstractmethod
    async def reload(self) -> None:
        pass

    @abstractmethod
    async def unload(self) -> None:
        pass
