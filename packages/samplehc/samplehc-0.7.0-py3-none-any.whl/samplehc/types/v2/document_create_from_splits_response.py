# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["DocumentCreateFromSplitsResponse", "CreatedDocument"]


class CreatedDocument(BaseModel):
    id: str

    end_page_inclusive: float = FieldInfo(alias="endPageInclusive")
    """The ending page number of this split document (1-indexed)."""

    file_name: str = FieldInfo(alias="fileName")

    start_page_inclusive: float = FieldInfo(alias="startPageInclusive")
    """The starting page number of this split document (1-indexed)."""


class DocumentCreateFromSplitsResponse(BaseModel):
    created_documents: List[CreatedDocument] = FieldInfo(alias="createdDocuments")
    """An array of newly created document resources from the splits."""
