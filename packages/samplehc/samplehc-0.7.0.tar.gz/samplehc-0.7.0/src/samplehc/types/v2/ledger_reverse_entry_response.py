# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["LedgerReverseEntryResponse"]


class LedgerReverseEntryResponse(BaseModel):
    reversing_entry_id: str = FieldInfo(alias="reversingEntryId")
    """ID of the reversing ledger entry created."""
