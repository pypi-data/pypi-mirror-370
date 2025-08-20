# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DocumentClassifyParams", "Document", "LabelSchema"]


class DocumentClassifyParams(TypedDict, total=False):
    document: Required[Document]
    """The document to be classified."""

    label_schemas: Required[Annotated[Iterable[LabelSchema], PropertyInfo(alias="labelSchemas")]]
    """An array of label schemas to classify against."""


class Document(TypedDict, total=False):
    id: Required[str]

    file_name: Required[Annotated[str, PropertyInfo(alias="fileName")]]


class LabelSchema(TypedDict, total=False):
    label: Required[str]

    description: str

    keywords: List[str]
