# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DocumentPresignedUploadURLParams"]


class DocumentPresignedUploadURLParams(TypedDict, total=False):
    file_name: Required[Annotated[str, PropertyInfo(alias="fileName")]]
    """The name of the file to be uploaded."""

    mime_type: Required[
        Annotated[
            Literal[
                "application/zip",
                "application/x-zip-compressed",
                "multipart/x-zip",
                "application/x-compress",
                "application/pdf",
                "text/csv",
                "application/javascript",
                "text/css",
                "image/png",
                "video/mp4",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "text/html",
                "application/json",
            ],
            PropertyInfo(alias="mimeType"),
        ]
    ]
    """The MIME type of the file to be uploaded."""
