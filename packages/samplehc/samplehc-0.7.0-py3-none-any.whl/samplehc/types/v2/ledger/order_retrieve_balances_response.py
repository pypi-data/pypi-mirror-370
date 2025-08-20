# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["OrderRetrieveBalancesResponse", "Balances"]


class Balances(BaseModel):
    institution_invoiced: float = FieldInfo(alias="institutionInvoiced")
    """Institution invoiced balance in cents"""

    institution_uninvoiced: float = FieldInfo(alias="institutionUninvoiced")
    """Institution uninvoiced balance in cents"""

    order_writeoff: float = FieldInfo(alias="orderWriteoff")
    """Order writeoff balance in cents"""

    patient_responsibility: float = FieldInfo(alias="patientResponsibility")
    """Patient responsibility balance in cents"""

    unallocated: float
    """Unallocated balance in cents"""


class OrderRetrieveBalancesResponse(BaseModel):
    balances: Balances

    order_id: str = FieldInfo(alias="orderId")
    """Order ID"""
