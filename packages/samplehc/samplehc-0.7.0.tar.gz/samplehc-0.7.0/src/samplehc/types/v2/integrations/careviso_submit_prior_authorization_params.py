# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["CarevisoSubmitPriorAuthorizationParams", "Attachment"]


class CarevisoSubmitPriorAuthorizationParams(TypedDict, total=False):
    attachments: Required[Iterable[Attachment]]

    case_type: Required[
        Annotated[Literal["prior_auth_request", "benefits_investigation"], PropertyInfo(alias="caseType")]
    ]

    cpt_codes: Required[Annotated[List[str], PropertyInfo(alias="cptCodes")]]

    group_id: Required[Annotated[str, PropertyInfo(alias="groupId")]]

    icd10_codes: Required[Annotated[List[str], PropertyInfo(alias="icd10Codes")]]

    insurance_name: Required[Annotated[str, PropertyInfo(alias="insuranceName")]]

    lab_order_id: Required[Annotated[str, PropertyInfo(alias="labOrderId")]]

    member_id: Required[Annotated[str, PropertyInfo(alias="memberId")]]

    patient_dob: Required[Annotated[str, PropertyInfo(alias="patientDob")]]

    patient_first_name: Required[Annotated[str, PropertyInfo(alias="patientFirstName")]]

    patient_id: Required[Annotated[str, PropertyInfo(alias="patientId")]]

    patient_last_name: Required[Annotated[str, PropertyInfo(alias="patientLastName")]]

    patient_phone: Required[Annotated[str, PropertyInfo(alias="patientPhone")]]

    provider_fax: Required[Annotated[str, PropertyInfo(alias="providerFax")]]

    provider_first_name: Required[Annotated[str, PropertyInfo(alias="providerFirstName")]]

    provider_id: Required[Annotated[str, PropertyInfo(alias="providerId")]]

    provider_last_name: Required[Annotated[str, PropertyInfo(alias="providerLastName")]]

    provider_npi: Required[Annotated[str, PropertyInfo(alias="providerNpi")]]

    provider_phone: Required[Annotated[str, PropertyInfo(alias="providerPhone")]]

    service_date: Required[Annotated[str, PropertyInfo(alias="serviceDate")]]
    """The date of service for the test. Should be in the format YYYY-MM-DD."""

    test_names: Required[Annotated[List[str], PropertyInfo(alias="testNames")]]

    accession_date: Annotated[str, PropertyInfo(alias="accessionDate")]

    collection_date: Annotated[str, PropertyInfo(alias="collectionDate")]
    """The date of collection for the test. Should be in the format YYYY-MM-DD."""

    collection_type: Annotated[str, PropertyInfo(alias="collectionType")]
    """The type of collection for the test"""

    insurance_id: Annotated[str, PropertyInfo(alias="insuranceId")]

    patient_city: Annotated[str, PropertyInfo(alias="patientCity")]

    patient_gender: Annotated[Literal["M", "F", "Non-binary", "Non-specified"], PropertyInfo(alias="patientGender")]

    patient_state: Annotated[str, PropertyInfo(alias="patientState")]

    patient_street: Annotated[str, PropertyInfo(alias="patientStreet")]

    patient_street2: Annotated[str, PropertyInfo(alias="patientStreet2")]

    patient_zip: Annotated[str, PropertyInfo(alias="patientZip")]

    test_identifiers: Annotated[List[str], PropertyInfo(alias="testIdentifiers")]

    test_type: Annotated[str, PropertyInfo(alias="testType")]


class Attachment(TypedDict, total=False):
    id: Required[str]

    file_name: Required[Annotated[str, PropertyInfo(alias="fileName")]]
