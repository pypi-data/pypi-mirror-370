# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel

__all__ = ["DocumentSearchResponse"]


class DocumentSearchResponse(BaseModel):
    results: List[object]
    """An array of search results. The structure of each result may vary."""
