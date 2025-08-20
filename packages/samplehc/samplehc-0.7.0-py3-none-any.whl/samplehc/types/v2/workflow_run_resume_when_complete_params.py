# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["WorkflowRunResumeWhenCompleteParams"]


class WorkflowRunResumeWhenCompleteParams(TypedDict, total=False):
    async_result_id: Required[Annotated[str, PropertyInfo(alias="asyncResultId")]]
    """The unique identifier of the asynchronous result to monitor before resuming."""
