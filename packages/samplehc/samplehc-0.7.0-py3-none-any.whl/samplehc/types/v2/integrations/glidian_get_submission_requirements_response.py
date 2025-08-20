# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["GlidianGetSubmissionRequirementsResponse", "UnionMember0", "UnionMember0Requirements", "UnionMember1"]


class UnionMember0Requirements(BaseModel):
    available_fields: List[str] = FieldInfo(alias="availableFields")

    required_fields: List[str] = FieldInfo(alias="requiredFields")


class UnionMember0(BaseModel):
    requirements: UnionMember0Requirements

    status: Literal["success"]


class UnionMember1(BaseModel):
    available_states: List[str] = FieldInfo(alias="availableStates")

    status: Literal["invalid-state"]


GlidianGetSubmissionRequirementsResponse: TypeAlias = Union[UnionMember0, UnionMember1]
