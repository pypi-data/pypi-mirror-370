# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union
from typing_extensions import Required, Annotated, TypedDict

from ......_utils import PropertyInfo

__all__ = ["ClinicalQuestionUpdateParams", "Responses"]


class ClinicalQuestionUpdateParams(TypedDict, total=False):
    slug: Required[str]

    responses: Required[Dict[str, Responses]]


class Responses(TypedDict, total=False):
    value: Required[Union[str, List[str]]]

    other_value: Annotated[str, PropertyInfo(alias="otherValue")]
