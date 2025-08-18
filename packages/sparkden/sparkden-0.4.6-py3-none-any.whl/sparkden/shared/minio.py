import os

from minio import Minio, S3Error

from .utils import getenv

_minio_client: Minio | None = None


def get_minio_client() -> Minio:
    global _minio_client
    if _minio_client is None:
        _minio_client = Minio(
            endpoint=getenv("MINIO_ENDPOINT"),
            access_key=getenv("MINIO_ROOT_USER"),
            secret_key=getenv("MINIO_ROOT_PASSWORD"),
            secure=getenv("MINIO_SECURE", "false").lower() == "true",
            region=os.getenv("MINIO_REGION"),
        )
    return _minio_client


def object_exists(bucket_name: str, object_name: str) -> bool:
    try:
        minio_client = get_minio_client()
        minio_client.stat_object(bucket_name, object_name)
        return True
    except S3Error as e:
        if e.code == "NoSuchKey":
            return False
        raise e
