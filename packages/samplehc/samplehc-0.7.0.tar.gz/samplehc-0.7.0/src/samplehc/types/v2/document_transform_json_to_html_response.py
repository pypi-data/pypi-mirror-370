# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["DocumentTransformJsonToHTMLResponse"]


class DocumentTransformJsonToHTMLResponse(BaseModel):
    html: str
    """The HTML string."""
