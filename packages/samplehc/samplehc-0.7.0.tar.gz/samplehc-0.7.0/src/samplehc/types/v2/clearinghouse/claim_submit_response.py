# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["ClaimSubmitResponse"]


class ClaimSubmitResponse(BaseModel):
    claim_submission_id: str = FieldInfo(alias="claimSubmissionId")
    """Sample's internal ID of the claim submission."""

    patient_control_number: str = FieldInfo(alias="patientControlNumber")
    """The patient control number we send to the clearinghouse for identification.

    This is a alphanumeric string with <= 20 characters.
    """
