# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ClearinghouseCoordinationOfBenefitsParams"]


class ClearinghouseCoordinationOfBenefitsParams(TypedDict, total=False):
    dependent_date_of_birth: Required[Annotated[str, PropertyInfo(alias="dependentDateOfBirth")]]

    dependent_first_name: Required[Annotated[str, PropertyInfo(alias="dependentFirstName")]]

    dependent_last_name: Required[Annotated[str, PropertyInfo(alias="dependentLastName")]]

    encounter_date_of_service: Required[Annotated[str, PropertyInfo(alias="encounterDateOfService")]]

    encounter_service_type_code: Required[Annotated[str, PropertyInfo(alias="encounterServiceTypeCode")]]

    provider_name: Required[Annotated[str, PropertyInfo(alias="providerName")]]

    provider_npi: Required[Annotated[str, PropertyInfo(alias="providerNpi")]]

    subscriber_date_of_birth: Required[Annotated[str, PropertyInfo(alias="subscriberDateOfBirth")]]

    subscriber_first_name: Required[Annotated[str, PropertyInfo(alias="subscriberFirstName")]]

    subscriber_last_name: Required[Annotated[str, PropertyInfo(alias="subscriberLastName")]]

    subscriber_member_id: Required[Annotated[str, PropertyInfo(alias="subscriberMemberId")]]

    trading_partner_service_id: Required[Annotated[str, PropertyInfo(alias="tradingPartnerServiceId")]]
