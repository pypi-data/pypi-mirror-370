# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["BrowserAgentInvokeResponse"]


class BrowserAgentInvokeResponse(BaseModel):
    async_result_id: str = FieldInfo(alias="asyncResultId")
    """ID to track the browser agent invocation status"""
