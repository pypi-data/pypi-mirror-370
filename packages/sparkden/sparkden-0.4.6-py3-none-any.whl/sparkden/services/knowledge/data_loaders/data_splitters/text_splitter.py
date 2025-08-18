from uuid import uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sparkden.models.knowledge import DataChunk

from .base import BaseDataSplitter


class TextSplitter(BaseDataSplitter):
    def split(self, data: str) -> list[DataChunk]:
        recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )

        chunks = recursive_splitter.create_documents([data])

        return [
            DataChunk(
                id=str(uuid4().hex),
                content=chunk.page_content,
                metadata=chunk.metadata,
            )
            for chunk in chunks
        ]
