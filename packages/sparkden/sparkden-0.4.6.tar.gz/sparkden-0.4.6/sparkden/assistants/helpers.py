from pydantic import BaseModel, ValidationError

from .models import (
    ToolResponse,
    ToolResponseStatus,
)


def validate_tool_param(
    tool_name: str, param_value: dict, param_type: type[BaseModel]
) -> ToolResponse | None:
    try:
        param_type.model_validate(param_value)
    except ValidationError as e:
        error_str = f"""Invoking `{tool_name}()` failed as the input parameters validation failed:
{str(e)}
You could retry calling this tool, but it is IMPORTANT for you to follow the input parameters schema."""
        return ToolResponse(
            status=ToolResponseStatus.ERROR,
            error=error_str,
        )
    return None
