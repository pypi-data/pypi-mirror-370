# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["LedgerInstitutionPaymentResponse"]


class LedgerInstitutionPaymentResponse(BaseModel):
    ledger_entry_id: str = FieldInfo(alias="ledgerEntryId")
    """The unique identifier of the successfully created ledger entry."""
