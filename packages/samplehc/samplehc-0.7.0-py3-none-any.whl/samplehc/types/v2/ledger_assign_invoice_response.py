# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["LedgerAssignInvoiceResponse"]


class LedgerAssignInvoiceResponse(BaseModel):
    ledger_entry_id: str = FieldInfo(alias="ledgerEntryId")
    """Created ledger entry ID"""
