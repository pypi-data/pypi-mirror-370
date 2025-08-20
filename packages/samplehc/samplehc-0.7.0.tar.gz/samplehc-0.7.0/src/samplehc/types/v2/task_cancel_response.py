# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["TaskCancelResponse"]


class TaskCancelResponse(BaseModel):
    message: str
    """Confirmation message that the task has been cancelled."""
