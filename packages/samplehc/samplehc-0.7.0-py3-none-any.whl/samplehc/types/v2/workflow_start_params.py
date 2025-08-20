# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["WorkflowStartParams"]


class WorkflowStartParams(TypedDict, total=False):
    body: object

    x_sample_start_data_parse_method: Annotated[
        Literal["standard", "top-level"], PropertyInfo(alias="X-Sample-Start-Data-Parse-Method")
    ]
