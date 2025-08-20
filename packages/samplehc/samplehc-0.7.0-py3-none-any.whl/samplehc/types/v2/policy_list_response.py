# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["PolicyListResponse", "Policy", "PolicyPlan"]


class PolicyPlan(BaseModel):
    name: str
    """Plan name"""

    state: str
    """State where the plan is available"""


class Policy(BaseModel):
    id: str
    """Unique identifier for the policy"""

    date_effective: str
    """Effective date of the policy"""

    date_expiration: Optional[str] = None
    """Expiration date of the policy"""

    file_url: str
    """URL to the policy document"""

    hcpcs_codes: List[str]
    """Associated HCPCS codes"""

    icd10_cm_codes: List[str]
    """Associated ICD-10-CM codes"""

    is_active: bool
    """Whether the policy is currently active"""

    name: str
    """Policy name"""

    parent_policy_id: str
    """Parent policy identifier"""

    plan: PolicyPlan

    plan_policy_id: str
    """Plan-specific policy identifier"""

    rank: Optional[float] = None
    """Policy ranking"""

    type: str
    """Type of policy (MEDICAL_POLICY, PAYMENT_POLICY, etc.)"""

    updated_at: str
    """Last updated date"""


class PolicyListResponse(BaseModel):
    count: float
    """Total number of policies available"""

    policies: List[Policy]
