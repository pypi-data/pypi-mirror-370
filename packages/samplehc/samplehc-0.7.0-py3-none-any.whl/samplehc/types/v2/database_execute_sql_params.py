# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["DatabaseExecuteSqlParams"]


class DatabaseExecuteSqlParams(TypedDict, total=False):
    query: Required[str]
    """The SQL query to execute."""

    params: List[Union[str, float, bool, Optional[Literal["null"]], Iterable[object], Dict[str, object]]]
    """An array of parameters to be used in the SQL query.

    Supports primitive types (string, number, boolean, null), arrays, and objects.
    Use placeholders like $1, $2, etc. in the query string. Examples: ["hello", 123,
    [1,2,3], {"name": "John", "age": 30}]
    """
