# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DocumentCreateFromSplitsParams", "Document"]


class DocumentCreateFromSplitsParams(TypedDict, total=False):
    document: Required[Document]
    """The source document from which to create new documents based on splits."""

    splits: Required[Iterable[float]]
    """Array of page numbers indicating where to split the document.

    Each number is the start of a new document segment.
    """


class Document(TypedDict, total=False):
    id: Required[str]

    file_name: Required[Annotated[str, PropertyInfo(alias="fileName")]]
