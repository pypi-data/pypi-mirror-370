# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["TaskCompleteResponse"]


class TaskCompleteResponse(BaseModel):
    next_task_id: Optional[str] = FieldInfo(alias="nextTaskId", default=None)
    """The ID of the next task in the workflow, if any, or null."""
