# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from ......_models import BaseModel

__all__ = ["ClinicalQuestionUpdateResponse"]


class ClinicalQuestionUpdateResponse(BaseModel):
    are_all_questions_answered: bool = FieldInfo(alias="areAllQuestionsAnswered")

    can_submit: bool = FieldInfo(alias="canSubmit")

    questions: List[object]
