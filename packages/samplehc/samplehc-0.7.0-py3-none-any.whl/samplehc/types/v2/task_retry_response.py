# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["TaskRetryResponse"]


class TaskRetryResponse(BaseModel):
    message: str
    """Confirmation message that the task retry has been initiated."""
