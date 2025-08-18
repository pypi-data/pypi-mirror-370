from typing import cast

import pymupdf
from sparkden.models.knowledge import (
    FetchDataResult,
    FetchDataType,
    FileObject,
    KnowledgeDataSource,
)
from sparkden.shared.minio import S3Error, get_minio_client
from sparkden.shared.pymupdf_rag import to_markdown

from .base import BaseDataFetcher


class FileDataFetcher(BaseDataFetcher):
    def fetch(self, data_source: KnowledgeDataSource) -> FetchDataResult:
        file = cast(FileObject, data_source.get_extra_info("file"))
        if not file:
            file = self.fetch_object(data_source)
        if not file:
            raise ValueError("File not found")
        if file.content_type == "text/plain":
            return self._parse_text_file(file)
        elif file.content_type == "application/pdf":
            return self._parse_pdf_file(file, data_source.collection_id)
        else:
            raise ValueError(f"Unsupported file type: {file.content_type}")

    def fetch_object(
        self, data_source: KnowledgeDataSource, object_name: str = "original"
    ) -> FileObject | None:
        file_hash = data_source.get_extra_info("file_hash")
        if not file_hash:
            return None

        object_name = f"{file_hash}/{object_name}"
        response = None
        try:
            minio_client = get_minio_client()
            response = minio_client.get_object(data_source.collection_id, object_name)
            fallback_content_type = response.headers["content-type"]
            content_type = data_source.get_extra_info(
                "file_type", fallback_content_type
            )
            file = FileObject(
                name=object_name,
                content=response.data,
                content_type=content_type,
            )
        except S3Error as e:
            if e.code == "NoSuchKey":
                return None
            raise e
        finally:
            if response:
                response.close()
                response.release_conn()

        return file

    def fetch_parsed_file(self, data_source: KnowledgeDataSource) -> FileObject | None:
        return self.fetch_object(data_source, object_name="parsed")

    @staticmethod
    def _parse_text_file(file: FileObject) -> FetchDataResult:
        return FetchDataResult(
            data=file.content.decode("utf-8"),
            data_type=FetchDataType.TEXT,
            extracted_files=[
                FileObject(
                    name=f"{file.hash}/original",
                    content=file.content,
                    content_type=file.content_type,
                )
            ],
        )

    @staticmethod
    def _parse_pdf_file(file: FileObject, collection_id: str) -> FetchDataResult:
        doc = pymupdf.open(stream=file.content, filetype="pdf")
        extracted_images: list[FileObject] = []

        def extract_image(image_data: bytes, image_name: str) -> str:
            extracted_images.append(
                FileObject(
                    name=image_name,
                    content=image_data,
                    content_type="image/png",
                )
            )
            return f"/images/{collection_id}/{image_name}"

        markdown = to_markdown(
            doc,
            filename=file.hash,
            write_images=extract_image is not None,
            on_write_image=extract_image,
            image_format="png",
        )

        return FetchDataResult(
            data=markdown,
            data_type=FetchDataType.MARKDOWN,
            extracted_files=[
                FileObject(
                    name=f"{file.hash}/original",
                    content=file.content,
                    content_type=file.content_type,
                ),
                FileObject(
                    name=f"{file.hash}/parsed",
                    content=markdown.encode("utf-8"),
                    content_type="text/markdown",
                ),
                *extracted_images,
            ],
        )
