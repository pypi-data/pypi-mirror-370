# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["DocumentCombineResponse", "Document"]


class Document(BaseModel):
    id: str

    file_name: str = FieldInfo(alias="fileName")


class DocumentCombineResponse(BaseModel):
    document: Document
    """Metadata of the newly created combined PDF document."""
