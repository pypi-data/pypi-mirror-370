# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["DocumentRetrieveResponse", "UnionMember0", "UnionMember1", "UnionMember2", "UnionMember3"]


class UnionMember0(BaseModel):
    id: str

    file_name: str = FieldInfo(alias="fileName")

    mime_type: Literal["application/pdf"] = FieldInfo(alias="mimeType")

    presigned_url: str = FieldInfo(alias="presignedUrl")

    ocr_response: Optional[object] = FieldInfo(alias="ocrResponse", default=None)


class UnionMember1(BaseModel):
    id: str

    file_name: str = FieldInfo(alias="fileName")

    mime_type: Literal["application/fhir+json"] = FieldInfo(alias="mimeType")

    chunked_response: Optional[object] = FieldInfo(alias="chunkedResponse", default=None)


class UnionMember2(BaseModel):
    id: str

    file_name: str = FieldInfo(alias="fileName")

    mime_type: Literal["application/fhir+jsonl"] = FieldInfo(alias="mimeType")

    chunked_response: Optional[object] = FieldInfo(alias="chunkedResponse", default=None)


class UnionMember3(BaseModel):
    id: str

    file_name: str = FieldInfo(alias="fileName")

    mime_type: Literal["application/json"] = FieldInfo(alias="mimeType")

    presigned_url: str = FieldInfo(alias="presignedUrl")


DocumentRetrieveResponse: TypeAlias = Union[UnionMember0, UnionMember1, UnionMember2, UnionMember3]
