# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["InstitutionListOutstandingAccountsResponse", "Account"]


class Account(BaseModel):
    balance_usd_cents: float = FieldInfo(alias="balanceUsdCents")
    """Outstanding balance in cents"""

    institution_id: str = FieldInfo(alias="institutionId")
    """Institution ID"""

    invoice_id: str = FieldInfo(alias="invoiceId")
    """Invoice ID"""


class InstitutionListOutstandingAccountsResponse(BaseModel):
    accounts: List[Account]
    """List of all outstanding institutional accounts"""
