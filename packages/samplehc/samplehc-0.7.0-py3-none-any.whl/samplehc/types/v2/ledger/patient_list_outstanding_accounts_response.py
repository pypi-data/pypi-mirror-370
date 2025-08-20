# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["PatientListOutstandingAccountsResponse", "Account"]


class Account(BaseModel):
    balance_usd_cents: float = FieldInfo(alias="balanceUsdCents")
    """Outstanding balance in cents"""

    patient_id: str = FieldInfo(alias="patientId")
    """Patient ID"""


class PatientListOutstandingAccountsResponse(BaseModel):
    accounts: List[Account]
    """List of all outstanding patient accounts"""
