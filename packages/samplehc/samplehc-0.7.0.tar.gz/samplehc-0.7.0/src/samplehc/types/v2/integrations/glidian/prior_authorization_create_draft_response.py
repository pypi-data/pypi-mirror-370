# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = ["PriorAuthorizationCreateDraftResponse"]


class PriorAuthorizationCreateDraftResponse(BaseModel):
    are_all_questions_answered: bool = FieldInfo(alias="areAllQuestionsAnswered")

    clinical_questions: List[object] = FieldInfo(alias="clinicalQuestions")

    glidian_record_id: str = FieldInfo(alias="glidianRecordId")

    status: Literal["draft"]

    record: Optional[object] = None
