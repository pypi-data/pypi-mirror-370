# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["TaskRetrieveResponse"]


class TaskRetrieveResponse(BaseModel):
    id: str

    output: Optional[Dict[str, object]] = None

    state: Optional[Dict[str, object]] = None

    status: Literal["running", "waiting-dependencies", "suspended", "completed", "failed", "cancelled"]

    workflow_run_id: str = FieldInfo(alias="workflowRunId")
