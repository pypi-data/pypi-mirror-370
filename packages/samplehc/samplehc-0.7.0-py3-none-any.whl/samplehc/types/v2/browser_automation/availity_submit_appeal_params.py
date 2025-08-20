# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["AvailitySubmitAppealParams", "Document"]


class AvailitySubmitAppealParams(TypedDict, total=False):
    availity_payer: Required[Annotated[Literal["Anthem - CA"], PropertyInfo(alias="availityPayer")]]

    billed_amount: Required[Annotated[str, PropertyInfo(alias="billedAmount")]]

    claim_number: Required[Annotated[str, PropertyInfo(alias="claimNumber")]]

    contact_phone_number: Required[Annotated[str, PropertyInfo(alias="contactPhoneNumber")]]

    document: Required[Document]

    member_date_of_birth: Required[Annotated[str, PropertyInfo(alias="memberDateOfBirth")]]

    member_first_name: Required[Annotated[str, PropertyInfo(alias="memberFirstName")]]

    member_id: Required[Annotated[str, PropertyInfo(alias="memberId")]]

    member_last_name: Required[Annotated[str, PropertyInfo(alias="memberLastName")]]

    request_reason: Required[
        Annotated[
            Literal[
                "Authorization Issue",
                "Balance Bill (Not Medicaid)",
                "Benefit Issue",
                "Claim Coding Issue",
                "Claim Payment Issue",
                "Contract Dispute",
                "DRG Outlier Review",
                "Federal Surprise Bill (Not Medicaid)",
                "State Surprise Bill (Not Medicaid)",
                "Timely Filing",
            ],
            PropertyInfo(alias="requestReason"),
        ]
    ]

    service_start_date: Required[Annotated[str, PropertyInfo(alias="serviceStartDate")]]

    state: Required[str]

    supporting_rationale: Required[Annotated[str, PropertyInfo(alias="supportingRationale")]]


class Document(TypedDict, total=False):
    id: Required[str]

    file_name: Required[Annotated[str, PropertyInfo(alias="fileName")]]
