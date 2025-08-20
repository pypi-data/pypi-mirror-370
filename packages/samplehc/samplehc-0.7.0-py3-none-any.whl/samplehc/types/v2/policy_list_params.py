# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["PolicyListParams"]


class PolicyListParams(TypedDict, total=False):
    active_at: Annotated[str, PropertyInfo(alias="activeAt")]
    """Filter policies active at this date (YYYY-MM-DD)"""

    company_id: Annotated[str, PropertyInfo(alias="companyId")]
    """ID of the company to which the policy belongs"""

    hcpcs_codes: Annotated[str, PropertyInfo(alias="hcpcsCodes")]
    """Comma-separated HCPCS codes to filter by"""

    icd10_cm_codes: Annotated[str, PropertyInfo(alias="icd10CmCodes")]
    """Comma-separated ICD-10-CM codes to filter by"""

    limit: float
    """Maximum number of results to return"""

    plan_id: Annotated[str, PropertyInfo(alias="planId")]
    """ID of the plan to which the policy belongs"""

    policy_topic: Annotated[str, PropertyInfo(alias="policyTopic")]
    """Keywords describing the policy content"""

    policy_topic_for_keyword_extraction: Annotated[str, PropertyInfo(alias="policyTopicForKeywordExtraction")]
    """String for keyword extraction (beta)"""

    policy_type: Annotated[str, PropertyInfo(alias="policyType")]
    """Type of policy (MEDICAL_POLICY, PAYMENT_POLICY, etc.)"""

    skip: float
    """Number of results to skip"""

    updated_at_max: Annotated[str, PropertyInfo(alias="updatedAtMax")]
    """Filter policies updated on or before this date (YYYY-MM-DD)"""

    updated_at_min: Annotated[str, PropertyInfo(alias="updatedAtMin")]
    """Filter policies updated on or after this date (YYYY-MM-DD)"""
