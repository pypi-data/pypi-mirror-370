from io import BytesIO

from qdrant_client.http.models import (
    FieldCondition,
    Filter,
    MatchValue,
)
from sparkden.models.knowledge import (
    DataChunk,
    FileObject,
)
from sparkden.shared.minio import get_minio_client

from ..embeddings import Embeddings
from ..vector_store import VectorStore
from .base_loader import BaseLoader


class FileLoader(BaseLoader):
    async def load(self, reload: bool = False) -> None:
        data_fetcher = self.get_data_fetcher(self.data_source.type)
        fetch_result = data_fetcher.fetch(self.data_source)

        data_splitter = self.get_data_splitter(fetch_result.data_type)
        chunks = data_splitter.split(fetch_result.data)

        for index, chunk in enumerate(chunks):
            chunk.metadata.update(
                {
                    "sequence_in_data_source": index + 1,
                    "data_source_id": self.data_source.id,
                }
            )

        if reload:
            await self.unload()
        self._save_objects(fetch_result.extracted_files)
        await self._add_to_vector_store(chunks)

    async def unload(self) -> None:
        file_hash = self.data_source.get_extra_info("file_hash")
        if file_hash:
            minio_client = get_minio_client()
            objects_to_delete = minio_client.list_objects(
                self.data_source.collection_id, prefix=file_hash, recursive=True
            )

            self._delete_objects(
                [
                    object.object_name
                    for object in objects_to_delete
                    if object.object_name
                ]
            )

        await self._delete_from_vector_store()

    async def reload(self) -> None:
        await self.load(reload=True)

    def _save_objects(self, objects: list[FileObject]) -> None:
        minio_client = get_minio_client()
        for object in objects:
            minio_client.put_object(
                bucket_name=self.data_source.collection_id,
                object_name=object.name,
                data=BytesIO(object.content),
                length=len(object.content),
                content_type=object.content_type,
            )

    def _delete_objects(self, object_names: list[str]) -> None:
        minio_client = get_minio_client()
        for object_name in object_names:
            minio_client.remove_object(
                bucket_name=self.data_source.collection_id,
                object_name=object_name,
            )

    async def _add_to_vector_store(self, chunks: list[DataChunk]) -> None:
        if not self.collection:
            raise ValueError("Collection is required to get vector dimensions")

        embeddings = Embeddings(dimensions=self.collection.vector_dimensions)
        vector_store = VectorStore(
            collection_name=self.collection.id,
            retrieval_mode=self.collection.retrieval_mode,
        )

        await vector_store.add_chunks(chunks, embeddings=embeddings)

    async def _delete_from_vector_store(self) -> None:
        vector_store = VectorStore(
            collection_name=self.data_source.collection_id,
        )

        filter = Filter(
            must=[
                FieldCondition(
                    key="data_source_id",
                    match=MatchValue(value=self.data_source.id),
                ),
            ]
        )

        await vector_store.delete_chunks(filter)
