# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from ...._models import BaseModel

__all__ = ["GlidianListServicesResponse", "GlidianListServicesResponseItem"]


class GlidianListServicesResponseItem(BaseModel):
    id: float

    name: str

    type: str


GlidianListServicesResponse: TypeAlias = List[GlidianListServicesResponseItem]
