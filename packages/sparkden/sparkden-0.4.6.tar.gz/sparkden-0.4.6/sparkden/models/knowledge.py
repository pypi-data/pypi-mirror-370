import hashlib
from enum import StrEnum
from functools import cached_property
from typing import Any, Callable

from sparkden.db.schema import (
    DataSourceStatus,
    DataSourceType,
    RetrievalMode,
    VectorDistance,
)
from sparkden.db.schema import KnowledgeCollection as StorageCollection
from sparkden.db.schema import KnowledgeDataSource as StorageDataSource
from sparkden.models.shared import BaseModel, ExtraInfoMixin


class FileObject(BaseModel):
    name: str
    content: bytes
    content_type: str

    @cached_property
    def hash(self) -> str:
        return hashlib.sha256(self.content).hexdigest()


class DataChunk(BaseModel):
    id: str
    content: str
    metadata: dict[str, Any]


class ScoredDataChunk(DataChunk):
    score: float
    retrieval_mode: RetrievalMode


class KnowledgeCollection(BaseModel):
    id: str
    name: str
    vector_dimensions: int
    vector_distance: VectorDistance
    retrieval_mode: RetrievalMode

    @classmethod
    def from_storage(cls, collection: StorageCollection) -> "KnowledgeCollection":
        return cls(
            id=str(collection.id),
            name=collection.name,
            vector_dimensions=collection.vector_dimensions,
            vector_distance=collection.vector_distance,
            retrieval_mode=collection.retrieval_mode,
        )


class KnowledgeDataSourceBase(ExtraInfoMixin, BaseModel):
    definition_id: str
    name: str
    type: DataSourceType
    collection_id: str


class KnowledgeDataSource(KnowledgeDataSourceBase):
    id: str
    status: DataSourceStatus

    @classmethod
    def from_storage(cls, data_source: StorageDataSource) -> "KnowledgeDataSource":
        return cls(
            id=str(data_source.id),
            definition_id=data_source.definition_id,
            name=data_source.name,
            type=data_source.type,
            status=data_source.status,
            extra_info=data_source.extra_info,
            collection_id=data_source.collection_id,
        )


class KnowledgeDataSourceCreate(KnowledgeDataSourceBase):
    id: str | None = None


LoadAndSplitData = Callable[
    [KnowledgeDataSource],
    tuple[list[DataChunk], list[FileObject]],
]


class FetchDataType(StrEnum):
    TEXT = "text"
    MARKDOWN = "markdown"
    TABLE = "table"


class FetchDataResult(ExtraInfoMixin, BaseModel):
    data: Any
    data_type: FetchDataType
    extracted_files: list[FileObject] = []
