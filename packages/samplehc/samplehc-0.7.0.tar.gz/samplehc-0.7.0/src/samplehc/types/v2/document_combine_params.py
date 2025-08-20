# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DocumentCombineParams", "Document"]


class DocumentCombineParams(TypedDict, total=False):
    combined_file_name: Required[Annotated[str, PropertyInfo(alias="combinedFileName")]]
    """The desired file name for the combined PDF (e.g., 'combined.pdf')."""

    documents: Required[Iterable[Document]]
    """An array of document resources to be combined. All documents must be PDFs."""


class Document(TypedDict, total=False):
    id: Required[str]

    file_name: Required[Annotated[str, PropertyInfo(alias="fileName")]]
