# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DocumentGenerateCsvParams", "Options"]


class DocumentGenerateCsvParams(TypedDict, total=False):
    file_name: Required[Annotated[str, PropertyInfo(alias="fileName")]]
    """The desired file name for the generated CSV (e.g., 'report.csv')."""

    rows: Required[Iterable[Dict[str, Union[str, float]]]]
    """
    Array of objects, where each object represents a row with column headers as
    keys.
    """

    options: Options


class Options(TypedDict, total=False):
    column_order: Annotated[List[str], PropertyInfo(alias="columnOrder")]
    """Optional array of strings to specify column order."""

    export_as_excel: Annotated[bool, PropertyInfo(alias="exportAsExcel")]
    """If true, includes BOM for Excel compatibility."""
