# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ......_models import BaseModel

__all__ = ["ClinicalQuestionListResponse", "Question", "Response"]


class Question(BaseModel):
    id: float

    prompt: str

    type: Literal["text", "select", "select-other", "multi-select"]

    options: Optional[List[str]] = None


class Response(BaseModel):
    question_id: float

    value: Union[str, List[str]]

    is_valid: Optional[bool] = None

    other_value: Optional[str] = None


class ClinicalQuestionListResponse(BaseModel):
    are_all_questions_answered: bool = FieldInfo(alias="areAllQuestionsAnswered")

    questions: List[Question]

    status: Literal["success"]

    responses: Optional[List[Response]] = None
