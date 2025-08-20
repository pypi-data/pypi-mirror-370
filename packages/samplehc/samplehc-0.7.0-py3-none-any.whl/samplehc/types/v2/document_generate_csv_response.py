# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["DocumentGenerateCsvResponse", "Document"]


class Document(BaseModel):
    id: str

    file_name: str = FieldInfo(alias="fileName")


class DocumentGenerateCsvResponse(BaseModel):
    document: Document
    """Metadata of the newly generated CSV document."""
