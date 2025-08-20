# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["LedgerPostRemittanceAcceptedParams"]


class LedgerPostRemittanceAcceptedParams(TypedDict, total=False):
    adjustment_usd_cents: Required[Annotated[float, PropertyInfo(alias="adjustmentUsdCents")]]
    """Adjustment amount in cents (positive or negative)."""

    claim_id: Required[Annotated[str, PropertyInfo(alias="claimId")]]
    """Identifier of the claim associated with this remittance."""

    ik: Required[str]
    """Idempotency key for the remittance."""

    insurance_id: Required[Annotated[str, PropertyInfo(alias="insuranceId")]]
    """Identifier of the insurance for the remittance."""

    order_id: Required[Annotated[str, PropertyInfo(alias="orderId")]]
    """Order ID associated with the remittance."""

    patient_id: Required[Annotated[str, PropertyInfo(alias="patientId")]]
    """Identifier of the patient for the remittance."""

    patient_responsibility_usd_cents: Required[Annotated[float, PropertyInfo(alias="patientResponsibilityUsdCents")]]
    """Patient responsibility amount in cents."""

    posted_at: Annotated[Union[str, datetime], PropertyInfo(alias="postedAt", format="iso8601")]
    """Optional ISO 8601 date-time to post the entry."""
