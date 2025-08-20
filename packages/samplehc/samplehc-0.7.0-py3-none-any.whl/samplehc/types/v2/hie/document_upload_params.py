# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["DocumentUploadParams", "DocumentType", "DocumentTypeCoding"]


class DocumentUploadParams(TypedDict, total=False):
    description: Required[str]
    """A brief description of the document."""

    document_type: Required[Annotated[DocumentType, PropertyInfo(alias="documentType")]]
    """The type of document being uploaded."""

    file_metadata_id: Required[Annotated[str, PropertyInfo(alias="fileMetadataId")]]
    """The ID of the file metadata to upload."""

    patient_id: Required[Annotated[str, PropertyInfo(alias="patientId")]]
    """The external Patient ID that you store and can use to reference this Patient."""

    date_end: Annotated[str, PropertyInfo(alias="dateEnd")]
    """ISO 8601 timestamp for when the document period ends."""

    date_start: Annotated[str, PropertyInfo(alias="dateStart")]
    """ISO 8601 timestamp for when the document period starts."""

    facility_name: Annotated[str, PropertyInfo(alias="facilityName")]
    """The name and type of facility (e.g., 'John Snow Clinic - Acute Care Centre')."""


class DocumentTypeCoding(TypedDict, total=False):
    code: Required[str]
    """The code from the terminology system."""

    display: Required[str]
    """Human-readable display name for the code."""

    system: Required[str]
    """The terminology system URI (e.g., http://loinc.org)."""


class DocumentType(TypedDict, total=False):
    text: Required[str]
    """Plain text representation of the document type."""

    coding: Iterable[DocumentTypeCoding]
    """Array of coded representations from terminology systems."""
