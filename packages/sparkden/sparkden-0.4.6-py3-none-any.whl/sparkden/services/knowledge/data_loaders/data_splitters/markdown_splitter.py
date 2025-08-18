from uuid import uuid4

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from sparkden.models.knowledge import DataChunk

from .base import BaseDataSplitter


class MarkdownSplitter(BaseDataSplitter):
    def split(self, data: str) -> list[DataChunk]:
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header1"),
                ("##", "Header2"),
                ("###", "Header3"),
                ("####", "Header4"),
                ("#####", "Header5"),
                ("######", "Header6"),
            ],
        )
        chunks = markdown_splitter.split_text(data)
        recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        chunks = recursive_splitter.split_documents(chunks)
        return [
            DataChunk(
                id=str(uuid4().hex),
                content=chunk.page_content,
                metadata=chunk.metadata,
            )
            for chunk in chunks
        ]
