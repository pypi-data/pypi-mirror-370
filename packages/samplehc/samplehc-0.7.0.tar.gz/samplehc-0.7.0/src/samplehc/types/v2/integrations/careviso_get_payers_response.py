# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["CarevisoGetPayersResponse", "CarevisoGetPayersResponseItem"]


class CarevisoGetPayersResponseItem(BaseModel):
    insurance_id: str = FieldInfo(alias="insuranceId")

    insurance_name: str = FieldInfo(alias="insuranceName")


CarevisoGetPayersResponse: TypeAlias = List[CarevisoGetPayersResponseItem]
