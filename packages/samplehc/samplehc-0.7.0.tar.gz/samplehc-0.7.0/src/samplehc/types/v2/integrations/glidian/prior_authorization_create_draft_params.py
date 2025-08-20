# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["PriorAuthorizationCreateDraftParams", "Attachment"]


class PriorAuthorizationCreateDraftParams(TypedDict, total=False):
    attachments: Required[Iterable[Attachment]]

    glidian_payer_id: Required[Annotated[float, PropertyInfo(alias="glidianPayerId")]]

    glidian_service_id: Required[Annotated[str, PropertyInfo(alias="glidianServiceId")]]

    reference_number: Required[Annotated[str, PropertyInfo(alias="referenceNumber")]]

    submission_requirements: Required[Annotated[Dict[str, str], PropertyInfo(alias="submissionRequirements")]]

    reference_number_two: Annotated[str, PropertyInfo(alias="referenceNumberTwo")]

    state: str


class Attachment(TypedDict, total=False):
    id: Required[str]

    file_name: Required[Annotated[str, PropertyInfo(alias="fileName")]]
