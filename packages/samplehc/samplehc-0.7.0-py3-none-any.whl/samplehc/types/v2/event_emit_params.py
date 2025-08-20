# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["EventEmitParams"]


class EventEmitParams(TypedDict, total=False):
    name: Required[str]
    """The name of the event to create."""

    payload: object
    """The payload data for the event."""

    idempotency_key: Annotated[str, PropertyInfo(alias="idempotency-key")]
