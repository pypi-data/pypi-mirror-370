# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = ["OrderRetrieveBalanceResponse"]


class OrderRetrieveBalanceResponse(BaseModel):
    balance_usd_cents: float = FieldInfo(alias="balanceUsdCents")
    """Balance in cents"""
