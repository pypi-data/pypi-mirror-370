# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DocumentSearchParams", "Document"]


class DocumentSearchParams(TypedDict, total=False):
    documents: Required[Iterable[Document]]
    """An array of document resources to search within."""

    query: Required[str]
    """The search query string."""


class Document(TypedDict, total=False):
    id: Required[str]

    file_name: Required[Annotated[str, PropertyInfo(alias="fileName")]]
