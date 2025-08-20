# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["AsyncResultRetrieveResponse"]


class AsyncResultRetrieveResponse(BaseModel):
    status: str
    """The current status of the asynchronous operation."""

    inputs: Optional[object] = None
    """The inputs provided to the asynchronous operation."""

    result: Optional[object] = None
    """The result of the operation, if completed."""
