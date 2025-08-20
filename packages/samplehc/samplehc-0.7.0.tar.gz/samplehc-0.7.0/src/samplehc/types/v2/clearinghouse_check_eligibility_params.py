# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ClearinghouseCheckEligibilityParams"]


class ClearinghouseCheckEligibilityParams(TypedDict, total=False):
    provider_identifier: Required[Annotated[str, PropertyInfo(alias="providerIdentifier")]]
    """The provider identifier. This is usually your NPI."""

    provider_name: Required[Annotated[str, PropertyInfo(alias="providerName")]]
    """The provider name."""

    service_type_codes: Required[Annotated[List[str], PropertyInfo(alias="serviceTypeCodes")]]
    """The service type codes."""

    subscriber_date_of_birth: Required[Annotated[str, PropertyInfo(alias="subscriberDateOfBirth")]]
    """The date of birth of the subscriber."""

    subscriber_first_name: Required[Annotated[str, PropertyInfo(alias="subscriberFirstName")]]
    """The first name of the subscriber."""

    subscriber_last_name: Required[Annotated[str, PropertyInfo(alias="subscriberLastName")]]
    """The last name of the subscriber."""

    subscriber_member_id: Required[Annotated[str, PropertyInfo(alias="subscriberMemberId")]]
    """The member ID of the subscriber."""

    trading_partner_service_id: Required[Annotated[str, PropertyInfo(alias="tradingPartnerServiceId")]]
    """The trading partner service ID"""
