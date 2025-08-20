# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["LedgerClaimPaymentParams"]


class LedgerClaimPaymentParams(TypedDict, total=False):
    amount_usd_cents: Required[Annotated[float, PropertyInfo(alias="amountUsdCents")]]
    """Payment amount in cents."""

    claim_id: Required[Annotated[str, PropertyInfo(alias="claimId")]]
    """Identifier of the claim associated with this payment."""

    ik: Required[str]
    """Idempotency key for the payment."""

    insurance_id: Required[Annotated[str, PropertyInfo(alias="insuranceId")]]
    """Identifier of the insurance for the payment."""

    order_id: Required[Annotated[str, PropertyInfo(alias="orderId")]]
    """Order ID associated with the payment."""

    reason: Required[str]
    """Reason for the payment."""

    posted_at: Annotated[Union[str, datetime], PropertyInfo(alias="postedAt", format="iso8601")]
    """Optional ISO 8601 date-time to post the entry."""
