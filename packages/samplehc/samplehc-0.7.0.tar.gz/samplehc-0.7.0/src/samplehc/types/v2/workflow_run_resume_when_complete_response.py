# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["WorkflowRunResumeWhenCompleteResponse"]


class WorkflowRunResumeWhenCompleteResponse(BaseModel):
    message: str
    """A message indicating the request has been accepted for processing."""
