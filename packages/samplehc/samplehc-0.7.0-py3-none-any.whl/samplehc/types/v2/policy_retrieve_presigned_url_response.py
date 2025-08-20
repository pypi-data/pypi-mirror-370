# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["PolicyRetrievePresignedURLResponse"]


class PolicyRetrievePresignedURLResponse(BaseModel):
    mime_type: str = FieldInfo(alias="mimeType")
    """MIME type of the policy document"""

    url: str
    """Presigned URL to access the policy document"""
