# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = [
    "ClaimSubmitParams",
    "Billing",
    "BillingAddress",
    "BillingContactInformation",
    "ClaimInformation",
    "ClaimInformationHealthCareCodeInformation",
    "ClaimInformationServiceLine",
    "ClaimInformationServiceLineProfessionalService",
    "ClaimInformationServiceLineProfessionalServiceCompositeDiagnosisCodePointers",
    "ClaimInformationServiceLineAmbulanceCertification",
    "ClaimInformationServiceLineAmbulanceDropOffLocation",
    "ClaimInformationServiceLineAmbulancePickUpLocation",
    "ClaimInformationServiceLineAmbulanceTransportInformation",
    "ClaimInformationServiceLineConditionIndicatorDurableMedicalEquipment",
    "ClaimInformationServiceLineContractInformation",
    "ClaimInformationServiceLineDrugIdentification",
    "ClaimInformationServiceLineDurableMedicalEquipmentCertificateOfMedicalNecessity",
    "ClaimInformationServiceLineDurableMedicalEquipmentCertification",
    "ClaimInformationServiceLineDurableMedicalEquipmentService",
    "ClaimInformationServiceLineFormIdentification",
    "ClaimInformationServiceLineFormIdentificationSupportingDocumentation",
    "ClaimInformationServiceLineLineAdjudicationInformation",
    "ClaimInformationServiceLineLineAdjudicationInformationClaimAdjustmentInformation",
    "ClaimInformationServiceLineLineAdjudicationInformationClaimAdjustmentInformationAdjustmentDetail",
    "ClaimInformationServiceLineLinePricingRepricingInformation",
    "ClaimInformationServiceLineOrderingProvider",
    "ClaimInformationServiceLineOrderingProviderAddress",
    "ClaimInformationServiceLineOrderingProviderContactInformation",
    "ClaimInformationServiceLineOrderingProviderSecondaryIdentifier",
    "ClaimInformationServiceLinePurchasedServiceInformation",
    "ClaimInformationServiceLinePurchasedServiceProvider",
    "ClaimInformationServiceLinePurchasedServiceProviderAddress",
    "ClaimInformationServiceLinePurchasedServiceProviderContactInformation",
    "ClaimInformationServiceLinePurchasedServiceProviderSecondaryIdentifier",
    "ClaimInformationServiceLineReferringProvider",
    "ClaimInformationServiceLineReferringProviderAddress",
    "ClaimInformationServiceLineReferringProviderContactInformation",
    "ClaimInformationServiceLineReferringProviderSecondaryIdentifier",
    "ClaimInformationServiceLineRenderingProvider",
    "ClaimInformationServiceLineRenderingProviderAddress",
    "ClaimInformationServiceLineRenderingProviderContactInformation",
    "ClaimInformationServiceLineRenderingProviderSecondaryIdentifier",
    "ClaimInformationServiceLineServiceFacilityLocation",
    "ClaimInformationServiceLineServiceFacilityLocationAddress",
    "ClaimInformationServiceLineServiceFacilityLocationSecondaryIdentifier",
    "ClaimInformationServiceLineServiceLineDateInformation",
    "ClaimInformationServiceLineServiceLineReferenceInformation",
    "ClaimInformationServiceLineServiceLineReferenceInformationPriorAuthorization",
    "ClaimInformationServiceLineServiceLineSupplementalInformation",
    "ClaimInformationServiceLineSupervisingProvider",
    "ClaimInformationServiceLineSupervisingProviderAddress",
    "ClaimInformationServiceLineSupervisingProviderContactInformation",
    "ClaimInformationServiceLineSupervisingProviderSecondaryIdentifier",
    "ClaimInformationServiceLineTestResult",
    "ClaimInformationAmbulanceCertification",
    "ClaimInformationAmbulanceDropOffLocation",
    "ClaimInformationAmbulancePickUpLocation",
    "ClaimInformationAmbulanceTransportInformation",
    "ClaimInformationClaimContractInformation",
    "ClaimInformationClaimDateInformation",
    "ClaimInformationClaimNote",
    "ClaimInformationClaimPricingRepricingInformation",
    "ClaimInformationClaimSupplementalInformation",
    "ClaimInformationClaimSupplementalInformationReportInformation",
    "ClaimInformationConditionInformation",
    "ClaimInformationEpsdtReferral",
    "ClaimInformationOtherSubscriberInformation",
    "ClaimInformationOtherSubscriberInformationOtherPayerName",
    "ClaimInformationOtherSubscriberInformationOtherPayerNameOtherPayerAddress",
    "ClaimInformationOtherSubscriberInformationOtherPayerNameOtherPayerSecondaryIdentifier",
    "ClaimInformationOtherSubscriberInformationOtherSubscriberName",
    "ClaimInformationOtherSubscriberInformationOtherSubscriberNameOtherInsuredAddress",
    "ClaimInformationOtherSubscriberInformationClaimLevelAdjustment",
    "ClaimInformationOtherSubscriberInformationClaimLevelAdjustmentAdjustmentDetail",
    "ClaimInformationOtherSubscriberInformationMedicareOutpatientAdjudication",
    "ClaimInformationOtherSubscriberInformationOtherPayerBillingProvider",
    "ClaimInformationOtherSubscriberInformationOtherPayerBillingProviderOtherPayerBillingProviderIdentifier",
    "ClaimInformationOtherSubscriberInformationOtherPayerReferringProvider",
    "ClaimInformationOtherSubscriberInformationOtherPayerReferringProviderOtherPayerReferringProviderIdentifier",
    "ClaimInformationOtherSubscriberInformationOtherPayerRenderingProvider",
    "ClaimInformationOtherSubscriberInformationOtherPayerRenderingProviderOtherPayerRenderingProviderSecondaryIdentifier",
    "ClaimInformationOtherSubscriberInformationOtherPayerServiceFacilityLocation",
    "ClaimInformationOtherSubscriberInformationOtherPayerServiceFacilityLocationOtherPayerServiceFacilityLocationSecondaryIdentifier",
    "ClaimInformationOtherSubscriberInformationOtherPayerSupervisingProvider",
    "ClaimInformationOtherSubscriberInformationOtherPayerSupervisingProviderOtherPayerSupervisingProviderIdentifier",
    "ClaimInformationPatientConditionInformationVision",
    "ClaimInformationServiceFacilityLocation",
    "ClaimInformationServiceFacilityLocationAddress",
    "ClaimInformationServiceFacilityLocationSecondaryIdentifier",
    "ClaimInformationSpinalManipulationServiceInformation",
    "Receiver",
    "Submitter",
    "SubmitterContactInformation",
    "Subscriber",
    "SubscriberAddress",
    "SubscriberContactInformation",
    "Dependent",
    "DependentAddress",
    "DependentContactInformation",
    "Ordering",
    "OrderingAddress",
    "OrderingContactInformation",
    "PayerAddress",
    "PayToAddress",
    "PayToPlan",
    "PayToPlanAddress",
    "Provider",
    "ProviderAddress",
    "ProviderContactInformation",
    "Referring",
    "ReferringAddress",
    "ReferringContactInformation",
    "Rendering",
    "RenderingAddress",
    "RenderingContactInformation",
    "Supervising",
    "SupervisingAddress",
    "SupervisingContactInformation",
]


class ClaimSubmitParams(TypedDict, total=False):
    billing: Required[Billing]

    claim_information: Required[Annotated[ClaimInformation, PropertyInfo(alias="claimInformation")]]

    is_testing: Required[Annotated[bool, PropertyInfo(alias="isTesting")]]

    receiver: Required[Receiver]

    submitter: Required[Submitter]

    subscriber: Required[Subscriber]

    trading_partner_service_id: Required[Annotated[str, PropertyInfo(alias="tradingPartnerServiceId")]]

    control_number: Annotated[str, PropertyInfo(alias="controlNumber")]

    dependent: Dependent

    ordering: Ordering

    payer_address: Annotated[PayerAddress, PropertyInfo(alias="payerAddress")]

    pay_to_address: Annotated[PayToAddress, PropertyInfo(alias="payToAddress")]

    pay_to_plan: Annotated[PayToPlan, PropertyInfo(alias="payToPlan")]

    providers: Iterable[Provider]

    referring: Referring

    rendering: Rendering

    supervising: Supervising

    trading_partner_name: Annotated[str, PropertyInfo(alias="tradingPartnerName")]


class BillingAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class BillingContactInformation(TypedDict, total=False):
    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    name: str

    phone_extension: Annotated[str, PropertyInfo(alias="phoneExtension")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]


