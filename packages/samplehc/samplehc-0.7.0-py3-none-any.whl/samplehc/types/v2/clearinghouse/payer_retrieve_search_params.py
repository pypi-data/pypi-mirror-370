# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["PayerRetrieveSearchParams"]


class PayerRetrieveSearchParams(TypedDict, total=False):
    query: Required[str]
    """The search query (e.g. name, ID, etc.) for the payer."""
