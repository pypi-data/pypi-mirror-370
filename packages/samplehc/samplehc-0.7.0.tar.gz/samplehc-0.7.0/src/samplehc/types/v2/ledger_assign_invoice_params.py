# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["LedgerAssignInvoiceParams"]


class LedgerAssignInvoiceParams(TypedDict, total=False):
    amount_usd_cents: Required[Annotated[float, PropertyInfo(alias="amountUsdCents")]]
    """Assignment amount in cents (positive or negative)."""

    ik: Required[str]
    """Idempotency key for the assignment."""

    institution_id: Required[Annotated[str, PropertyInfo(alias="institutionId")]]
    """Identifier of the institution for the assignment."""

    invoice_id: Required[Annotated[str, PropertyInfo(alias="invoiceId")]]
    """Invoice ID being assigned."""

    order_id: Required[Annotated[str, PropertyInfo(alias="orderId")]]
    """Order ID associated with the assignment."""

    reason: Required[str]
    """Reason for the assignment."""

    posted_at: Annotated[Union[str, datetime], PropertyInfo(alias="postedAt", format="iso8601")]
    """Optional ISO 8601 date-time to post the entry."""
