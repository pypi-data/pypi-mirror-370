# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["LedgerReverseEntryParams"]


class LedgerReverseEntryParams(TypedDict, total=False):
    ik: Required[str]
    """Idempotency key for the reversal."""
