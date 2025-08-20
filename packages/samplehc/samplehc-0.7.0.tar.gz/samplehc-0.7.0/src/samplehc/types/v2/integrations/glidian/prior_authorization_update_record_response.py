# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["PriorAuthorizationUpdateRecordResponse"]


class PriorAuthorizationUpdateRecordResponse(BaseModel):
    status: Literal["updated"]

    record: Optional[object] = None
