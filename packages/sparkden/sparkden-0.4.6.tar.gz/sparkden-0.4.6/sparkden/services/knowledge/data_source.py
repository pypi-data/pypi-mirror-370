from sparkden.db.schema import DataSourceStatus, DataSourceType
from sparkden.db.schema import KnowledgeDataSource as StorageDataSource
from sparkden.models.knowledge import (
    DataChunk,
    KnowledgeCollection,
    KnowledgeDataSource,
    KnowledgeDataSourceCreate,
)
from sparkden.models.shared import OffsetPagination, OrderBy
from sparkden.services.base import BaseService
from sparkden.shared.minio import object_exists
from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from .collection import get_collection
from .data_loaders.file_loader import FileLoader
from .vector_store import (
    FieldCondition,
    Filter,
    MatchValue,
    VectorStore,
)


class KnowledgeDataSourceService(BaseService):
    async def list_data_sources(
        self, collection_id: str, *, limit: int = 30, offset: int = 0
    ) -> OffsetPagination[KnowledgeDataSource]:
        async with self.db_session_maker.begin() as db_session:
            query = (
                select(
                    StorageDataSource,
                    func.count().over().label("total_count"),
                )
                .where(StorageDataSource.collection_id == collection_id)
                .order_by(StorageDataSource.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            result = (await db_session.execute(query)).all()
            data_sources = [KnowledgeDataSource.from_storage(row[0]) for row in result]
            total = result[0][1] if result else 0
            return OffsetPagination(
                items=data_sources,
                total=total,
                limit=limit,
                offset=offset,
            )

    async def get_data_source(self, data_source_id: str) -> KnowledgeDataSource | None:
        async with self.db_session_maker.begin() as db_session:
            data_source = await db_session.get(StorageDataSource, data_source_id)
            if data_source:
                return KnowledgeDataSource.from_storage(data_source)
            return None

    async def get_data_source_by_file_hash(
        self,
        collection_id: str,
        file_hash: str,
    ) -> KnowledgeDataSource | None:
        async with self.db_session_maker.begin() as db_session:
            query = select(StorageDataSource).where(
                StorageDataSource.collection_id == collection_id,
                StorageDataSource.extra_info["file_hash"].astext == file_hash,
            )
            data_source = await db_session.scalar(query)
            if data_source:
                return KnowledgeDataSource.from_storage(data_source)
            return None

    async def list_data_source_chunks(
        self,
        collection_id: str,
        data_source_id: str,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> OffsetPagination[DataChunk]:
        filter = Filter(
            must=[
                FieldCondition(
                    key="data_source_id",
                    match=MatchValue(value=data_source_id),
                ),
            ]
        )

        vector_store = VectorStore(
            collection_name=collection_id,
        )

        chunks = await vector_store.filter_chunks(
            filter,
            limit,
            offset,
            OrderBy(field="sequence_in_data_source", desc=False),
        )

        items = [
            DataChunk(
                id=chunk.id,
                content=chunk.content,
                metadata=chunk.metadata,
            )
            for chunk in chunks
        ]

        return OffsetPagination(
            items=items,
            total=await vector_store.count_chunks(filter),
            limit=limit,
            offset=offset,
        )

    async def add_data_source(
        self, data_source: KnowledgeDataSourceCreate
    ) -> tuple[KnowledgeDataSource, bool]:
        collection = await get_collection(data_source.collection_id)
        if not collection:
            raise ValueError("Collection not found")

        if data_source.type == DataSourceType.UPLOAD:
            return await self.add_file_data_source(data_source, collection)
        else:
            raise NotImplementedError("Not implemented")

    async def add_file_data_source(
        self, data_source: KnowledgeDataSourceCreate, collection: KnowledgeCollection
    ) -> tuple[KnowledgeDataSource, bool]:
        file = data_source.pop_extra_info("file")
        if not file:
            raise ValueError("File not found")

        # prevent duplicate file data source
        if object_exists(data_source.collection_id, f"{file.hash}/original"):
            existing_data_source = await self.get_data_source_by_file_hash(
                data_source.collection_id, file.hash
            )
            if existing_data_source:
                return existing_data_source, False
            else:
                raise ValueError("File not found")

        async with self.db_session_maker.begin() as db_session:
            data_source.set_extra_info("file_hash", file.hash)
            data_source.set_extra_info("file_type", file.content_type)
            new_data_source = await create_data_source(data_source, db_session)

        loader = FileLoader(
            data_source=new_data_source.model_copy(
                update={
                    "extra_info": {
                        **(new_data_source.extra_info or {}),
                        "file": file,
                    }
                }
            ),
            collection=collection,
        )
        await loader.load()

        return new_data_source, True

    async def delete_data_source(self, data_source_id: str) -> None:
        async with self.db_session_maker.begin() as db_session:
            data_source = await db_session.scalar(
                delete(StorageDataSource)
                .where(
                    StorageDataSource.id == data_source_id,
                )
                .returning(StorageDataSource)
            )
        if not data_source:
            return

        if data_source.type == DataSourceType.UPLOAD:
            loader = FileLoader(
                data_source=KnowledgeDataSource.from_storage(data_source),
            )
            await loader.unload()
        else:
            raise NotImplementedError("Not implemented")

    async def refresh_data_source(self, data_source_id: str) -> None:
        data_source = await self.get_data_source(data_source_id)
        if not data_source:
            raise ValueError("Data source not found")

        collection = await get_collection(data_source.collection_id)
        if not collection:
            raise ValueError("Collection not found")

        if data_source.type == DataSourceType.UPLOAD:
            loader = FileLoader(
                data_source=data_source,
                collection=collection,
            )
            await loader.reload()
        else:
            raise NotImplementedError("Not implemented")


async def create_data_source(
    data_source: KnowledgeDataSourceCreate, db_session: AsyncSession
) -> KnowledgeDataSource:
    data_source_attributes = {
        **data_source.model_dump(exclude_none=True),
        "status": DataSourceStatus.READY,
    }
    data_source_id = await db_session.scalar(
        insert(StorageDataSource)
        .values(data_source_attributes)
        .on_conflict_do_update(
            index_elements=[StorageDataSource.id],
            set_=data_source_attributes,
        )
        .returning(StorageDataSource.id)
    )
    if not data_source_id:
        raise Exception("Failed to create data_source")
    return KnowledgeDataSource(id=str(data_source_id), **data_source_attributes)
