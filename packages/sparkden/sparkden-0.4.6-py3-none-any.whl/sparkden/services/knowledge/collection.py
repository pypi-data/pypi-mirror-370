from sparkden.db.schema import KnowledgeCollection as StorageCollection
from sparkden.models.knowledge import (
    KnowledgeCollection,
    RetrievalMode,
    ScoredDataChunk,
)
from sparkden.services.base import BaseService
from sparkden.shared.minio import get_minio_client
from sparkden.shared.pg import get_session_maker
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from .embeddings import Embeddings
from .vector_store import (
    Distance,
    Field,
    Filter,
    VectorParams,
    VectorStore,
)

default_vector_params = VectorParams(size=1024, distance=Distance.COSINE)


class KnowledgeCollectionService(BaseService):
    async def list_collections(self) -> list[KnowledgeCollection]:
        async with self.db_session_maker.begin() as db_session:
            query = select(StorageCollection).order_by(
                StorageCollection.created_at.desc()
            )
            collections = await db_session.scalars(query)
            return [
                KnowledgeCollection.from_storage(collection)
                for collection in collections
            ]

    async def create_collection(
        self,
        collection_id: str,
        collection_name: str | None = None,
        vector_params: VectorParams = default_vector_params,
    ) -> None:
        await create_collection(collection_id, collection_name, vector_params)

    async def get_collection(self, collection_id: str) -> KnowledgeCollection | None:
        return await get_collection(collection_id)

    async def search_collection(
        self,
        collection_id: str,
        query: str,
        filter: Filter | None = None,
        k: int = 5,
        retrieval_mode: RetrievalMode = RetrievalMode.DENSE,
        score_threshold: float | None = None,
    ) -> list[ScoredDataChunk]:
        collection = await get_collection(collection_id)
        if not collection:
            raise ValueError(f"Collection not found: {collection_id}")

        vector_store = VectorStore(
            collection_name=collection_id, retrieval_mode=retrieval_mode
        )

        embeddings = Embeddings(dimensions=collection.vector_dimensions)
        return await vector_store.search(query, embeddings, filter, k, score_threshold)


async def get_collection(collection_id: str) -> KnowledgeCollection | None:
    async with get_session_maker().begin() as db_session:
        collection = await db_session.get(StorageCollection, collection_id)
        return KnowledgeCollection.from_storage(collection) if collection else None


async def create_collection(
    collection_id: str,
    collection_name: str | None = None,
    vector_params: VectorParams = default_vector_params,
) -> None:
    try:
        minio_client = get_minio_client()
        if not minio_client.bucket_exists(collection_id):
            minio_client.make_bucket(collection_id)
            print(f"Created MinIO bucket: {collection_id}")
    except Exception as e:
        print(f"Unexpected error initializing MinIO bucket: {e}")
        raise

    try:
        created = await VectorStore.create_collection(
            collection_id, vector_params=vector_params
        )
        if created:
            print(f"Vector store collection created: {collection_id}")

            await VectorStore.create_index(
                collection_id,
                Field(name="sequence_in_data_source", type="integer"),
            )
    except Exception as e:
        print(f"Unexpected error initializing vector store collection: {e}")
        raise

    async with get_session_maker().begin() as db_session:
        collection = await db_session.scalar(
            insert(StorageCollection)
            .values(
                id=collection_id,
                name=collection_name or collection_id,
                vector_dimensions=vector_params.size,
                vector_distance=vector_params.distance,
            )
            .on_conflict_do_nothing(
                index_elements=[StorageCollection.id],
            )
            .returning(StorageCollection)
        )

        if collection:
            print(f"Database collection created: {collection.id}")
