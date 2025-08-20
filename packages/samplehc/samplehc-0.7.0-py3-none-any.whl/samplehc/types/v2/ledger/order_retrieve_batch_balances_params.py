# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["OrderRetrieveBatchBalancesParams"]


class OrderRetrieveBatchBalancesParams(TypedDict, total=False):
    order_ids: Required[Annotated[List[str], PropertyInfo(alias="orderIds")]]
    """Array of order IDs to retrieve balances for (max 100)"""
