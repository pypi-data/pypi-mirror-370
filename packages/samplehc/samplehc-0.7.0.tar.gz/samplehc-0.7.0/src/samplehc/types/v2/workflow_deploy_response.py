# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["WorkflowDeployResponse"]


class WorkflowDeployResponse(BaseModel):
    async_result_id: str = FieldInfo(alias="asyncResultId")
    """The ID of the async result tracking the deployment progress."""
