from enum import StrEnum
from typing import Callable, NotRequired, Sequence, TypedDict

from google.adk.agents import BaseAgent
from google.adk.plugins.base_plugin import BasePlugin
from litestar import Controller
from litestar.handlers import ASGIRouteHandler
from pydantic import ConfigDict

from sparkden.models.knowledge import DataSourceType
from sparkden.models.shared import BaseModel, ExtraInfoMixin, base_model_config
from sparkden.services.knowledge.data_loaders.data_fetchers.base import (
    BaseDataFetcher,
)
from sparkden.services.knowledge.data_loaders.data_splitters.base import (
    BaseDataSplitter,
)


class ToolResponseStatus(StrEnum):
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"


class ToolResponse[ResultT](TypedDict):
    """The base tool response."""

    result: NotRequired[ResultT]
    """The result of the tool."""

    status: NotRequired[ToolResponseStatus]
    """The status of the tool response."""

    error: NotRequired[str]
    """The error message of the tool response."""


class UserApprovalResult[ItemT](BaseModel):
    """The user approval result."""

    approved: bool
    """Whether the user approved the request."""

    feedback: str
    """The feedback for the user approval."""

    modified_item: ItemT | None = None
    """A modified item provided on approval as result, or on rejection as a suggestion."""


class ProgressItemStatus(StrEnum):
    COMPLETED = "completed"
    RUNNING = "running"
    PENDING = "pending"


class KnowledgeDataSourceDefinition(ExtraInfoMixin, BaseModel):
    model_config = ConfigDict(
        **base_model_config,
        arbitrary_types_allowed=True,
    )
    id: str
    type: DataSourceType
    data_fetcher: BaseDataFetcher | None = None
    data_splitter: BaseDataSplitter | None = None


AssistantApiRoute = type[Controller] | ASGIRouteHandler


class Assistant(BaseModel):
    model_config = ConfigDict(
        **base_model_config,
        arbitrary_types_allowed=True,
    )

    id: str
    disabled: bool = False
    root_agent: BaseAgent
    api_routes: Sequence[AssistantApiRoute] | None = None
    agent_plugins: list[BasePlugin] = []
    callbacks: dict[str, Callable] | None = None
    data_sources: list[KnowledgeDataSourceDefinition] | None = None
    sequence: int = 9999
