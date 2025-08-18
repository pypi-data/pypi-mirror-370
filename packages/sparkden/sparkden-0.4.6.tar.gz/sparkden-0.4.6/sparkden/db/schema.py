from enum import StrEnum
from uuid import uuid4

from google.adk.sessions.database_session_service import StorageSession
from litestar.plugins.sqlalchemy import base
from sqlalchemy import ForeignKey, ForeignKeyConstraint, Index, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"


class DataSourceType(StrEnum):
    UPLOAD = "upload"
    API = "api"


class DataSourceStatus(StrEnum):
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class VectorDistance(StrEnum):
    COSINE = "Cosine"
    EUCLID = "Euclid"
    DOT = "Dot"
    MANHATTAN = "Manhattan"


class RetrievalMode(StrEnum):
    DENSE = "dense"
    SPARSE = "sparse"
    HYBRID = "hybrid"


class User(base.UUIDAuditBase):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(default=lambda: str(uuid4()), primary_key=True)
    name: Mapped[str]
    username: Mapped[str | None]
    password: Mapped[bytes | None]
    avatar: Mapped[str | None]
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    extra_info: Mapped[dict | None] = mapped_column(JSONB)


class ApiKey(base.UUIDAuditBase):
    __tablename__ = "api_keys"
    key_hash: Mapped[str] = mapped_column(unique=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    revoked: Mapped[bool] = mapped_column(default=False)


class KnowledgeCollection(base.UUIDAuditBase):
    __tablename__ = "knowledge_collections"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    vector_dimensions: Mapped[int] = mapped_column(default=1024)
    vector_distance: Mapped[VectorDistance] = mapped_column(
        default=VectorDistance.COSINE
    )
    retrieval_mode: Mapped[RetrievalMode] = mapped_column(default=RetrievalMode.DENSE)


class KnowledgeDataSource(base.UUIDAuditBase):
    __tablename__ = "knowledge_data_sources"
    __table_args__ = (
        Index("idx_knowledge_data_sources_collection_id", "collection_id"),
        Index(
            "idx_knowledge_data_sources_file_hash", text("(extra_info ->> 'file_hash')")
        ),
    )

    name: Mapped[str]
    definition_id: Mapped[str]
    type: Mapped[DataSourceType]
    status: Mapped[DataSourceStatus]
    extra_info: Mapped[dict | None] = mapped_column(JSONB)
    collection_id: Mapped[str] = mapped_column(ForeignKey("knowledge_collections.id"))


class Task(base.UUIDAuditBase):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("idx_tasks_agent_session_id", "agent_session_id"),
        Index("idx_tasks_user_id_assistant_id", "user_id", "assistant_id"),
        ForeignKeyConstraint(
            ["assistant_id", "user_id", "agent_session_id"],
            [StorageSession.app_name, StorageSession.user_id, StorageSession.id],
            ondelete="CASCADE",
        ),
    )

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    assistant_id: Mapped[str]
    agent_session_id: Mapped[str]
    title: Mapped[str]
    extra_info: Mapped[dict | None] = mapped_column(JSONB)
