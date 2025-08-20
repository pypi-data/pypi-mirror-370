# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["DocumentQueryResponse"]


class DocumentQueryResponse(BaseModel):
    async_result_id: str = FieldInfo(alias="asyncResultId")
    """The async result ID.

    When the async result completes, the result will contain both FHIR bundle and
    document objects.
    """
