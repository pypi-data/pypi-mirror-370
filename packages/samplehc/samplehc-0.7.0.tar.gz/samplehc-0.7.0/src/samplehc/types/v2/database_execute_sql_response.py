# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union

from ..._models import BaseModel

__all__ = ["DatabaseExecuteSqlResponse"]


class DatabaseExecuteSqlResponse(BaseModel):
    rows: Union[List[Dict[str, object]], List[List[object]]]
    """An array of results from the query.

    Each item is an object with the column names as keys.
    """
