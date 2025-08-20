# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["DocumentUnzipResponse", "Document"]


class Document(BaseModel):
    id: str

    file_name: str = FieldInfo(alias="fileName")


class DocumentUnzipResponse(BaseModel):
    documents: List[Document]
    """The list of PDFs found in the ZIP file."""
