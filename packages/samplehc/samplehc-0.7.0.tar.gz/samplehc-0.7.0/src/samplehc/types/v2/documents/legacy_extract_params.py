# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ...._utils import PropertyInfo

__all__ = [
    "LegacyExtractParams",
    "AnswerSchema",
    "AnswerSchemaUnionMember0",
    "AnswerSchemaUnionMember1",
    "AnswerSchemaUnionMember2",
    "AnswerSchemaUnionMember3",
    "AnswerSchemaUnionMember4",
    "AnswerSchemaUnionMember4Event",
    "AnswerSchemaUnionMember4EventFields",
    "Document",
]


class LegacyExtractParams(TypedDict, total=False):
    answer_schemas: Required[Annotated[Iterable[AnswerSchema], PropertyInfo(alias="answerSchemas")]]
    """An array of answer schemas defining data to extract."""

    documents: Required[Iterable[Document]]
    """An array of documents to process."""


class AnswerSchemaUnionMember0(TypedDict, total=False):
    label: Required[str]

    question: Required[str]

    type: Required[Literal["boolean"]]

    description: str

    extract_multiple: Annotated[bool, PropertyInfo(alias="extractMultiple")]

    keywords: List[str]


class AnswerSchemaUnionMember1(TypedDict, total=False):
    label: Required[str]

    question: Required[str]

    type: Required[Literal["string"]]

    description: str

    extract_multiple: Annotated[bool, PropertyInfo(alias="extractMultiple")]

    keywords: List[str]


class AnswerSchemaUnionMember2(TypedDict, total=False):
    label: Required[str]

    question: Required[str]

    type: Required[Literal["enum"]]

    values: Required[List[str]]

    description: str

    extract_multiple: Annotated[bool, PropertyInfo(alias="extractMultiple")]

    keywords: List[str]


class AnswerSchemaUnionMember3(TypedDict, total=False):
    label: Required[str]

    properties: Required[Dict[str, object]]

    question: Required[str]

    type: Required[Literal["object"]]

    description: str

    extract_multiple: Annotated[bool, PropertyInfo(alias="extractMultiple")]

    keywords: List[str]


class AnswerSchemaUnionMember4EventFields(TypedDict, total=False):
    description: Required[str]

    field_type: Required[Literal["string", "boolean", "number"]]

    optional: bool


class AnswerSchemaUnionMember4Event(TypedDict, total=False):
    event_type: Required[str]

    fields: Required[Dict[str, AnswerSchemaUnionMember4EventFields]]

    type: Required[Literal["event"]]

    description: str

    keywords: List[str]


class AnswerSchemaUnionMember4(TypedDict, total=False):
    events: Required[Iterable[AnswerSchemaUnionMember4Event]]

    extract_multiple: Required[Annotated[Literal[True], PropertyInfo(alias="extractMultiple")]]

    label: Required[str]

    type: Required[Literal["event_log"]]


AnswerSchema: TypeAlias = Union[
    AnswerSchemaUnionMember0,
    AnswerSchemaUnionMember1,
    AnswerSchemaUnionMember2,
    AnswerSchemaUnionMember3,
    AnswerSchemaUnionMember4,
]


class Document(TypedDict, total=False):
    id: Required[str]

    file_name: Required[Annotated[str, PropertyInfo(alias="fileName")]]
