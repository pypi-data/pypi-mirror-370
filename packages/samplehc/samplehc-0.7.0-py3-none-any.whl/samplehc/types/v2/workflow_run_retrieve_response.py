# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["WorkflowRunRetrieveResponse"]


class WorkflowRunRetrieveResponse(BaseModel):
    workflow_run: Optional[object] = FieldInfo(alias="workflowRun", default=None)
    """The detailed workflow run object."""
