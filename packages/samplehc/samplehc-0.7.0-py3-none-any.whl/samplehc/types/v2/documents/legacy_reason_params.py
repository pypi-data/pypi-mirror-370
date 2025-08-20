# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ...._utils import PropertyInfo

__all__ = [
    "LegacyReasonParams",
    "Document",
    "Task",
    "TaskUnionMember0",
    "TaskUnionMember1",
    "TaskUnionMember1ResponseSchema",
    "TaskUnionMember1ResponseSchemaType",
    "TaskUnionMember2",
    "TaskUnionMember2ResponseSchema",
]


class LegacyReasonParams(TypedDict, total=False):
    documents: Required[Iterable[Document]]
    """An array of documents to apply reasoning to."""

    task: Required[Task]
    """The task schema defining the reasoning process."""


class Document(TypedDict, total=False):
    id: Required[str]

    file_name: Required[Annotated[str, PropertyInfo(alias="fileName")]]


class TaskUnionMember0(TypedDict, total=False):
    id: Required[str]

    description: Required[str]

    label: Required[str]

    type: Required[Literal["reasoning"]]


class TaskUnionMember1ResponseSchemaType(TypedDict, total=False):
    type: Required[Literal["text"]]


TaskUnionMember1ResponseSchema: TypeAlias = Union[
    TaskUnionMember1ResponseSchemaType, TaskUnionMember1ResponseSchemaType
]


class TaskUnionMember1(TypedDict, total=False):
    id: Required[str]

    description: Required[str]

    label: Required[str]

    response_schema: Required[TaskUnionMember1ResponseSchema]

    type: Required[Literal["extraction"]]


class TaskUnionMember2ResponseSchema(TypedDict, total=False):
    type: Required[Literal["text"]]


class TaskUnionMember2(TypedDict, total=False):
    id: Required[str]

    description: Required[str]

    label: Required[str]

    response_schema: Required[TaskUnionMember2ResponseSchema]

    type: Required[Literal["array-extraction"]]


Task: TypeAlias = Union[TaskUnionMember0, TaskUnionMember1, TaskUnionMember2]