class Billing(TypedDict, total=False):
    address: BillingAddress

    commercial_number: Annotated[str, PropertyInfo(alias="commercialNumber")]

    contact_information: Annotated[BillingContactInformation, PropertyInfo(alias="contactInformation")]

    employer_id: Annotated[str, PropertyInfo(alias="employerId")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    location_number: Annotated[str, PropertyInfo(alias="locationNumber")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    provider_type: Annotated[str, PropertyInfo(alias="providerType")]

    provider_upin_number: Annotated[str, PropertyInfo(alias="providerUpinNumber")]

    ssn: str

    state_license_number: Annotated[str, PropertyInfo(alias="stateLicenseNumber")]

    suffix: str

    taxonomy_code: Annotated[str, PropertyInfo(alias="taxonomyCode")]


class ClaimInformationHealthCareCodeInformation(TypedDict, total=False):
    diagnosis_code: Required[Annotated[str, PropertyInfo(alias="diagnosisCode")]]

    diagnosis_type_code: Required[Annotated[Literal["BK", "ABK", "BF", "ABF"], PropertyInfo(alias="diagnosisTypeCode")]]


class ClaimInformationServiceLineProfessionalServiceCompositeDiagnosisCodePointers(TypedDict, total=False):
    diagnosis_code_pointers: Required[Annotated[List[str], PropertyInfo(alias="diagnosisCodePointers")]]


class ClaimInformationServiceLineProfessionalService(TypedDict, total=False):
    composite_diagnosis_code_pointers: Required[
        Annotated[
            ClaimInformationServiceLineProfessionalServiceCompositeDiagnosisCodePointers,
            PropertyInfo(alias="compositeDiagnosisCodePointers"),
        ]
    ]

    line_item_charge_amount: Required[Annotated[str, PropertyInfo(alias="lineItemChargeAmount")]]

    measurement_unit: Required[Annotated[Literal["MJ", "UN"], PropertyInfo(alias="measurementUnit")]]

    procedure_code: Required[Annotated[str, PropertyInfo(alias="procedureCode")]]

    procedure_identifier: Required[
        Annotated[Literal["ER", "HC", "IV", "WK"], PropertyInfo(alias="procedureIdentifier")]
    ]

    service_unit_count: Required[Annotated[str, PropertyInfo(alias="serviceUnitCount")]]

    copay_status_code: Annotated[Literal["0"], PropertyInfo(alias="copayStatusCode")]

    description: str

    emergency_indicator: Annotated[Literal["Y"], PropertyInfo(alias="emergencyIndicator")]

    epsdt_indicator: Annotated[Literal["Y"], PropertyInfo(alias="epsdtIndicator")]

    family_planning_indicator: Annotated[Literal["Y"], PropertyInfo(alias="familyPlanningIndicator")]

    place_of_service_code: Annotated[str, PropertyInfo(alias="placeOfServiceCode")]

    procedure_modifiers: Annotated[List[str], PropertyInfo(alias="procedureModifiers")]


class ClaimInformationServiceLineAmbulanceCertification(TypedDict, total=False):
    certification_condition_indicator: Required[
        Annotated[Literal["N", "Y"], PropertyInfo(alias="certificationConditionIndicator")]
    ]

    condition_codes: Required[
        Annotated[List[Literal["01", "04", "05", "06", "07", "08", "09", "12"]], PropertyInfo(alias="conditionCodes")]
    ]


class ClaimInformationServiceLineAmbulanceDropOffLocation(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ClaimInformationServiceLineAmbulancePickUpLocation(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ClaimInformationServiceLineAmbulanceTransportInformation(TypedDict, total=False):
    ambulance_transport_reason_code: Required[
        Annotated[Literal["A", "B", "C", "D", "E"], PropertyInfo(alias="ambulanceTransportReasonCode")]
    ]

    transport_distance_in_miles: Required[Annotated[str, PropertyInfo(alias="transportDistanceInMiles")]]

    patient_weight_in_pounds: Annotated[str, PropertyInfo(alias="patientWeightInPounds")]

    round_trip_purpose_description: Annotated[str, PropertyInfo(alias="roundTripPurposeDescription")]

    stretcher_purpose_description: Annotated[str, PropertyInfo(alias="stretcherPurposeDescription")]


class ClaimInformationServiceLineConditionIndicatorDurableMedicalEquipment(TypedDict, total=False):
    certification_condition_indicator: Required[
        Annotated[Literal["Y", "N"], PropertyInfo(alias="certificationConditionIndicator")]
    ]

    condition_indicator: Required[Annotated[Literal["38", "ZV"], PropertyInfo(alias="conditionIndicator")]]

    condition_indicator_code: Annotated[Literal["38", "ZV"], PropertyInfo(alias="conditionIndicatorCode")]


class ClaimInformationServiceLineContractInformation(TypedDict, total=False):
    contract_type_code: Required[
        Annotated[Literal["01", "02", "03", "04", "05", "06", "09"], PropertyInfo(alias="contractTypeCode")]
    ]

    contract_amount: Annotated[str, PropertyInfo(alias="contractAmount")]

    contract_code: Annotated[str, PropertyInfo(alias="contractCode")]

    contract_percentage: Annotated[str, PropertyInfo(alias="contractPercentage")]

    contract_version_identifier: Annotated[str, PropertyInfo(alias="contractVersionIdentifier")]

    terms_discount_percentage: Annotated[str, PropertyInfo(alias="termsDiscountPercentage")]


class ClaimInformationServiceLineDrugIdentification(TypedDict, total=False):
    measurement_unit_code: Required[
        Annotated[Literal["F2", "GR", "ME", "ML", "UN"], PropertyInfo(alias="measurementUnitCode")]
    ]

    national_drug_code: Required[Annotated[str, PropertyInfo(alias="nationalDrugCode")]]

    national_drug_unit_count: Required[Annotated[str, PropertyInfo(alias="nationalDrugUnitCount")]]

    service_id_qualifier: Required[
        Annotated[Literal["EN", "EO", "HI", "N4", "ON", "UK", "UP"], PropertyInfo(alias="serviceIdQualifier")]
    ]

    link_sequence_number: Annotated[str, PropertyInfo(alias="linkSequenceNumber")]

    pharmacy_prescription_number: Annotated[str, PropertyInfo(alias="pharmacyPrescriptionNumber")]


class ClaimInformationServiceLineDurableMedicalEquipmentCertificateOfMedicalNecessity(TypedDict, total=False):
    attachment_transmission_code: Required[
        Annotated[Literal["AB", "AD", "AF", "AG", "NS"], PropertyInfo(alias="attachmentTransmissionCode")]
    ]


class ClaimInformationServiceLineDurableMedicalEquipmentCertification(TypedDict, total=False):
    certification_type_code: Required[Annotated[Literal["I", "R", "S"], PropertyInfo(alias="certificationTypeCode")]]

    durable_medical_equipment_duration_in_months: Required[
        Annotated[str, PropertyInfo(alias="durableMedicalEquipmentDurationInMonths")]
    ]


class ClaimInformationServiceLineDurableMedicalEquipmentService(TypedDict, total=False):
    days: Required[str]

    frequency_code: Required[Annotated[Literal["1", "4", "6"], PropertyInfo(alias="frequencyCode")]]

    purchase_price: Required[Annotated[str, PropertyInfo(alias="purchasePrice")]]

    rental_price: Required[Annotated[str, PropertyInfo(alias="rentalPrice")]]


class ClaimInformationServiceLineFormIdentificationSupportingDocumentation(TypedDict, total=False):
    question_number: Required[Annotated[str, PropertyInfo(alias="questionNumber")]]

    question_response: Annotated[str, PropertyInfo(alias="questionResponse")]

    question_response_as_date: Annotated[str, PropertyInfo(alias="questionResponseAsDate")]

    question_response_as_percent: Annotated[str, PropertyInfo(alias="questionResponseAsPercent")]

    question_response_code: Annotated[Literal["N", "W", "Y"], PropertyInfo(alias="questionResponseCode")]


class ClaimInformationServiceLineFormIdentification(TypedDict, total=False):
    form_identifier: Required[Annotated[str, PropertyInfo(alias="formIdentifier")]]

    form_type_code: Required[Annotated[Literal["AS", "UT"], PropertyInfo(alias="formTypeCode")]]

    supporting_documentation: Annotated[
        Iterable[ClaimInformationServiceLineFormIdentificationSupportingDocumentation],
        PropertyInfo(alias="supportingDocumentation"),
    ]


class ClaimInformationServiceLineLineAdjudicationInformationClaimAdjustmentInformationAdjustmentDetail(
    TypedDict, total=False
):
    adjustment_amount: Required[Annotated[str, PropertyInfo(alias="adjustmentAmount")]]

    adjustment_reason_code: Required[Annotated[str, PropertyInfo(alias="adjustmentReasonCode")]]

    adjustment_quantity: Annotated[str, PropertyInfo(alias="adjustmentQuantity")]


class ClaimInformationServiceLineLineAdjudicationInformationClaimAdjustmentInformation(TypedDict, total=False):
    adjustment_details: Required[
        Annotated[
            Iterable[ClaimInformationServiceLineLineAdjudicationInformationClaimAdjustmentInformationAdjustmentDetail],
            PropertyInfo(alias="adjustmentDetails"),
        ]
    ]

    adjustment_group_code: Required[
        Annotated[Literal["CO", "CR", "OA", "PI", "PR"], PropertyInfo(alias="adjustmentGroupCode")]
    ]


class ClaimInformationServiceLineLineAdjudicationInformation(TypedDict, total=False):
    adjudication_or_payment_date: Required[Annotated[str, PropertyInfo(alias="adjudicationOrPaymentDate")]]

    other_payer_primary_identifier: Required[Annotated[str, PropertyInfo(alias="otherPayerPrimaryIdentifier")]]

    paid_service_unit_count: Required[Annotated[str, PropertyInfo(alias="paidServiceUnitCount")]]

    procedure_code: Required[Annotated[str, PropertyInfo(alias="procedureCode")]]

    service_id_qualifier: Required[
        Annotated[Literal["ER", "HC", "HP", "IV", "WK"], PropertyInfo(alias="serviceIdQualifier")]
    ]

    service_line_paid_amount: Required[Annotated[str, PropertyInfo(alias="serviceLinePaidAmount")]]

    bundled_or_unbundled_line_number: Annotated[str, PropertyInfo(alias="bundledOrUnbundledLineNumber")]

    claim_adjustment_information: Annotated[
        Iterable[ClaimInformationServiceLineLineAdjudicationInformationClaimAdjustmentInformation],
        PropertyInfo(alias="claimAdjustmentInformation"),
    ]

    procedure_code_description: Annotated[str, PropertyInfo(alias="procedureCodeDescription")]

    procedure_modifier: Annotated[List[str], PropertyInfo(alias="procedureModifier")]

    remaining_patient_liability: Annotated[str, PropertyInfo(alias="remainingPatientLiability")]


class ClaimInformationServiceLineLinePricingRepricingInformation(TypedDict, total=False):
    pricing_methodology_code: Required[
        Annotated[
            Literal["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14"],
            PropertyInfo(alias="pricingMethodologyCode"),
        ]
    ]

    repriced_allowed_amount: Required[Annotated[str, PropertyInfo(alias="repricedAllowedAmount")]]

    exception_code: Annotated[Literal["1", "2", "3", "4", "5", "6"], PropertyInfo(alias="exceptionCode")]

    policy_compliance_code: Annotated[Literal["1", "2", "3", "4", "5"], PropertyInfo(alias="policyComplianceCode")]

    reject_reason_code: Annotated[Literal["T1", "T2", "T3", "T4", "T5", "T6"], PropertyInfo(alias="rejectReasonCode")]

    repriced_approved_ambulatory_patient_group_amount: Annotated[
        str, PropertyInfo(alias="repricedApprovedAmbulatoryPatientGroupAmount")
    ]

    repriced_approved_ambulatory_patient_group_code: Annotated[
        str, PropertyInfo(alias="repricedApprovedAmbulatoryPatientGroupCode")
    ]

    repriced_saving_amount: Annotated[str, PropertyInfo(alias="repricedSavingAmount")]

    repricing_organization_identifier: Annotated[str, PropertyInfo(alias="repricingOrganizationIdentifier")]

    repricing_per_diem_or_flat_rate_amount: Annotated[str, PropertyInfo(alias="repricingPerDiemOrFlatRateAmount")]


class ClaimInformationServiceLineOrderingProviderAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ClaimInformationServiceLineOrderingProviderContactInformation(TypedDict, total=False):
    name: Required[str]

    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    phone_extension: Annotated[str, PropertyInfo(alias="phoneExtension")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]


class ClaimInformationServiceLineOrderingProviderSecondaryIdentifier(TypedDict, total=False):
    identifier: Required[str]

    qualifier: Required[str]

    other_identifier: Annotated[str, PropertyInfo(alias="otherIdentifier")]


class ClaimInformationServiceLineOrderingProvider(TypedDict, total=False):
    address: ClaimInformationServiceLineOrderingProviderAddress

    claim_office_number: Annotated[str, PropertyInfo(alias="claimOfficeNumber")]

    commercial_number: Annotated[str, PropertyInfo(alias="commercialNumber")]

    contact_information: Annotated[
        ClaimInformationServiceLineOrderingProviderContactInformation, PropertyInfo(alias="contactInformation")
    ]

    employer_id: Annotated[str, PropertyInfo(alias="employerId")]

    employer_identification_number: Annotated[str, PropertyInfo(alias="employerIdentificationNumber")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    location_number: Annotated[str, PropertyInfo(alias="locationNumber")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    naic: str

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    other_identifier: Annotated[str, PropertyInfo(alias="otherIdentifier")]

    payer_identification_number: Annotated[str, PropertyInfo(alias="payerIdentificationNumber")]

    provider_type: Annotated[str, PropertyInfo(alias="providerType")]

    provider_upin_number: Annotated[str, PropertyInfo(alias="providerUpinNumber")]

    secondary_identifier: Annotated[
        Iterable[ClaimInformationServiceLineOrderingProviderSecondaryIdentifier],
        PropertyInfo(alias="secondaryIdentifier"),
    ]

    ssn: str

    state_license_number: Annotated[str, PropertyInfo(alias="stateLicenseNumber")]

    suffix: str

    taxonomy_code: Annotated[str, PropertyInfo(alias="taxonomyCode")]


class ClaimInformationServiceLinePurchasedServiceInformation(TypedDict, total=False):
    purchased_service_charge_amount: Required[Annotated[str, PropertyInfo(alias="purchasedServiceChargeAmount")]]

    purchased_service_provider_identifier: Required[
        Annotated[str, PropertyInfo(alias="purchasedServiceProviderIdentifier")]
    ]


class ClaimInformationServiceLinePurchasedServiceProviderAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ClaimInformationServiceLinePurchasedServiceProviderContactInformation(TypedDict, total=False):
    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    name: str

    phone_extension: Annotated[str, PropertyInfo(alias="phoneExtension")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]


class ClaimInformationServiceLinePurchasedServiceProviderSecondaryIdentifier(TypedDict, total=False):
    identifier: Required[str]

    qualifier: Required[str]

    other_identifier: Annotated[str, PropertyInfo(alias="otherIdentifier")]


class ClaimInformationServiceLinePurchasedServiceProvider(TypedDict, total=False):
    address: ClaimInformationServiceLinePurchasedServiceProviderAddress

    claim_office_number: Annotated[str, PropertyInfo(alias="claimOfficeNumber")]

    commercial_number: Annotated[str, PropertyInfo(alias="commercialNumber")]

    contact_information: Annotated[
        ClaimInformationServiceLinePurchasedServiceProviderContactInformation, PropertyInfo(alias="contactInformation")
    ]

    employer_id: Annotated[str, PropertyInfo(alias="employerId")]

    employer_identification_number: Annotated[str, PropertyInfo(alias="employerIdentificationNumber")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    location_number: Annotated[str, PropertyInfo(alias="locationNumber")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    naic: str

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    other_identifier: Annotated[str, PropertyInfo(alias="otherIdentifier")]

    payer_identification_number: Annotated[str, PropertyInfo(alias="payerIdentificationNumber")]

    provider_type: Annotated[str, PropertyInfo(alias="providerType")]

    provider_upin_number: Annotated[str, PropertyInfo(alias="providerUpinNumber")]

    secondary_identifier: Annotated[
        Iterable[ClaimInformationServiceLinePurchasedServiceProviderSecondaryIdentifier],
        PropertyInfo(alias="secondaryIdentifier"),
    ]

    ssn: str

    state_license_number: Annotated[str, PropertyInfo(alias="stateLicenseNumber")]

    suffix: str

    taxonomy_code: Annotated[str, PropertyInfo(alias="taxonomyCode")]


class ClaimInformationServiceLineReferringProviderAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ClaimInformationServiceLineReferringProviderContactInformation(TypedDict, total=False):
    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    name: str

    phone_extension: Annotated[str, PropertyInfo(alias="phoneExtension")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]


class ClaimInformationServiceLineReferringProviderSecondaryIdentifier(TypedDict, total=False):
    identifier: Required[str]

    qualifier: Required[str]

    other_identifier: Annotated[str, PropertyInfo(alias="otherIdentifier")]


class ClaimInformationServiceLineReferringProvider(TypedDict, total=False):
    provider_type: Required[Annotated[str, PropertyInfo(alias="providerType")]]

    address: ClaimInformationServiceLineReferringProviderAddress

    claim_office_number: Annotated[str, PropertyInfo(alias="claimOfficeNumber")]

    commercial_number: Annotated[str, PropertyInfo(alias="commercialNumber")]

    contact_information: Annotated[
        ClaimInformationServiceLineReferringProviderContactInformation, PropertyInfo(alias="contactInformation")
    ]

    employer_id: Annotated[str, PropertyInfo(alias="employerId")]

    employer_identification_number: Annotated[str, PropertyInfo(alias="employerIdentificationNumber")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    location_number: Annotated[str, PropertyInfo(alias="locationNumber")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    naic: str

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    other_identifier: Annotated[str, PropertyInfo(alias="otherIdentifier")]

    payer_identification_number: Annotated[str, PropertyInfo(alias="payerIdentificationNumber")]

    provider_upin_number: Annotated[str, PropertyInfo(alias="providerUpinNumber")]

    secondary_identifier: Annotated[
        Iterable[ClaimInformationServiceLineReferringProviderSecondaryIdentifier],
        PropertyInfo(alias="secondaryIdentifier"),
    ]

    ssn: str

    state_license_number: Annotated[str, PropertyInfo(alias="stateLicenseNumber")]

    suffix: str

    taxonomy_code: Annotated[str, PropertyInfo(alias="taxonomyCode")]


class ClaimInformationServiceLineRenderingProviderAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ClaimInformationServiceLineRenderingProviderContactInformation(TypedDict, total=False):
    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    name: str

    phone_extension: Annotated[str, PropertyInfo(alias="phoneExtension")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]


class ClaimInformationServiceLineRenderingProviderSecondaryIdentifier(TypedDict, total=False):
    identifier: Required[str]

    qualifier: Required[str]

    other_identifier: Annotated[str, PropertyInfo(alias="otherIdentifier")]


class ClaimInformationServiceLineRenderingProvider(TypedDict, total=False):
    provider_type: Required[Annotated[str, PropertyInfo(alias="providerType")]]

    address: ClaimInformationServiceLineRenderingProviderAddress

    claim_office_number: Annotated[str, PropertyInfo(alias="claimOfficeNumber")]

    commercial_number: Annotated[str, PropertyInfo(alias="commercialNumber")]

    contact_information: Annotated[
        ClaimInformationServiceLineRenderingProviderContactInformation, PropertyInfo(alias="contactInformation")
    ]

    employer_id: Annotated[str, PropertyInfo(alias="employerId")]

    employer_identification_number: Annotated[str, PropertyInfo(alias="employerIdentificationNumber")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    location_number: Annotated[str, PropertyInfo(alias="locationNumber")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    naic: str

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    other_identifier: Annotated[str, PropertyInfo(alias="otherIdentifier")]

    payer_identification_number: Annotated[str, PropertyInfo(alias="payerIdentificationNumber")]

    provider_upin_number: Annotated[str, PropertyInfo(alias="providerUpinNumber")]

    secondary_identifier: Annotated[
        Iterable[ClaimInformationServiceLineRenderingProviderSecondaryIdentifier],
        PropertyInfo(alias="secondaryIdentifier"),
    ]

    ssn: str

    state_license_number: Annotated[str, PropertyInfo(alias="stateLicenseNumber")]

    suffix: str

    taxonomy_code: Annotated[str, PropertyInfo(alias="taxonomyCode")]


class ClaimInformationServiceLineServiceFacilityLocationAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ClaimInformationServiceLineServiceFacilityLocationSecondaryIdentifier(TypedDict, total=False):
    identifier: Required[str]

    qualifier: Required[str]

    other_identifier: Annotated[str, PropertyInfo(alias="otherIdentifier")]


class ClaimInformationServiceLineServiceFacilityLocation(TypedDict, total=False):
    address: Required[ClaimInformationServiceLineServiceFacilityLocationAddress]

    organization_name: Required[Annotated[str, PropertyInfo(alias="organizationName")]]

    npi: str

    phone_extension: Annotated[str, PropertyInfo(alias="phoneExtension")]

    phone_name: Annotated[str, PropertyInfo(alias="phoneName")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]

    secondary_identifier: Annotated[
        Iterable[ClaimInformationServiceLineServiceFacilityLocationSecondaryIdentifier],
        PropertyInfo(alias="secondaryIdentifier"),
    ]


class ClaimInformationServiceLineServiceLineDateInformation(TypedDict, total=False):
    begin_therapy_date: Annotated[str, PropertyInfo(alias="beginTherapyDate")]

    certification_revision_or_recertification_date: Annotated[
        str, PropertyInfo(alias="certificationRevisionOrRecertificationDate")
    ]

    hemoglobin_test_date: Annotated[str, PropertyInfo(alias="hemoglobinTestDate")]

    initial_treatment_date: Annotated[str, PropertyInfo(alias="initialTreatmentDate")]

    last_certification_date: Annotated[str, PropertyInfo(alias="lastCertificationDate")]

    last_x_ray_date: Annotated[str, PropertyInfo(alias="lastXRayDate")]

    prescription_date: Annotated[str, PropertyInfo(alias="prescriptionDate")]

    serum_creatine_test_date: Annotated[str, PropertyInfo(alias="serumCreatineTestDate")]

    shipped_date: Annotated[str, PropertyInfo(alias="shippedDate")]

    treatment_or_therapy_date: Annotated[str, PropertyInfo(alias="treatmentOrTherapyDate")]


class ClaimInformationServiceLineServiceLineReferenceInformationPriorAuthorization(TypedDict, total=False):
    prior_authorization_or_referral_number: Required[
        Annotated[str, PropertyInfo(alias="priorAuthorizationOrReferralNumber")]
    ]

    other_payer_primary_identifier: Annotated[str, PropertyInfo(alias="otherPayerPrimaryIdentifier")]


class ClaimInformationServiceLineServiceLineReferenceInformation(TypedDict, total=False):
    adjusted_repriced_line_item_reference_number: Annotated[
        str, PropertyInfo(alias="adjustedRepricedLineItemReferenceNumber")
    ]

    clinical_laboratory_improvement_amendment_number: Annotated[
        str, PropertyInfo(alias="clinicalLaboratoryImprovementAmendmentNumber")
    ]

    immunization_batch_number: Annotated[str, PropertyInfo(alias="immunizationBatchNumber")]

    mammography_certification_number: Annotated[str, PropertyInfo(alias="mammographyCertificationNumber")]

    prior_authorization: Annotated[
        Iterable[ClaimInformationServiceLineServiceLineReferenceInformationPriorAuthorization],
        PropertyInfo(alias="priorAuthorization"),
    ]

    referral_number: Annotated[List[str], PropertyInfo(alias="referralNumber")]

    referring_clia_number: Annotated[str, PropertyInfo(alias="referringCliaNumber")]

    repriced_line_item_reference_number: Annotated[str, PropertyInfo(alias="repricedLineItemReferenceNumber")]


class ClaimInformationServiceLineServiceLineSupplementalInformation(TypedDict, total=False):
    attachment_report_type_code: Required[
        Annotated[
            Literal[
                "03",
                "04",
                "05",
                "06",
                "07",
                "08",
                "09",
                "10",
                "11",
                "13",
                "15",
                "21",
                "A3",
                "A4",
                "AM",
                "AS",
                "B2",
                "B3",
                "B4",
                "BR",
                "BS",
                "BT",
                "CB",
                "CK",
                "CT",
                "D2",
                "DA",
                "DB",
                "DG",
                "DJ",
                "DS",
                "EB",
                "HC",
                "HR",
                "I5",
                "IR",
                "LA",
                "M1",
                "MT",
                "NM",
                "OB",
                "OC",
                "OD",
                "OE",
                "OX",
                "OZ",
                "P4",
                "P5",
                "PE",
                "PN",
                "PO",
                "PQ",
                "PY",
                "PZ",
                "RB",
                "RR",
                "RT",
                "RX",
                "SG",
                "V5",
                "XP",
            ],
            PropertyInfo(alias="attachmentReportTypeCode"),
        ]
    ]

    attachment_transmission_code: Required[
        Annotated[Literal["AA", "BM", "EL", "EM", "FT", "FX"], PropertyInfo(alias="attachmentTransmissionCode")]
    ]

    attachment_control_number: Annotated[str, PropertyInfo(alias="attachmentControlNumber")]


class ClaimInformationServiceLineSupervisingProviderAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ClaimInformationServiceLineSupervisingProviderContactInformation(TypedDict, total=False):
    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    name: str

    phone_extension: Annotated[str, PropertyInfo(alias="phoneExtension")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]


class ClaimInformationServiceLineSupervisingProviderSecondaryIdentifier(TypedDict, total=False):
    identifier: Required[str]

    qualifier: Required[str]

    other_identifier: Annotated[str, PropertyInfo(alias="otherIdentifier")]


class ClaimInformationServiceLineSupervisingProvider(TypedDict, total=False):
    provider_type: Required[Annotated[str, PropertyInfo(alias="providerType")]]

    address: ClaimInformationServiceLineSupervisingProviderAddress

    claim_office_number: Annotated[str, PropertyInfo(alias="claimOfficeNumber")]

    commercial_number: Annotated[str, PropertyInfo(alias="commercialNumber")]

    contact_information: Annotated[
        ClaimInformationServiceLineSupervisingProviderContactInformation, PropertyInfo(alias="contactInformation")
    ]

    employer_id: Annotated[str, PropertyInfo(alias="employerId")]

    employer_identification_number: Annotated[str, PropertyInfo(alias="employerIdentificationNumber")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    location_number: Annotated[str, PropertyInfo(alias="locationNumber")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    naic: str

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    other_identifier: Annotated[str, PropertyInfo(alias="otherIdentifier")]

    payer_identification_number: Annotated[str, PropertyInfo(alias="payerIdentificationNumber")]

    provider_upin_number: Annotated[str, PropertyInfo(alias="providerUpinNumber")]

    secondary_identifier: Annotated[
        Iterable[ClaimInformationServiceLineSupervisingProviderSecondaryIdentifier],
        PropertyInfo(alias="secondaryIdentifier"),
    ]

    ssn: str

    state_license_number: Annotated[str, PropertyInfo(alias="stateLicenseNumber")]

    suffix: str

    taxonomy_code: Annotated[str, PropertyInfo(alias="taxonomyCode")]


class ClaimInformationServiceLineTestResult(TypedDict, total=False):
    measurement_qualifier: Required[
        Annotated[Literal["HT", "R1", "R2", "R3", "R4"], PropertyInfo(alias="measurementQualifier")]
    ]

    measurement_reference_identification_code: Required[
        Annotated[Literal["OG", "TR"], PropertyInfo(alias="measurementReferenceIdentificationCode")]
    ]

    test_results: Required[Annotated[str, PropertyInfo(alias="testResults")]]


class ClaimInformationServiceLine(TypedDict, total=False):
    professional_service: Required[
        Annotated[ClaimInformationServiceLineProfessionalService, PropertyInfo(alias="professionalService")]
    ]

    service_date: Required[Annotated[str, PropertyInfo(alias="serviceDate")]]

    additional_notes: Annotated[str, PropertyInfo(alias="additionalNotes")]

    ambulance_certification: Annotated[
        Iterable[ClaimInformationServiceLineAmbulanceCertification], PropertyInfo(alias="ambulanceCertification")
    ]

    ambulance_drop_off_location: Annotated[
        ClaimInformationServiceLineAmbulanceDropOffLocation, PropertyInfo(alias="ambulanceDropOffLocation")
    ]

    ambulance_patient_count: Annotated[float, PropertyInfo(alias="ambulancePatientCount")]

    ambulance_pick_up_location: Annotated[
        ClaimInformationServiceLineAmbulancePickUpLocation, PropertyInfo(alias="ambulancePickUpLocation")
    ]

    ambulance_transport_information: Annotated[
        ClaimInformationServiceLineAmbulanceTransportInformation, PropertyInfo(alias="ambulanceTransportInformation")
    ]

    assigned_number: Annotated[str, PropertyInfo(alias="assignedNumber")]

    condition_indicator_durable_medical_equipment: Annotated[
        ClaimInformationServiceLineConditionIndicatorDurableMedicalEquipment,
        PropertyInfo(alias="conditionIndicatorDurableMedicalEquipment"),
    ]

    contract_information: Annotated[
        ClaimInformationServiceLineContractInformation, PropertyInfo(alias="contractInformation")
    ]

    drug_identification: Annotated[
        ClaimInformationServiceLineDrugIdentification, PropertyInfo(alias="drugIdentification")
    ]

    durable_medical_equipment_certificate_of_medical_necessity: Annotated[
        ClaimInformationServiceLineDurableMedicalEquipmentCertificateOfMedicalNecessity,
        PropertyInfo(alias="durableMedicalEquipmentCertificateOfMedicalNecessity"),
    ]

    durable_medical_equipment_certification: Annotated[
        ClaimInformationServiceLineDurableMedicalEquipmentCertification,
        PropertyInfo(alias="durableMedicalEquipmentCertification"),
    ]

    durable_medical_equipment_service: Annotated[
        ClaimInformationServiceLineDurableMedicalEquipmentService, PropertyInfo(alias="durableMedicalEquipmentService")
    ]

    file_information: Annotated[List[str], PropertyInfo(alias="fileInformation")]

    form_identification: Annotated[
        Iterable[ClaimInformationServiceLineFormIdentification], PropertyInfo(alias="formIdentification")
    ]

    goal_rehab_or_discharge_plans: Annotated[str, PropertyInfo(alias="goalRehabOrDischargePlans")]

    hospice_employee_indicator: Annotated[bool, PropertyInfo(alias="hospiceEmployeeIndicator")]

    line_adjudication_information: Annotated[
        Iterable[ClaimInformationServiceLineLineAdjudicationInformation],
        PropertyInfo(alias="lineAdjudicationInformation"),
    ]

    line_pricing_repricing_information: Annotated[
        ClaimInformationServiceLineLinePricingRepricingInformation,
        PropertyInfo(alias="linePricingRepricingInformation"),
    ]

    obstetric_anesthesia_additional_units: Annotated[float, PropertyInfo(alias="obstetricAnesthesiaAdditionalUnits")]

    ordering_provider: Annotated[ClaimInformationServiceLineOrderingProvider, PropertyInfo(alias="orderingProvider")]

    postage_tax_amount: Annotated[str, PropertyInfo(alias="postageTaxAmount")]

    purchased_service_information: Annotated[
        ClaimInformationServiceLinePurchasedServiceInformation, PropertyInfo(alias="purchasedServiceInformation")
    ]

    purchased_service_provider: Annotated[
        ClaimInformationServiceLinePurchasedServiceProvider, PropertyInfo(alias="purchasedServiceProvider")
    ]

    referring_provider: Annotated[ClaimInformationServiceLineReferringProvider, PropertyInfo(alias="referringProvider")]

    rendering_provider: Annotated[ClaimInformationServiceLineRenderingProvider, PropertyInfo(alias="renderingProvider")]

    sales_tax_amount: Annotated[str, PropertyInfo(alias="salesTaxAmount")]

    service_date_end: Annotated[str, PropertyInfo(alias="serviceDateEnd")]

    service_facility_location: Annotated[
        ClaimInformationServiceLineServiceFacilityLocation, PropertyInfo(alias="serviceFacilityLocation")
    ]

    service_line_date_information: Annotated[
        ClaimInformationServiceLineServiceLineDateInformation, PropertyInfo(alias="serviceLineDateInformation")
    ]

    service_line_reference_information: Annotated[
        ClaimInformationServiceLineServiceLineReferenceInformation,
        PropertyInfo(alias="serviceLineReferenceInformation"),
    ]

    service_line_supplemental_information: Annotated[
        Iterable[ClaimInformationServiceLineServiceLineSupplementalInformation],
        PropertyInfo(alias="serviceLineSupplementalInformation"),
    ]

    supervising_provider: Annotated[
        ClaimInformationServiceLineSupervisingProvider, PropertyInfo(alias="supervisingProvider")
    ]

    test_results: Annotated[Iterable[ClaimInformationServiceLineTestResult], PropertyInfo(alias="testResults")]

    third_party_organization_notes: Annotated[str, PropertyInfo(alias="thirdPartyOrganizationNotes")]


class ClaimInformationAmbulanceCertification(TypedDict, total=False):
    certification_condition_indicator: Required[
        Annotated[Literal["N", "Y"], PropertyInfo(alias="certificationConditionIndicator")]
    ]

    condition_codes: Required[
        Annotated[List[Literal["01", "04", "05", "06", "07", "08", "09", "12"]], PropertyInfo(alias="conditionCodes")]
    ]


class ClaimInformationAmbulanceDropOffLocation(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ClaimInformationAmbulancePickUpLocation(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ClaimInformationAmbulanceTransportInformation(TypedDict, total=False):
    ambulance_transport_reason_code: Required[
        Annotated[Literal["A", "B", "C", "D", "E"], PropertyInfo(alias="ambulanceTransportReasonCode")]
    ]

    transport_distance_in_miles: Required[Annotated[str, PropertyInfo(alias="transportDistanceInMiles")]]

    patient_weight_in_pounds: Annotated[str, PropertyInfo(alias="patientWeightInPounds")]

    round_trip_purpose_description: Annotated[str, PropertyInfo(alias="roundTripPurposeDescription")]

    stretcher_purpose_description: Annotated[str, PropertyInfo(alias="stretcherPurposeDescription")]


class ClaimInformationClaimContractInformation(TypedDict, total=False):
    contract_type_code: Required[
        Annotated[Literal["01", "02", "03", "04", "05", "06", "09"], PropertyInfo(alias="contractTypeCode")]
    ]

    contract_amount: Annotated[str, PropertyInfo(alias="contractAmount")]

    contract_code: Annotated[str, PropertyInfo(alias="contractCode")]

    contract_percentage: Annotated[str, PropertyInfo(alias="contractPercentage")]

    contract_version_identifier: Annotated[str, PropertyInfo(alias="contractVersionIdentifier")]

    terms_discount_percentage: Annotated[str, PropertyInfo(alias="termsDiscountPercentage")]


class ClaimInformationClaimDateInformation(TypedDict, total=False):
    accident_date: Annotated[str, PropertyInfo(alias="accidentDate")]

    acute_manifestation_date: Annotated[str, PropertyInfo(alias="acuteManifestationDate")]

    admission_date: Annotated[str, PropertyInfo(alias="admissionDate")]

    assumed_and_relinquished_care_begin_date: Annotated[str, PropertyInfo(alias="assumedAndRelinquishedCareBeginDate")]

    assumed_and_relinquished_care_end_date: Annotated[str, PropertyInfo(alias="assumedAndRelinquishedCareEndDate")]

    authorized_return_to_work_date: Annotated[str, PropertyInfo(alias="authorizedReturnToWorkDate")]

    disability_begin_date: Annotated[str, PropertyInfo(alias="disabilityBeginDate")]

    disability_end_date: Annotated[str, PropertyInfo(alias="disabilityEndDate")]

    discharge_date: Annotated[str, PropertyInfo(alias="dischargeDate")]

    first_contact_date: Annotated[str, PropertyInfo(alias="firstContactDate")]

    hearing_and_vision_prescription_date: Annotated[str, PropertyInfo(alias="hearingAndVisionPrescriptionDate")]

    initial_treatment_date: Annotated[str, PropertyInfo(alias="initialTreatmentDate")]

    last_menstrual_period_date: Annotated[str, PropertyInfo(alias="lastMenstrualPeriodDate")]

    last_seen_date: Annotated[str, PropertyInfo(alias="lastSeenDate")]

    last_worked_date: Annotated[str, PropertyInfo(alias="lastWorkedDate")]

    last_x_ray_date: Annotated[str, PropertyInfo(alias="lastXRayDate")]

    repricer_received_date: Annotated[str, PropertyInfo(alias="repricerReceivedDate")]

    symptom_date: Annotated[str, PropertyInfo(alias="symptomDate")]


class ClaimInformationClaimNote(TypedDict, total=False):
    additional_information: Annotated[str, PropertyInfo(alias="additionalInformation")]

    certification_narrative: Annotated[str, PropertyInfo(alias="certificationNarrative")]

    diagnosis_description: Annotated[str, PropertyInfo(alias="diagnosisDescription")]

    goal_rehab_or_discharge_plans: Annotated[str, PropertyInfo(alias="goalRehabOrDischargePlans")]

    third_part_org_notes: Annotated[str, PropertyInfo(alias="thirdPartOrgNotes")]


class ClaimInformationClaimPricingRepricingInformation(TypedDict, total=False):
    pricing_methodology_code: Required[
        Annotated[
            Literal["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14"],
            PropertyInfo(alias="pricingMethodologyCode"),
        ]
    ]

    repriced_allowed_amount: Required[Annotated[str, PropertyInfo(alias="repricedAllowedAmount")]]

    exception_code: Annotated[Literal["1", "2", "3", "4", "5", "6"], PropertyInfo(alias="exceptionCode")]

    policy_compliance_code: Annotated[Literal["1", "2", "3", "4", "5"], PropertyInfo(alias="policyComplianceCode")]

    reject_reason_code: Annotated[Literal["T1", "T2", "T3", "T4", "T5", "T6"], PropertyInfo(alias="rejectReasonCode")]

    repriced_approved_ambulatory_patient_group_amount: Annotated[
        str, PropertyInfo(alias="repricedApprovedAmbulatoryPatientGroupAmount")
    ]

    repriced_approved_ambulatory_patient_group_code: Annotated[
        str, PropertyInfo(alias="repricedApprovedAmbulatoryPatientGroupCode")
    ]

    repriced_saving_amount: Annotated[str, PropertyInfo(alias="repricedSavingAmount")]

    repricing_organization_identifier: Annotated[str, PropertyInfo(alias="repricingOrganizationIdentifier")]

    repricing_per_diem_or_flat_rate_amount: Annotated[str, PropertyInfo(alias="repricingPerDiemOrFlatRateAmount")]


class ClaimInformationClaimSupplementalInformationReportInformation(TypedDict, total=False):
    attachment_report_type_code: Required[
        Annotated[
            Literal[
                "03",
                "04",
                "05",
                "06",
                "07",
                "08",
                "09",
                "10",
                "11",
                "13",
                "15",
                "21",
                "A3",
                "A4",
                "AM",
                "AS",
                "B2",
                "B3",
                "B4",
                "BR",
                "BS",
                "BT",
                "CB",
                "CK",
                "CT",
                "D2",
                "DA",
                "DB",
                "DG",
                "DJ",
                "DS",
                "EB",
                "HC",
                "HR",
                "I5",
                "IR",
                "LA",
                "M1",
                "MT",
                "NM",
                "OB",
                "OC",
                "OD",
                "OE",
                "OX",
                "OZ",
                "P4",
                "P5",
                "PE",
                "PN",
                "PO",
                "PQ",
                "PY",
                "PZ",
                "RB",
                "RR",
                "RT",
                "RX",
                "SG",
                "V5",
                "XP",
            ],
            PropertyInfo(alias="attachmentReportTypeCode"),
        ]
    ]

    attachment_transmission_code: Required[
        Annotated[Literal["AA", "BM", "EL", "EM", "FT", "FX"], PropertyInfo(alias="attachmentTransmissionCode")]
    ]

    attachment_control_number: Annotated[str, PropertyInfo(alias="attachmentControlNumber")]


class ClaimInformationClaimSupplementalInformation(TypedDict, total=False):
    adjusted_repriced_claim_number: Annotated[str, PropertyInfo(alias="adjustedRepricedClaimNumber")]

    care_plan_oversight_number: Annotated[str, PropertyInfo(alias="carePlanOversightNumber")]

    claim_control_number: Annotated[str, PropertyInfo(alias="claimControlNumber")]

    claim_number: Annotated[str, PropertyInfo(alias="claimNumber")]

    clia_number: Annotated[str, PropertyInfo(alias="cliaNumber")]

    demo_project_identifier: Annotated[str, PropertyInfo(alias="demoProjectIdentifier")]

    investigational_device_exemption_number: Annotated[str, PropertyInfo(alias="investigationalDeviceExemptionNumber")]

    mammography_certification_number: Annotated[str, PropertyInfo(alias="mammographyCertificationNumber")]

    medical_record_number: Annotated[str, PropertyInfo(alias="medicalRecordNumber")]

    medicare_crossover_reference_id: Annotated[str, PropertyInfo(alias="medicareCrossoverReferenceId")]

    prior_authorization_number: Annotated[str, PropertyInfo(alias="priorAuthorizationNumber")]

    referral_number: Annotated[str, PropertyInfo(alias="referralNumber")]

    report_information: Annotated[
        ClaimInformationClaimSupplementalInformationReportInformation, PropertyInfo(alias="reportInformation")
    ]

    report_informations: Annotated[
        Iterable[ClaimInformationClaimSupplementalInformationReportInformation],
        PropertyInfo(alias="reportInformations"),
    ]

    repriced_claim_number: Annotated[str, PropertyInfo(alias="repricedClaimNumber")]

    service_authorization_exception_code: Annotated[
        Literal["1", "2", "3", "4", "5", "6", "7"], PropertyInfo(alias="serviceAuthorizationExceptionCode")
    ]


class ClaimInformationConditionInformation(TypedDict, total=False):
    condition_codes: Required[Annotated[List[str], PropertyInfo(alias="conditionCodes")]]


class ClaimInformationEpsdtReferral(TypedDict, total=False):
    certification_condition_code_applies_indicator: Required[
        Annotated[Literal["N", "Y"], PropertyInfo(alias="certificationConditionCodeAppliesIndicator")]
    ]

    condition_codes: Required[Annotated[List[Literal["AV", "NU", "S2", "ST"]], PropertyInfo(alias="conditionCodes")]]


class ClaimInformationOtherSubscriberInformationOtherPayerNameOtherPayerAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ClaimInformationOtherSubscriberInformationOtherPayerNameOtherPayerSecondaryIdentifier(TypedDict, total=False):
    identifier: Required[str]

    qualifier: Required[str]

    other_identifier: Annotated[str, PropertyInfo(alias="otherIdentifier")]


class ClaimInformationOtherSubscriberInformationOtherPayerName(TypedDict, total=False):
    other_payer_identifier: Required[Annotated[str, PropertyInfo(alias="otherPayerIdentifier")]]

    other_payer_identifier_type_code: Required[
        Annotated[Literal["PI", "XV"], PropertyInfo(alias="otherPayerIdentifierTypeCode")]
    ]

    other_payer_organization_name: Required[Annotated[str, PropertyInfo(alias="otherPayerOrganizationName")]]

    other_payer_address: Annotated[
        ClaimInformationOtherSubscriberInformationOtherPayerNameOtherPayerAddress,
        PropertyInfo(alias="otherPayerAddress"),
    ]

    other_payer_adjudication_or_payment_date: Annotated[str, PropertyInfo(alias="otherPayerAdjudicationOrPaymentDate")]

    other_payer_claim_adjustment_indicator: Annotated[bool, PropertyInfo(alias="otherPayerClaimAdjustmentIndicator")]

    other_payer_claim_control_number: Annotated[str, PropertyInfo(alias="otherPayerClaimControlNumber")]

    other_payer_prior_authorization_number: Annotated[str, PropertyInfo(alias="otherPayerPriorAuthorizationNumber")]

    other_payer_prior_authorization_or_referral_number: Annotated[
        str, PropertyInfo(alias="otherPayerPriorAuthorizationOrReferralNumber")
    ]

    other_payer_secondary_identifier: Annotated[
        Iterable[ClaimInformationOtherSubscriberInformationOtherPayerNameOtherPayerSecondaryIdentifier],
        PropertyInfo(alias="otherPayerSecondaryIdentifier"),
    ]


class ClaimInformationOtherSubscriberInformationOtherSubscriberNameOtherInsuredAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ClaimInformationOtherSubscriberInformationOtherSubscriberName(TypedDict, total=False):
    other_insured_identifier: Required[Annotated[str, PropertyInfo(alias="otherInsuredIdentifier")]]

    other_insured_identifier_type_code: Required[
        Annotated[Literal["II", "MI"], PropertyInfo(alias="otherInsuredIdentifierTypeCode")]
    ]

    other_insured_last_name: Required[Annotated[str, PropertyInfo(alias="otherInsuredLastName")]]

    other_insured_qualifier: Required[Annotated[Literal["1", "2"], PropertyInfo(alias="otherInsuredQualifier")]]

    other_insured_additional_identifier: Annotated[str, PropertyInfo(alias="otherInsuredAdditionalIdentifier")]

    other_insured_address: Annotated[
        ClaimInformationOtherSubscriberInformationOtherSubscriberNameOtherInsuredAddress,
        PropertyInfo(alias="otherInsuredAddress"),
    ]

    other_insured_first_name: Annotated[str, PropertyInfo(alias="otherInsuredFirstName")]

    other_insured_middle_name: Annotated[str, PropertyInfo(alias="otherInsuredMiddleName")]

    other_insured_name_suffix: Annotated[str, PropertyInfo(alias="otherInsuredNameSuffix")]


class ClaimInformationOtherSubscriberInformationClaimLevelAdjustmentAdjustmentDetail(TypedDict, total=False):
    adjustment_amount: Required[Annotated[str, PropertyInfo(alias="adjustmentAmount")]]

    adjustment_reason_code: Required[Annotated[str, PropertyInfo(alias="adjustmentReasonCode")]]

    adjustment_quantity: Annotated[str, PropertyInfo(alias="adjustmentQuantity")]


class ClaimInformationOtherSubscriberInformationClaimLevelAdjustment(TypedDict, total=False):
    adjustment_details: Required[
        Annotated[
            Iterable[ClaimInformationOtherSubscriberInformationClaimLevelAdjustmentAdjustmentDetail],
            PropertyInfo(alias="adjustmentDetails"),
        ]
    ]

    adjustment_group_code: Required[
        Annotated[Literal["CO", "CR", "OA", "PI", "PR"], PropertyInfo(alias="adjustmentGroupCode")]
    ]


class ClaimInformationOtherSubscriberInformationMedicareOutpatientAdjudication(TypedDict, total=False):
    claim_payment_remark_code: Annotated[List[str], PropertyInfo(alias="claimPaymentRemarkCode")]

    end_stage_renal_disease_payment_amount: Annotated[str, PropertyInfo(alias="endStageRenalDiseasePaymentAmount")]

    hcpcs_payable_amount: Annotated[str, PropertyInfo(alias="hcpcsPayableAmount")]

    non_payable_professional_component_billed_amount: Annotated[
        str, PropertyInfo(alias="nonPayableProfessionalComponentBilledAmount")
    ]

    reimbursement_rate: Annotated[str, PropertyInfo(alias="reimbursementRate")]


class ClaimInformationOtherSubscriberInformationOtherPayerBillingProviderOtherPayerBillingProviderIdentifier(
    TypedDict, total=False
):
    identifier: Required[str]

    qualifier: Required[str]

    other_identifier: Annotated[str, PropertyInfo(alias="otherIdentifier")]


class ClaimInformationOtherSubscriberInformationOtherPayerBillingProvider(TypedDict, total=False):
    entity_type_qualifier: Required[Annotated[Literal["1", "2"], PropertyInfo(alias="entityTypeQualifier")]]

    other_payer_billing_provider_identifier: Required[
        Annotated[
            Iterable[
                ClaimInformationOtherSubscriberInformationOtherPayerBillingProviderOtherPayerBillingProviderIdentifier
            ],
            PropertyInfo(alias="otherPayerBillingProviderIdentifier"),
        ]
    ]


class ClaimInformationOtherSubscriberInformationOtherPayerReferringProviderOtherPayerReferringProviderIdentifier(
    TypedDict, total=False
):
    identifier: Required[str]

    qualifier: Required[str]

    other_identifier: Annotated[str, PropertyInfo(alias="otherIdentifier")]


class ClaimInformationOtherSubscriberInformationOtherPayerReferringProvider(TypedDict, total=False):
    other_payer_referring_provider_identifier: Required[
        Annotated[
            Iterable[
                ClaimInformationOtherSubscriberInformationOtherPayerReferringProviderOtherPayerReferringProviderIdentifier
            ],
            PropertyInfo(alias="otherPayerReferringProviderIdentifier"),
        ]
    ]


class ClaimInformationOtherSubscriberInformationOtherPayerRenderingProviderOtherPayerRenderingProviderSecondaryIdentifier(
    TypedDict, total=False
):
    identifier: Required[str]

    qualifier: Required[str]

    other_identifier: Annotated[str, PropertyInfo(alias="otherIdentifier")]


class ClaimInformationOtherSubscriberInformationOtherPayerRenderingProvider(TypedDict, total=False):
    entity_type_qualifier: Required[Annotated[Literal["1", "2"], PropertyInfo(alias="entityTypeQualifier")]]

    other_payer_rendering_provider_secondary_identifier: Annotated[
        Iterable[
            ClaimInformationOtherSubscriberInformationOtherPayerRenderingProviderOtherPayerRenderingProviderSecondaryIdentifier
        ],
        PropertyInfo(alias="otherPayerRenderingProviderSecondaryIdentifier"),
    ]


class ClaimInformationOtherSubscriberInformationOtherPayerServiceFacilityLocationOtherPayerServiceFacilityLocationSecondaryIdentifier(
    TypedDict, total=False
):
    identifier: Required[str]

    qualifier: Required[str]

    other_identifier: Annotated[str, PropertyInfo(alias="otherIdentifier")]


class ClaimInformationOtherSubscriberInformationOtherPayerServiceFacilityLocation(TypedDict, total=False):
    other_payer_service_facility_location_secondary_identifier: Required[
        Annotated[
            Iterable[
                ClaimInformationOtherSubscriberInformationOtherPayerServiceFacilityLocationOtherPayerServiceFacilityLocationSecondaryIdentifier
            ],
            PropertyInfo(alias="otherPayerServiceFacilityLocationSecondaryIdentifier"),
        ]
    ]


class ClaimInformationOtherSubscriberInformationOtherPayerSupervisingProviderOtherPayerSupervisingProviderIdentifier(
    TypedDict, total=False
):
    identifier: Required[str]

    qualifier: Required[str]

    other_identifier: Annotated[str, PropertyInfo(alias="otherIdentifier")]


class ClaimInformationOtherSubscriberInformationOtherPayerSupervisingProvider(TypedDict, total=False):
    other_payer_supervising_provider_identifier: Required[
        Annotated[
            Iterable[
                ClaimInformationOtherSubscriberInformationOtherPayerSupervisingProviderOtherPayerSupervisingProviderIdentifier
            ],
            PropertyInfo(alias="otherPayerSupervisingProviderIdentifier"),
        ]
    ]


class ClaimInformationOtherSubscriberInformation(TypedDict, total=False):
    benefits_assignment_certification_indicator: Required[
        Annotated[Literal["N", "W", "Y"], PropertyInfo(alias="benefitsAssignmentCertificationIndicator")]
    ]

    claim_filing_indicator_code: Required[
        Annotated[
            Literal[
                "11",
                "12",
                "13",
                "14",
                "15",
                "16",
                "17",
                "AM",
                "BL",
                "CH",
                "CI",
                "DS",
                "FI",
                "HM",
                "LM",
                "MA",
                "MB",
                "MC",
                "OF",
                "TV",
                "VA",
                "WC",
                "ZZ",
            ],
            PropertyInfo(alias="claimFilingIndicatorCode"),
        ]
    ]

    individual_relationship_code: Required[
        Annotated[
            Literal["01", "18", "19", "20", "21", "39", "40", "53", "G8"],
            PropertyInfo(alias="individualRelationshipCode"),
        ]
    ]

    other_payer_name: Required[
        Annotated[ClaimInformationOtherSubscriberInformationOtherPayerName, PropertyInfo(alias="otherPayerName")]
    ]

    other_subscriber_name: Required[
        Annotated[
            ClaimInformationOtherSubscriberInformationOtherSubscriberName, PropertyInfo(alias="otherSubscriberName")
        ]
    ]

    payment_responsibility_level_code: Required[
        Annotated[
            Literal["A", "B", "C", "D", "E", "F", "G", "H", "P", "S", "T", "U"],
            PropertyInfo(alias="paymentResponsibilityLevelCode"),
        ]
    ]

    release_of_information_code: Required[Annotated[Literal["I", "Y"], PropertyInfo(alias="releaseOfInformationCode")]]

    claim_level_adjustments: Annotated[
        Iterable[ClaimInformationOtherSubscriberInformationClaimLevelAdjustment],
        PropertyInfo(alias="claimLevelAdjustments"),
    ]

    insurance_group_or_policy_number: Annotated[str, PropertyInfo(alias="insuranceGroupOrPolicyNumber")]

    insurance_type_code: Annotated[
        Literal["12", "13", "14", "15", "16", "41", "42", "43", "47"], PropertyInfo(alias="insuranceTypeCode")
    ]

    medicare_outpatient_adjudication: Annotated[
        ClaimInformationOtherSubscriberInformationMedicareOutpatientAdjudication,
        PropertyInfo(alias="medicareOutpatientAdjudication"),
    ]

    non_covered_charge_amount: Annotated[str, PropertyInfo(alias="nonCoveredChargeAmount")]

    other_insured_group_name: Annotated[str, PropertyInfo(alias="otherInsuredGroupName")]

    other_payer_billing_provider: Annotated[
        Iterable[ClaimInformationOtherSubscriberInformationOtherPayerBillingProvider],
        PropertyInfo(alias="otherPayerBillingProvider"),
    ]

    other_payer_referring_provider: Annotated[
        Iterable[ClaimInformationOtherSubscriberInformationOtherPayerReferringProvider],
        PropertyInfo(alias="otherPayerReferringProvider"),
    ]

    other_payer_rendering_provider: Annotated[
        Iterable[ClaimInformationOtherSubscriberInformationOtherPayerRenderingProvider],
        PropertyInfo(alias="otherPayerRenderingProvider"),
    ]

    other_payer_service_facility_location: Annotated[
        Iterable[ClaimInformationOtherSubscriberInformationOtherPayerServiceFacilityLocation],
        PropertyInfo(alias="otherPayerServiceFacilityLocation"),
    ]

    other_payer_supervising_provider: Annotated[
        Iterable[ClaimInformationOtherSubscriberInformationOtherPayerSupervisingProvider],
        PropertyInfo(alias="otherPayerSupervisingProvider"),
    ]

    patient_signature_generated_for_patient: Annotated[bool, PropertyInfo(alias="patientSignatureGeneratedForPatient")]

    payer_paid_amount: Annotated[str, PropertyInfo(alias="payerPaidAmount")]

    remaining_patient_liability: Annotated[str, PropertyInfo(alias="remainingPatientLiability")]


class ClaimInformationPatientConditionInformationVision(TypedDict, total=False):
    certification_condition_indicator: Required[
        Annotated[Literal["N", "Y"], PropertyInfo(alias="certificationConditionIndicator")]
    ]

    code_category: Required[Annotated[Literal["E1", "E2", "E3"], PropertyInfo(alias="codeCategory")]]

    condition_codes: Required[
        Annotated[List[Literal["L1", "L2", "L3", "L4", "L5"]], PropertyInfo(alias="conditionCodes")]
    ]


class ClaimInformationServiceFacilityLocationAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ClaimInformationServiceFacilityLocationSecondaryIdentifier(TypedDict, total=False):
    identifier: Required[str]

    qualifier: Required[str]

    other_identifier: Annotated[str, PropertyInfo(alias="otherIdentifier")]


class ClaimInformationServiceFacilityLocation(TypedDict, total=False):
    address: Required[ClaimInformationServiceFacilityLocationAddress]

    organization_name: Required[Annotated[str, PropertyInfo(alias="organizationName")]]

    npi: str

    phone_extension: Annotated[str, PropertyInfo(alias="phoneExtension")]

    phone_name: Annotated[str, PropertyInfo(alias="phoneName")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]

    secondary_identifier: Annotated[
        Iterable[ClaimInformationServiceFacilityLocationSecondaryIdentifier], PropertyInfo(alias="secondaryIdentifier")
    ]


class ClaimInformationSpinalManipulationServiceInformation(TypedDict, total=False):
    patient_condition_code: Required[Annotated[str, PropertyInfo(alias="patientConditionCode")]]

    patient_condition_description1: Annotated[
        Literal["A", "C", "D", "E", "F", "G", "M"], PropertyInfo(alias="patientConditionDescription1")
    ]

    patient_condition_description2: Annotated[str, PropertyInfo(alias="patientConditionDescription2")]


class ClaimInformation(TypedDict, total=False):
    benefits_assignment_certification_indicator: Required[
        Annotated[Literal["N", "W", "Y"], PropertyInfo(alias="benefitsAssignmentCertificationIndicator")]
    ]

    claim_charge_amount: Required[Annotated[str, PropertyInfo(alias="claimChargeAmount")]]

    claim_filing_code: Required[
        Annotated[
            Literal[
                "11",
                "12",
                "13",
                "14",
                "15",
                "16",
                "17",
                "AM",
                "BL",
                "CH",
                "CI",
                "DS",
                "FI",
                "HM",
                "LM",
                "MA",
                "MB",
                "MC",
                "OF",
                "TV",
                "VA",
                "WC",
                "ZZ",
            ],
            PropertyInfo(alias="claimFilingCode"),
        ]
    ]

    claim_frequency_code: Required[Annotated[Literal["1", "7", "8"], PropertyInfo(alias="claimFrequencyCode")]]

    health_care_code_information: Required[
        Annotated[Iterable[ClaimInformationHealthCareCodeInformation], PropertyInfo(alias="healthCareCodeInformation")]
    ]

    place_of_service_code: Required[
        Annotated[
            Literal[
                "01",
                "02",
                "03",
                "04",
                "05",
                "06",
                "07",
                "08",
                "09",
                "10",
                "11",
                "12",
                "13",
                "14",
                "15",
                "16",
                "17",
                "18",
                "19",
                "20",
                "21",
                "22",
                "23",
                "24",
                "25",
                "26",
                "27",
                "31",
                "32",
                "33",
                "34",
                "41",
                "42",
                "49",
                "50",
                "51",
                "52",
                "53",
                "54",
                "55",
                "56",
                "57",
                "58",
                "60",
                "61",
                "62",
                "65",
                "66",
                "71",
                "72",
                "81",
                "99",
            ],
            PropertyInfo(alias="placeOfServiceCode"),
        ]
    ]

    plan_participation_code: Required[Annotated[Literal["A", "B", "C"], PropertyInfo(alias="planParticipationCode")]]

    release_information_code: Required[Annotated[Literal["I", "Y"], PropertyInfo(alias="releaseInformationCode")]]

    service_lines: Required[Annotated[Iterable[ClaimInformationServiceLine], PropertyInfo(alias="serviceLines")]]

    signature_indicator: Required[Annotated[Literal["N", "Y"], PropertyInfo(alias="signatureIndicator")]]

    ambulance_certification: Annotated[
        Iterable[ClaimInformationAmbulanceCertification], PropertyInfo(alias="ambulanceCertification")
    ]

    ambulance_drop_off_location: Annotated[
        ClaimInformationAmbulanceDropOffLocation, PropertyInfo(alias="ambulanceDropOffLocation")
    ]

    ambulance_pick_up_location: Annotated[
        ClaimInformationAmbulancePickUpLocation, PropertyInfo(alias="ambulancePickUpLocation")
    ]

    ambulance_transport_information: Annotated[
        ClaimInformationAmbulanceTransportInformation, PropertyInfo(alias="ambulanceTransportInformation")
    ]

    anesthesia_related_surgical_procedure: Annotated[
        List[str], PropertyInfo(alias="anesthesiaRelatedSurgicalProcedure")
    ]

    auto_accident_country_code: Annotated[str, PropertyInfo(alias="autoAccidentCountryCode")]

    auto_accident_state_code: Annotated[str, PropertyInfo(alias="autoAccidentStateCode")]

    claim_contract_information: Annotated[
        ClaimInformationClaimContractInformation, PropertyInfo(alias="claimContractInformation")
    ]

    claim_date_information: Annotated[ClaimInformationClaimDateInformation, PropertyInfo(alias="claimDateInformation")]

    claim_note: Annotated[ClaimInformationClaimNote, PropertyInfo(alias="claimNote")]

    claim_pricing_repricing_information: Annotated[
        ClaimInformationClaimPricingRepricingInformation, PropertyInfo(alias="claimPricingRepricingInformation")
    ]

    claim_supplemental_information: Annotated[
        ClaimInformationClaimSupplementalInformation, PropertyInfo(alias="claimSupplementalInformation")
    ]

    condition_information: Annotated[
        Iterable[ClaimInformationConditionInformation], PropertyInfo(alias="conditionInformation")
    ]

    death_date: Annotated[str, PropertyInfo(alias="deathDate")]

    delay_reason_code: Annotated[
        Literal["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "15"], PropertyInfo(alias="delayReasonCode")
    ]

    epsdt_referral: Annotated[ClaimInformationEpsdtReferral, PropertyInfo(alias="epsdtReferral")]

    file_information: Annotated[str, PropertyInfo(alias="fileInformation")]

    file_information_list: Annotated[List[str], PropertyInfo(alias="fileInformationList")]

    homebound_indicator: Annotated[bool, PropertyInfo(alias="homeboundIndicator")]

    other_subscriber_information: Annotated[
        Iterable[ClaimInformationOtherSubscriberInformation], PropertyInfo(alias="otherSubscriberInformation")
    ]

    patient_amount_paid: Annotated[str, PropertyInfo(alias="patientAmountPaid")]

    patient_condition_information_vision: Annotated[
        Iterable[ClaimInformationPatientConditionInformationVision],
        PropertyInfo(alias="patientConditionInformationVision"),
    ]

    patient_signature_source_code: Annotated[bool, PropertyInfo(alias="patientSignatureSourceCode")]

    patient_weight: Annotated[str, PropertyInfo(alias="patientWeight")]

    pregnancy_indicator: Annotated[Literal["Y"], PropertyInfo(alias="pregnancyIndicator")]

    property_casualty_claim_number: Annotated[str, PropertyInfo(alias="propertyCasualtyClaimNumber")]

    related_causes_code: Annotated[List[Literal["AA", "EM", "OA"]], PropertyInfo(alias="relatedCausesCode")]

    service_facility_location: Annotated[
        ClaimInformationServiceFacilityLocation, PropertyInfo(alias="serviceFacilityLocation")
    ]

    special_program_code: Annotated[Literal["02", "03", "05", "09"], PropertyInfo(alias="specialProgramCode")]

    spinal_manipulation_service_information: Annotated[
        ClaimInformationSpinalManipulationServiceInformation, PropertyInfo(alias="spinalManipulationServiceInformation")
    ]


class Receiver(TypedDict, total=False):
    organization_name: Required[Annotated[str, PropertyInfo(alias="organizationName")]]


class SubmitterContactInformation(TypedDict, total=False):
    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    name: str

    phone_extension: Annotated[str, PropertyInfo(alias="phoneExtension")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]


class Submitter(TypedDict, total=False):
    contact_information: Required[Annotated[SubmitterContactInformation, PropertyInfo(alias="contactInformation")]]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    submitter_identification: Annotated[str, PropertyInfo(alias="submitterIdentification")]


class SubscriberAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class SubscriberContactInformation(TypedDict, total=False):
    name: Required[str]

    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    phone_extension: Annotated[str, PropertyInfo(alias="phoneExtension")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]


class Subscriber(TypedDict, total=False):
    address: SubscriberAddress

    contact_information: Annotated[SubscriberContactInformation, PropertyInfo(alias="contactInformation")]

    date_of_birth: Annotated[str, PropertyInfo(alias="dateOfBirth")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    gender: Literal["M", "F", "U"]

    group_number: Annotated[str, PropertyInfo(alias="groupNumber")]

    insurance_type_code: Annotated[
        Literal["12", "13", "14", "15", "16", "41", "42", "43", "47"], PropertyInfo(alias="insuranceTypeCode")
    ]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    member_id: Annotated[str, PropertyInfo(alias="memberId")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    payment_responsibility_level_code: Annotated[
        Literal["A", "B", "C", "D", "E", "F", "G", "H", "P", "S", "T", "U"],
        PropertyInfo(alias="paymentResponsibilityLevelCode"),
    ]

    policy_number: Annotated[str, PropertyInfo(alias="policyNumber")]

    ssn: str

    subscriber_group_name: Annotated[str, PropertyInfo(alias="subscriberGroupName")]

    suffix: str


class DependentAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class DependentContactInformation(TypedDict, total=False):
    name: Required[str]

    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    phone_extension: Annotated[str, PropertyInfo(alias="phoneExtension")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]


class Dependent(TypedDict, total=False):
    date_of_birth: Required[Annotated[str, PropertyInfo(alias="dateOfBirth")]]

    first_name: Required[Annotated[str, PropertyInfo(alias="firstName")]]

    gender: Required[Literal["M", "F", "U"]]

    last_name: Required[Annotated[str, PropertyInfo(alias="lastName")]]

    relationship_to_subscriber_code: Required[
        Annotated[
            Literal["01", "19", "20", "21", "39", "40", "53", "G8"], PropertyInfo(alias="relationshipToSubscriberCode")
        ]
    ]

    address: DependentAddress

    contact_information: Annotated[DependentContactInformation, PropertyInfo(alias="contactInformation")]

    member_id: Annotated[str, PropertyInfo(alias="memberId")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    ssn: str

    suffix: str


class OrderingAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class OrderingContactInformation(TypedDict, total=False):
    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    name: str

    phone_extension: Annotated[str, PropertyInfo(alias="phoneExtension")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]


class Ordering(TypedDict, total=False):
    address: OrderingAddress

    claim_office_number: Annotated[str, PropertyInfo(alias="claimOfficeNumber")]

    commercial_number: Annotated[str, PropertyInfo(alias="commercialNumber")]

    contact_information: Annotated[OrderingContactInformation, PropertyInfo(alias="contactInformation")]

    employer_id: Annotated[str, PropertyInfo(alias="employerId")]

    employer_identification_number: Annotated[str, PropertyInfo(alias="employerIdentificationNumber")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    location_number: Annotated[str, PropertyInfo(alias="locationNumber")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    naic: str

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    payer_identification_number: Annotated[str, PropertyInfo(alias="payerIdentificationNumber")]

    provider_type: Annotated[str, PropertyInfo(alias="providerType")]

    provider_upin_number: Annotated[str, PropertyInfo(alias="providerUpinNumber")]

    ssn: str

    state_license_number: Annotated[str, PropertyInfo(alias="stateLicenseNumber")]

    suffix: str

    taxonomy_code: Annotated[str, PropertyInfo(alias="taxonomyCode")]


class PayerAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class PayToAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class PayToPlanAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class PayToPlan(TypedDict, total=False):
    address: Required[PayToPlanAddress]

    organization_name: Required[Annotated[str, PropertyInfo(alias="organizationName")]]

    primary_identifier: Required[Annotated[str, PropertyInfo(alias="primaryIdentifier")]]

    primary_identifier_type_code: Required[
        Annotated[Literal["PI", "XV"], PropertyInfo(alias="primaryIdentifierTypeCode")]
    ]

    tax_identification_number: Required[Annotated[str, PropertyInfo(alias="taxIdentificationNumber")]]

    secondary_identifier: Annotated[str, PropertyInfo(alias="secondaryIdentifier")]

    secondary_identifier_type_code: Annotated[
        Literal["2U", "FY", "NF"], PropertyInfo(alias="secondaryIdentifierTypeCode")
    ]


class ProviderAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ProviderContactInformation(TypedDict, total=False):
    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    name: str

    phone_extension: Annotated[str, PropertyInfo(alias="phoneExtension")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]


class Provider(TypedDict, total=False):
    address: ProviderAddress

    commercial_number: Annotated[str, PropertyInfo(alias="commercialNumber")]

    contact_information: Annotated[ProviderContactInformation, PropertyInfo(alias="contactInformation")]

    employer_id: Annotated[str, PropertyInfo(alias="employerId")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    location_number: Annotated[str, PropertyInfo(alias="locationNumber")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    provider_type: Annotated[str, PropertyInfo(alias="providerType")]

    provider_upin_number: Annotated[str, PropertyInfo(alias="providerUpinNumber")]

    ssn: str

    state_license_number: Annotated[str, PropertyInfo(alias="stateLicenseNumber")]

    suffix: str

    taxonomy_code: Annotated[str, PropertyInfo(alias="taxonomyCode")]


class ReferringAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class ReferringContactInformation(TypedDict, total=False):
    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    name: str

    phone_extension: Annotated[str, PropertyInfo(alias="phoneExtension")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]


class Referring(TypedDict, total=False):
    address: ReferringAddress

    commercial_number: Annotated[str, PropertyInfo(alias="commercialNumber")]

    contact_information: Annotated[ReferringContactInformation, PropertyInfo(alias="contactInformation")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    provider_type: Annotated[str, PropertyInfo(alias="providerType")]

    provider_upin_number: Annotated[str, PropertyInfo(alias="providerUpinNumber")]

    state_license_number: Annotated[str, PropertyInfo(alias="stateLicenseNumber")]

    suffix: str

    taxonomy_code: Annotated[str, PropertyInfo(alias="taxonomyCode")]


class RenderingAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class RenderingContactInformation(TypedDict, total=False):
    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    name: str

    phone_extension: Annotated[str, PropertyInfo(alias="phoneExtension")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]


class Rendering(TypedDict, total=False):
    address: RenderingAddress

    commercial_number: Annotated[str, PropertyInfo(alias="commercialNumber")]

    contact_information: Annotated[RenderingContactInformation, PropertyInfo(alias="contactInformation")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    location_number: Annotated[str, PropertyInfo(alias="locationNumber")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    provider_type: Annotated[str, PropertyInfo(alias="providerType")]

    provider_upin_number: Annotated[str, PropertyInfo(alias="providerUpinNumber")]

    state_license_number: Annotated[str, PropertyInfo(alias="stateLicenseNumber")]

    suffix: str

    taxonomy_code: Annotated[str, PropertyInfo(alias="taxonomyCode")]


class SupervisingAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    address2: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: str


class SupervisingContactInformation(TypedDict, total=False):
    email: str

    fax_number: Annotated[str, PropertyInfo(alias="faxNumber")]

    name: str

    phone_extension: Annotated[str, PropertyInfo(alias="phoneExtension")]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]


class Supervising(TypedDict, total=False):
    address: SupervisingAddress

    commercial_number: Annotated[str, PropertyInfo(alias="commercialNumber")]

    contact_information: Annotated[SupervisingContactInformation, PropertyInfo(alias="contactInformation")]

    employer_id: Annotated[str, PropertyInfo(alias="employerId")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    location_number: Annotated[str, PropertyInfo(alias="locationNumber")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    npi: str

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]

    provider_type: Annotated[str, PropertyInfo(alias="providerType")]

    provider_upin_number: Annotated[str, PropertyInfo(alias="providerUpinNumber")]

    ssn: str

    state_license_number: Annotated[str, PropertyInfo(alias="stateLicenseNumber")]

    suffix: str

    taxonomy_code: Annotated[str, PropertyInfo(alias="taxonomyCode")]
