# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["InstitutionRetrieveOutstandingOrdersResponse", "Order"]


class Order(BaseModel):
    balance_usd_cents: float = FieldInfo(alias="balanceUsdCents")
    """Outstanding balance in cents"""

    institution_id: str = FieldInfo(alias="institutionId")
    """Institution ID"""

    order_id: str = FieldInfo(alias="orderId")
    """Order ID"""


class InstitutionRetrieveOutstandingOrdersResponse(BaseModel):
    orders: List[Order]
    """List of outstanding institutional orders"""
