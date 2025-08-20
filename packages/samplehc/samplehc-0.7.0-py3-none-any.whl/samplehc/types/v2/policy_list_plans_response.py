# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel

__all__ = ["PolicyListPlansResponse", "Plan"]


class Plan(BaseModel):
    id: str
    """Unique identifier for the plan"""

    company_id: str
    """ID of the company that owns this plan"""

    name: str
    """Plan name"""

    state: str
    """State where the plan is available"""


class PolicyListPlansResponse(BaseModel):
    count: float
    """Total number of plans available"""

    plans: List[Plan]
