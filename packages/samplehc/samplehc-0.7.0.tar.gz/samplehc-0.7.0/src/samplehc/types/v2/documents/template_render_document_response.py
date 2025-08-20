# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["TemplateRenderDocumentResponse"]


class TemplateRenderDocumentResponse(BaseModel):
    body: Optional[object] = None
    """The rendered document body."""
