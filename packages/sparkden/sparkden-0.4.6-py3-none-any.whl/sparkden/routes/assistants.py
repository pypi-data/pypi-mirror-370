from typing import Annotated, Any

from litestar import Controller, get
from litestar.plugins.pydantic import PydanticDTO
from sparkden.models.shared import BaseModel
from sparkden.shared.utils import dto_config


class PartialAssistant(BaseModel):
    id: str
    disabled: bool
    data_sources: list[dict[str, Any]]


class ListAssistantsResponse(BaseModel):
    assistants: list[PartialAssistant]


ListAssistantsResponseDTO = PydanticDTO[
    Annotated[
        ListAssistantsResponse,
        dto_config(),
    ]
]


class AssistantController(Controller):
    path = "/assistants"

    @get("/", return_dto=ListAssistantsResponseDTO, sync_to_thread=True)
    def list_assistants(self) -> ListAssistantsResponse:
        from sparkden.assistants import assistants

        return ListAssistantsResponse(
            assistants=[
                PartialAssistant(
                    id=assistant.id,
                    disabled=assistant.disabled,
                    data_sources=[
                        data_source.model_dump(
                            exclude={"data_fetcher", "data_splitter"},
                            exclude_none=True,
                            by_alias=True,
                        )
                        for data_source in assistant.data_sources or []
                    ],
                )
                for assistant in assistants.get_assistants(include_disabled=True)
            ]
        )
