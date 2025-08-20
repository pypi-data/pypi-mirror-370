# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["PolicyListCompaniesParams"]


class PolicyListCompaniesParams(TypedDict, total=False):
    company_name: str
    """Company name to filter by"""

    limit: float
    """Maximum number of results to return"""

    skip: float
    """Number of results to skip"""
