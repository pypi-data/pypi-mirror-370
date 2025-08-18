from typing import Annotated

from litestar import Controller, Request, get, post
from litestar.di import Provide
from litestar.exceptions import ValidationException
from litestar.plugins.pydantic import PydanticDTO
from litestar.response import ServerSentEvent
from sparkden.models.shared import BaseModel, OffsetPagination
from sparkden.models.task import CreateTaskParams, SendMessageParams, Task, TaskItem
from sparkden.services.task import TaskService
from sparkden.shared.utils import dto_config, snake_case_dict


class GetTaskResponse(BaseModel):
    task: Task | None


CreateTaskParamsDTO = PydanticDTO[Annotated[CreateTaskParams, dto_config()]]
SendMessageParamsDTO = PydanticDTO[Annotated[SendMessageParams, dto_config()]]
TaskDTO = PydanticDTO[Annotated[Task, dto_config()]]
GetTaskResponseDTO = PydanticDTO[Annotated[GetTaskResponse, dto_config()]]
ListTasksResponseDTO = PydanticDTO[Annotated[OffsetPagination[TaskItem], dto_config()]]


def get_task_service(request: Request) -> TaskService:
    return TaskService(user_id=str(request.user.id))


class TaskController(Controller):
    path = "/tasks"
    dependencies = {
        "task_service": Provide(get_task_service, sync_to_thread=True),
    }

    @get("/", return_dto=ListTasksResponseDTO)
    async def list_tasks(
        self, task_service: TaskService, limit: int = 30, offset: int = 0
    ) -> OffsetPagination[TaskItem]:
        return await task_service.list_tasks(limit=limit, offset=offset)

    @post("/", dto=CreateTaskParamsDTO, return_dto=TaskDTO)
    async def create_task(
        self, task_service: TaskService, data: CreateTaskParams
    ) -> Task:
        return await task_service.create_task(
            title=data.title, assistant_id=data.assistant_id, task_id=data.task_id
        )

    @get("/{task_id:str}", return_dto=GetTaskResponseDTO)
    async def get_task(
        self, task_service: TaskService, task_id: str, assistant_id: str
    ) -> GetTaskResponse:
        task = await task_service.get_task(assistant_id=assistant_id, task_id=task_id)
        return GetTaskResponse(task=task)

    @post("/{task_id:str}/run", dto=SendMessageParamsDTO)
    async def run_task(
        self, task_service: TaskService, task_id: str, data: SendMessageParams
    ) -> ServerSentEvent:
        message = data.message or data.message_part
        if message is None:
            raise ValidationException(
                status_code=400, detail="param message or message_part is required"
            )

        return ServerSentEvent(
            task_service.run_task(
                assistant_id=data.assistant_id,
                task_id=task_id,
                message=message,
                state_delta=snake_case_dict(data.state_delta)
                if data.state_delta
                else None,
                edit_message_id=data.edit_message_id,
            )
        )
