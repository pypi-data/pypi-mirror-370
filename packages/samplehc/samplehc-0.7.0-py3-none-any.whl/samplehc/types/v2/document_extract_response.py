# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["DocumentExtractResponse"]


class DocumentExtractResponse(BaseModel):
    async_result_id: str = FieldInfo(alias="asyncResultId")
    """The ID to track the asynchronous extraction task."""
