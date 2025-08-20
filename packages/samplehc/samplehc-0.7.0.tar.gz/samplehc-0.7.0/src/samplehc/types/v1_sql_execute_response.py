# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import TypeAlias

from .._models import BaseModel

__all__ = ["V1SqlExecuteResponse", "Rows", "Error"]


class Rows(BaseModel):
    rows: List[object]
    """An array of results from the query.

    Each item is an object (default) or an array of values (if arrayMode is true).
    """


class Error(BaseModel):
    error: str
    """
    An error message if the query was processed but resulted in a recoverable error
    (e.g., syntax error in SQL that was caught gracefully).
    """


V1SqlExecuteResponse: TypeAlias = Union[Rows, Error]
