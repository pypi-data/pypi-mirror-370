# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["TaskUpdateScreenTimeParams"]


class TaskUpdateScreenTimeParams(TypedDict, total=False):
    additional_screen_time: Required[Annotated[float, PropertyInfo(alias="additionalScreenTime")]]
    """The additional screen time in milliseconds to add to the task's total."""
