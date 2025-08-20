# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["GlidianGetSubmissionRequirementsParams"]


class GlidianGetSubmissionRequirementsParams(TypedDict, total=False):
    insurance_id: Required[Annotated[float, PropertyInfo(alias="insuranceId")]]

    service_id: Required[Annotated[float, PropertyInfo(alias="serviceId")]]

    state: str
