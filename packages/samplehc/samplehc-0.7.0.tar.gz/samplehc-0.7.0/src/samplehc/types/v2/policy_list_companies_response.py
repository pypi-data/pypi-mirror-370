# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel

__all__ = ["PolicyListCompaniesResponse", "Company"]


class Company(BaseModel):
    id: str
    """Unique identifier for the company"""

    name: str
    """Company name"""


class PolicyListCompaniesResponse(BaseModel):
    companies: List[Company]

    count: float
    """Total number of companies available"""
