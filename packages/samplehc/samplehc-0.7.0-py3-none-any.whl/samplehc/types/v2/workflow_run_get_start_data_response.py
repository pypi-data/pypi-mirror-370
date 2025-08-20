# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["WorkflowRunGetStartDataResponse"]


class WorkflowRunGetStartDataResponse(BaseModel):
    start_data: Optional[object] = FieldInfo(alias="startData", default=None)
    """The initial data payload provided when this workflow run was started."""
