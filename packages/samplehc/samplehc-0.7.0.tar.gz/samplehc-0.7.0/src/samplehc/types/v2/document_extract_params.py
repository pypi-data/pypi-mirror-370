# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DocumentExtractParams", "Document"]


class DocumentExtractParams(TypedDict, total=False):
    documents: Required[Iterable[Document]]
    """An array of documents to extract data from."""

    prompt: Required[str]
    """A prompt guiding the extraction process."""

    response_json_schema: Required[Annotated[Dict[str, object], PropertyInfo(alias="responseJsonSchema")]]
    """A JSON schema defining the structure of the desired extraction output."""

    model: Literal["reasoning-3-mini", "reasoning-3"]
    """The model to use for extraction."""

    reasoning_effort: Annotated[Literal["low", "medium", "high"], PropertyInfo(alias="reasoningEffort")]
    """Optional control over the reasoning effort for extraction."""


class Document(TypedDict, total=False):
    id: Required[str]

    file_name: Required[Annotated[str, PropertyInfo(alias="fileName")]]
