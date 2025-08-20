# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["V1SqlExecuteParams"]


class V1SqlExecuteParams(TypedDict, total=False):
    query: Required[str]
    """The SQL query to execute."""

    array_mode: Annotated[bool, PropertyInfo(alias="arrayMode")]
    """If true, rows will be returned as arrays of values instead of objects.

    Defaults to false.
    """

    params: Iterable[object]
    """An array of parameters to be used in the SQL query.

    Use placeholders like $1, $2, etc. in the query string.
    """
