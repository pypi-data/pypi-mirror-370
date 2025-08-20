# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["PolicyListPlansParams"]


class PolicyListPlansParams(TypedDict, total=False):
    limit: float
    """Maximum number of results to return"""

    plan_name: str
    """Plan name to filter by"""

    skip: float
    """Number of results to skip"""
