# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["PriorAuthorizationUpdateRecordParams"]


class PriorAuthorizationUpdateRecordParams(TypedDict, total=False):
    slug: Required[str]

    reference_number: Annotated[str, PropertyInfo(alias="referenceNumber")]

    reference_number_two: Annotated[str, PropertyInfo(alias="referenceNumberTwo")]

    submission_requirements: Annotated[Dict[str, str], PropertyInfo(alias="submissionRequirements")]
