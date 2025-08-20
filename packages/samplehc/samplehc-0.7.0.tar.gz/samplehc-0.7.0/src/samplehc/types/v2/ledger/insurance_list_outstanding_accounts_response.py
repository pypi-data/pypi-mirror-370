# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["InsuranceListOutstandingAccountsResponse", "Account"]


class Account(BaseModel):
    balance_usd_cents: float = FieldInfo(alias="balanceUsdCents")
    """Outstanding balance in cents"""

    claim_id: str = FieldInfo(alias="claimId")
    """Claim ID"""

    insurance_id: str = FieldInfo(alias="insuranceId")
    """Insurance ID"""


class InsuranceListOutstandingAccountsResponse(BaseModel):
    accounts: List[Account]
    """List of all outstanding insurance accounts"""
