# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["LegacyExtractResponse"]


class LegacyExtractResponse(BaseModel):
    async_result_id: str = FieldInfo(alias="asyncResultId")
    """The ID to track the asynchronous legacy extraction task."""
