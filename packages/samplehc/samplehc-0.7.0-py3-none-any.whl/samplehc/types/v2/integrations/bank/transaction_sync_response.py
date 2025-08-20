# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = ["TransactionSyncResponse"]


class TransactionSyncResponse(BaseModel):
    has_more: bool = FieldInfo(alias="hasMore")
    """Whether there are more transactions to fetch."""

    modified: List[object]
    """Array of modified transactions."""

    next_cursor: Optional[str] = FieldInfo(alias="nextCursor", default=None)
    """Cursor for the next page of transactions."""

    removed: List[object]
    """Array of removed transactions."""

    transactions: List[object]
    """Array of added transactions."""
