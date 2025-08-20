# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = [
    "ClearinghouseCalculatePatientCostParams",
    "EligibilityResponse",
    "EligibilityResponseBenefitsInformation",
    "EligibilityResponseBenefitsInformationAdditionalInformation",
    "EligibilityResponseBenefitsInformationBenefitsAdditionalInformation",
    "EligibilityResponseBenefitsInformationBenefitsDateInformation",
    "EligibilityResponseBenefitsInformationBenefitsDateInformationAdmission",
    "EligibilityResponseBenefitsInformationBenefitsDateInformationDischarge",
    "EligibilityResponseBenefitsInformationBenefitsRelatedEntity",
    "EligibilityResponseBenefitsInformationBenefitsRelatedEntityAddress",
    "EligibilityResponseBenefitsInformationBenefitsRelatedEntityContactInformation",
    "EligibilityResponseBenefitsInformationBenefitsRelatedEntityContactInformationContact",
    "EligibilityResponseBenefitsInformationBenefitsRelatedEntityProviderInformation",
    "EligibilityResponseBenefitsInformationBenefitsServiceDelivery",
    "EligibilityResponseBenefitsInformationCompositeMedicalProcedureIdentifier",
    "EligibilityResponseBenefitsInformationEligibilityAdditionalInformation",
    "EligibilityResponseBenefitsInformationEligibilityAdditionalInformationList",
    "EligibilityResponseDependent",
    "EligibilityResponseDependentAaaError",
    "EligibilityResponseDependentAddress",
    "EligibilityResponseDependentHealthCareDiagnosisCode",
    "EligibilityResponseDependentResponseProvider",
    "EligibilityResponseDependentResponseProviderAaaError",
    "EligibilityResponseDependentResponseProviderAddress",
    "EligibilityResponseError",
    "EligibilityResponseMeta",
    "EligibilityResponsePayer",
    "EligibilityResponsePayerAaaError",
    "EligibilityResponsePayerContactInformation",
    "EligibilityResponsePayerContactInformationContact",
    "EligibilityResponsePlanDateInformation",
    "EligibilityResponsePlanInformation",
    "EligibilityResponsePlanStatus",
    "EligibilityResponseProvider",
    "EligibilityResponseProviderAaaError",
    "EligibilityResponseProviderAddress",
    "EligibilityResponseSubscriber",
    "EligibilityResponseSubscriberAaaError",
    "EligibilityResponseSubscriberAddress",
    "EligibilityResponseSubscriberHealthCareDiagnosisCode",
    "EligibilityResponseSubscriberResponseProvider",
    "EligibilityResponseSubscriberResponseProviderAaaError",
    "EligibilityResponseSubscriberResponseProviderAddress",
    "EligibilityResponseSubscriberTraceNumber",
    "EligibilityResponseWarning",
    "LineItem",
]


class ClearinghouseCalculatePatientCostParams(TypedDict, total=False):
    eligibility_responses: Required[
        Annotated[Iterable[EligibilityResponse], PropertyInfo(alias="eligibilityResponses")]
    ]
    """
    The eligibility responses that the patient has in order of preference (primary,
    secondary, etc.).
    """

    line_items: Required[Annotated[Iterable[LineItem], PropertyInfo(alias="lineItems")]]
    """The line items you are estimating the patient cost for"""


class EligibilityResponseBenefitsInformationAdditionalInformation(TypedDict, total=False):
    description: str


class EligibilityResponseBenefitsInformationBenefitsAdditionalInformation(TypedDict, total=False):
    alternative_list_id: Annotated[str, PropertyInfo(alias="alternativeListId")]

    coverage_list_id: Annotated[str, PropertyInfo(alias="coverageListId")]

    drug_formulary_number: Annotated[str, PropertyInfo(alias="drugFormularyNumber")]

    family_unit_number: Annotated[str, PropertyInfo(alias="familyUnitNumber")]

    group_description: Annotated[str, PropertyInfo(alias="groupDescription")]

    group_number: Annotated[str, PropertyInfo(alias="groupNumber")]

    hic_number: Annotated[str, PropertyInfo(alias="hicNumber")]

    insurance_policy_number: Annotated[str, PropertyInfo(alias="insurancePolicyNumber")]

    medicaid_recepient_id_number: Annotated[str, PropertyInfo(alias="medicaidRecepientIdNumber")]

    medical_assistance_category: Annotated[str, PropertyInfo(alias="medicalAssistanceCategory")]

    member_id: Annotated[str, PropertyInfo(alias="memberId")]

    plan_description: Annotated[str, PropertyInfo(alias="planDescription")]

    plan_network_description: Annotated[str, PropertyInfo(alias="planNetworkDescription")]

    plan_network_id_number: Annotated[str, PropertyInfo(alias="planNetworkIdNumber")]

    plan_number: Annotated[str, PropertyInfo(alias="planNumber")]

    policy_number: Annotated[str, PropertyInfo(alias="policyNumber")]

    prior_authorization_number: Annotated[str, PropertyInfo(alias="priorAuthorizationNumber")]

    referral_number: Annotated[str, PropertyInfo(alias="referralNumber")]


class EligibilityResponseBenefitsInformationBenefitsDateInformationAdmission(TypedDict, total=False):
    date: str

    end_date: Annotated[str, PropertyInfo(alias="endDate")]

    start_date: Annotated[str, PropertyInfo(alias="startDate")]


class EligibilityResponseBenefitsInformationBenefitsDateInformationDischarge(TypedDict, total=False):
    date: str

    end_date: Annotated[str, PropertyInfo(alias="endDate")]

    start_date: Annotated[str, PropertyInfo(alias="startDate")]


class EligibilityResponseBenefitsInformationBenefitsDateInformation(TypedDict, total=False):
    added: str

    admission: str

    admissions: Iterable[EligibilityResponseBenefitsInformationBenefitsDateInformationAdmission]

    benefit: str

    benefit_begin: Annotated[str, PropertyInfo(alias="benefitBegin")]

    benefit_end: Annotated[str, PropertyInfo(alias="benefitEnd")]

    certification: str

    cobra_begin: Annotated[str, PropertyInfo(alias="cobraBegin")]

    cobra_end: Annotated[str, PropertyInfo(alias="cobraEnd")]

    completion: str

    coordination_of_benefits: Annotated[str, PropertyInfo(alias="coordinationOfBenefits")]

    date_of_death: Annotated[str, PropertyInfo(alias="dateOfDeath")]

    date_of_last_update: Annotated[str, PropertyInfo(alias="dateOfLastUpdate")]

    discharge: str

    discharges: Iterable[EligibilityResponseBenefitsInformationBenefitsDateInformationDischarge]

    effective_date_of_change: Annotated[str, PropertyInfo(alias="effectiveDateOfChange")]

    eligibility: str

    eligibility_begin: Annotated[str, PropertyInfo(alias="eligibilityBegin")]

    eligibility_end: Annotated[str, PropertyInfo(alias="eligibilityEnd")]

    enrollment: str

    issue: str

    latest_visit_or_consultation: Annotated[str, PropertyInfo(alias="latestVisitOrConsultation")]

    period_end: Annotated[str, PropertyInfo(alias="periodEnd")]

    period_start: Annotated[str, PropertyInfo(alias="periodStart")]

    plan: str

    plan_begin: Annotated[str, PropertyInfo(alias="planBegin")]

    plan_end: Annotated[str, PropertyInfo(alias="planEnd")]

    policy_effective: Annotated[str, PropertyInfo(alias="policyEffective")]

    policy_expiration: Annotated[str, PropertyInfo(alias="policyExpiration")]

    premium_paidto_date_begin: Annotated[str, PropertyInfo(alias="premiumPaidtoDateBegin")]

    premium_paid_to_date_end: Annotated[str, PropertyInfo(alias="premiumPaidToDateEnd")]

    primary_care_provider: Annotated[str, PropertyInfo(alias="primaryCareProvider")]

    service: str

    status: str


class EligibilityResponseBenefitsInformationBenefitsRelatedEntityAddress(TypedDict, total=False):
    address1: str

    address2: str

    city: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: Literal[
        "NL",
        "PE",
        "NS",
        "NB",
        "QC",
        "ON",
        "MB",
        "SK",
        "AB",
        "BC",
        "YT",
        "NT",
        "NU",
        "DC",
        "AS",
        "GU",
        "MP",
        "PR",
        "UM",
        "VI",
        "AK",
        "AL",
        "AR",
        "AZ",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "IA",
        "ID",
        "IL",
        "IN",
        "KS",
        "KY",
        "LA",
        "MA",
        "MD",
        "ME",
        "MI",
        "MN",
        "MO",
        "MS",
        "MT",
        "NC",
        "ND",
        "NE",
        "NH",
        "NJ",
        "NM",
        "NV",
        "NY",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VA",
        "VT",
        "WA",
        "WI",
        "WV",
        "WY",
    ]


class EligibilityResponseBenefitsInformationBenefitsRelatedEntityContactInformationContact(TypedDict, total=False):
    communication_mode: Annotated[
        Literal[
            "Electronic Data Interchange Access Number",
            "Electronic Mail",
            "Facsimile",
            "Telephone",
            "Uniform Resource Locator (URL)",
        ],
        PropertyInfo(alias="communicationMode"),
    ]

    communication_number: Annotated[str, PropertyInfo(alias="communicationNumber")]


class EligibilityResponseBenefitsInformationBenefitsRelatedEntityContactInformation(TypedDict, total=False):
    contacts: Iterable[EligibilityResponseBenefitsInformationBenefitsRelatedEntityContactInformationContact]

    name: str


class EligibilityResponseBenefitsInformationBenefitsRelatedEntityProviderInformation(TypedDict, total=False):
    provider_code: Annotated[
        Literal[
            "AD", "AT", "BI", "CO", "CV", "H", "HH", "LA", "OT", "P1", "P2", "PC", "PE", "R", "RF", "SB", "SK", "SU"
        ],
        PropertyInfo(alias="providerCode"),
    ]

    reference_identification: Annotated[str, PropertyInfo(alias="referenceIdentification")]


class EligibilityResponseBenefitsInformationBenefitsRelatedEntity(TypedDict, total=False):
    address: EligibilityResponseBenefitsInformationBenefitsRelatedEntityAddress

    contact_information: Annotated[
        EligibilityResponseBenefitsInformationBenefitsRelatedEntityContactInformation,
        PropertyInfo(alias="contactInformation"),
    ]

    entity_firstname: Annotated[str, PropertyInfo(alias="entityFirstname")]

    entity_identification: Annotated[
        Literal["24", "34", "46", "FA", "FI", "II", "MI", "NI", "PI", "PP", "SV", "XV", "XX"],
        PropertyInfo(alias="entityIdentification"),
    ]

    entity_identification_value: Annotated[str, PropertyInfo(alias="entityIdentificationValue")]

    entity_identifier: Annotated[
        Literal[
            "Contracted Service Provider",
            "Preferred Provider Organization (PPO)",
            "Provider",
            "Third-Party Administrator",
            "Employer",
            "Other Physician",
            "Facility",
            "Gateway Provider",
            "Group",
            "Independent Physicians Association (IPA)",
            "Insured or Subscriber",
            "Legal Representative",
            "Origin Carrier",
            "Primary Care Provider",
            "Prior Insurance Carrier",
            "Plan Sponsor",
            "Payer",
            "Primary Payer",
            "Secondary Payer",
            "Tertiary Payer",
            "Party Performing Verification",
            "Vendor",
            "Organization Completing Configuration Change",
            "Utilization Management Organization",
            "Managed Care Organization",
        ],
        PropertyInfo(alias="entityIdentifier"),
    ]

    entity_middlename: Annotated[str, PropertyInfo(alias="entityMiddlename")]

    entity_name: Annotated[str, PropertyInfo(alias="entityName")]

    entity_relationship: Annotated[
        Literal["01", "02", "27", "41", "48", "65", "72"], PropertyInfo(alias="entityRelationship")
    ]

    entity_suffix: Annotated[str, PropertyInfo(alias="entitySuffix")]

    entity_type: Annotated[Literal["Person", "Non-Person Entity"], PropertyInfo(alias="entityType")]

    provider_information: Annotated[
        EligibilityResponseBenefitsInformationBenefitsRelatedEntityProviderInformation,
        PropertyInfo(alias="providerInformation"),
    ]


class EligibilityResponseBenefitsInformationBenefitsServiceDelivery(TypedDict, total=False):
    delivery_or_calendar_pattern_code: Annotated[
        Literal[
            "1st Week of the Month",
            "2nd Week of the Month",
            "3rd Week of the Month",
            "4th Week of the Month",
            "5th Week of the Month",
            "1st & 3rd Week of the Month",
            "2nd & 4th Week of the Month",
            "1st Working Day of Period",
            "Last Working Day of Period",
            "Monday through Friday",
            "Monday through Saturday",
            "Monday through Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
            "Monday through Thursday",
            "Immediately",
            "As Directed",
            "Daily Mon. Through Fri.",
            "1/2 Mon. & 1/2 Tues.",
            "1/2 Tues. & 1/2 Thurs.",
            "1/2 Wed. & 1/2 Fri.",
            "Once Anytime Mon. through Fri.",
            "Tuesday through Friday",
            "Monday, Tuesday and Thursday",
            "Monday, Tuesday and Friday",
            "Wednesday and Thursday",
            "Monday, Wednesday and Thursday",
            "Tuesday, Thursday and Friday",
            "1/2 Tues. & 1/2 Fri.",
            "1/2 Mon. & 1/2 Wed.",
            "1/3 Mon., 1/3 Wed., 1/3 Fri.",
            "Whenever Necessary",
            "1/2 By Wed. Bal. By Fri.",
            "None (Also Used to Cancel or Override a Previous Pattern)",
        ],
        PropertyInfo(alias="deliveryOrCalendarPatternCode"),
    ]

    delivery_or_calendar_pattern_qualifier: Annotated[
        Literal[
            "1st Week of the Month",
            "2nd Week of the Month",
            "3rd Week of the Month",
            "4th Week of the Month",
            "5th Week of the Month",
            "1st & 3rd Week of the Month",
            "2nd & 4th Week of the Month",
            "1st Working Day of Period",
            "Last Working Day of Period",
            "Monday through Friday",
            "Monday through Saturday",
            "Monday through Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
            "Monday through Thursday",
            "Immediately",
            "As Directed",
            "Daily Mon. Through Fri.",
            "1/2 Mon. & 1/2 Tues.",
            "1/2 Tues. & 1/2 Thurs.",
            "1/2 Wed. & 1/2 Fri.",
            "Once Anytime Mon. through Fri.",
            "Tuesday through Friday",
            "Monday, Tuesday and Thursday",
            "Monday, Tuesday and Friday",
            "Wednesday and Thursday",
            "Monday, Wednesday and Thursday",
            "Tuesday, Thursday and Friday",
            "1/2 Tues. & 1/2 Fri.",
            "1/2 Mon. & 1/2 Wed.",
            "1/3 Mon., 1/3 Wed., 1/3 Fri.",
            "Whenever Necessary",
            "1/2 By Wed. Bal. By Fri.",
            "None (Also Used to Cancel or Override a Previous Pattern)",
        ],
        PropertyInfo(alias="deliveryOrCalendarPatternQualifier"),
    ]

    delivery_or_calendar_pattern_qualifier_code: Annotated[
        Literal[
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "SG",
            "SL",
            "SP",
            "SX",
            "SY",
            "SZ",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
        ],
        PropertyInfo(alias="deliveryOrCalendarPatternQualifierCode"),
    ]

    delivery_pattern_time_code: Annotated[
        Literal[
            "1st Shift (Normal Working Hours)",
            "2nd Shift",
            "3rd Shift",
            "A.M.",
            "P.M.",
            "As Directed",
            "Any Shift",
            "None (Also Used to Cancel or Override a Previous Pattern)",
        ],
        PropertyInfo(alias="deliveryPatternTimeCode"),
    ]

    delivery_pattern_time_qualifier: Annotated[
        Literal[
            "1st Shift (Normal Working Hours)",
            "2nd Shift",
            "3rd Shift",
            "A.M.",
            "P.M.",
            "As Directed",
            "Any Shift",
            "None (Also Used to Cancel or Override a Previous Pattern)",
        ],
        PropertyInfo(alias="deliveryPatternTimeQualifier"),
    ]

    delivery_pattern_time_qualifier_code: Annotated[
        Literal["A", "B", "C", "D", "E", "F", "G", "Y"], PropertyInfo(alias="deliveryPatternTimeQualifierCode")
    ]

    num_of_periods: Annotated[str, PropertyInfo(alias="numOfPeriods")]

    quantity: str

    quantity_qualifier: Annotated[
        Literal["Days", "Units", "Hours", "Month", "Visits"], PropertyInfo(alias="quantityQualifier")
    ]

    quantity_qualifier_code: Annotated[
        Literal["DY", "FL", "HS", "MN", "VS"], PropertyInfo(alias="quantityQualifierCode")
    ]

    sample_selection_modulus: Annotated[str, PropertyInfo(alias="sampleSelectionModulus")]

    time_period_qualifier: Annotated[
        Literal[
            "Hour",
            "Day",
            "Years",
            "Service Year",
            "Calendar Year",
            "Year to Date",
            "Contract",
            "Episode",
            "Visit",
            "Outlier",
            "Remaining",
            "Exceeded",
            "Not Exceeded",
            "Lifetime",
            "Lifetime Remaining",
            "Month",
            "Week",
        ],
        PropertyInfo(alias="timePeriodQualifier"),
    ]

    time_period_qualifier_code: Annotated[
        Literal["6", "7", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35"],
        PropertyInfo(alias="timePeriodQualifierCode"),
    ]

    unit_for_measurement_code: Annotated[
        Literal["Days", "Months", "Visits", "Week", "Years"], PropertyInfo(alias="unitForMeasurementCode")
    ]

    unit_for_measurement_qualifier: Annotated[
        Literal["Days", "Months", "Visits", "Week", "Years"], PropertyInfo(alias="unitForMeasurementQualifier")
    ]

    unit_for_measurement_qualifier_code: Annotated[
        Literal["DA", "MO", "VS", "WK", "YR"], PropertyInfo(alias="unitForMeasurementQualifierCode")
    ]


class EligibilityResponseBenefitsInformationCompositeMedicalProcedureIdentifier(TypedDict, total=False):
    diagnosis_code_pointer: Annotated[List[str], PropertyInfo(alias="diagnosisCodePointer")]

    procedure_code: Annotated[str, PropertyInfo(alias="procedureCode")]

    procedure_modifiers: Annotated[List[str], PropertyInfo(alias="procedureModifiers")]

    product_or_service_id: Annotated[str, PropertyInfo(alias="productOrServiceID")]

    product_or_service_id_qualifier: Annotated[str, PropertyInfo(alias="productOrServiceIdQualifier")]

    product_or_service_id_qualifier_code: Annotated[str, PropertyInfo(alias="productOrServiceIdQualifierCode")]


class EligibilityResponseBenefitsInformationEligibilityAdditionalInformation(TypedDict, total=False):
    code_category: Annotated[Literal["44"], PropertyInfo(alias="codeCategory")]

    code_list_qualifier: Annotated[str, PropertyInfo(alias="codeListQualifier")]

    code_list_qualifier_code: Annotated[Literal["GR", "NI", "ZZ"], PropertyInfo(alias="codeListQualifierCode")]

    industry: str

    industry_code: Annotated[str, PropertyInfo(alias="industryCode")]

    injured_body_part_name: Annotated[str, PropertyInfo(alias="injuredBodyPartName")]


class EligibilityResponseBenefitsInformationEligibilityAdditionalInformationList(TypedDict, total=False):
    code_category: Annotated[Literal["44"], PropertyInfo(alias="codeCategory")]

    code_list_qualifier: Annotated[str, PropertyInfo(alias="codeListQualifier")]

    code_list_qualifier_code: Annotated[Literal["GR", "NI", "ZZ"], PropertyInfo(alias="codeListQualifierCode")]

    industry: str

    industry_code: Annotated[str, PropertyInfo(alias="industryCode")]

    injured_body_part_name: Annotated[str, PropertyInfo(alias="injuredBodyPartName")]


class EligibilityResponseBenefitsInformation(TypedDict, total=False):
    additional_information: Annotated[
        Iterable[EligibilityResponseBenefitsInformationAdditionalInformation],
        PropertyInfo(alias="additionalInformation"),
    ]

    auth_or_cert_indicator: Annotated[Literal["N", "U", "Y"], PropertyInfo(alias="authOrCertIndicator")]

    benefit_amount: Annotated[str, PropertyInfo(alias="benefitAmount")]

    benefit_percent: Annotated[str, PropertyInfo(alias="benefitPercent")]

    benefit_quantity: Annotated[str, PropertyInfo(alias="benefitQuantity")]

    benefits_additional_information: Annotated[
        EligibilityResponseBenefitsInformationBenefitsAdditionalInformation,
        PropertyInfo(alias="benefitsAdditionalInformation"),
    ]

    benefits_date_information: Annotated[
        EligibilityResponseBenefitsInformationBenefitsDateInformation, PropertyInfo(alias="benefitsDateInformation")
    ]

    benefits_related_entities: Annotated[
        Iterable[EligibilityResponseBenefitsInformationBenefitsRelatedEntity],
        PropertyInfo(alias="benefitsRelatedEntities"),
    ]

    benefits_related_entity: Annotated[
        EligibilityResponseBenefitsInformationBenefitsRelatedEntity, PropertyInfo(alias="benefitsRelatedEntity")
    ]

    benefits_service_delivery: Annotated[
        Iterable[EligibilityResponseBenefitsInformationBenefitsServiceDelivery],
        PropertyInfo(alias="benefitsServiceDelivery"),
    ]

    code: Literal[
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "A",
        "B",
        "C",
        "CB",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "MC",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
    ]

    composite_medical_procedure_identifier: Annotated[
        EligibilityResponseBenefitsInformationCompositeMedicalProcedureIdentifier,
        PropertyInfo(alias="compositeMedicalProcedureIdentifier"),
    ]

    coverage_level: Annotated[
        Literal[
            "Children Only",
            "Dependents Only",
            "Employee and Children",
            "Employee Only",
            "Employee and Spouse",
            "Family",
            "Individual",
            "Spouse and Children",
            "Spouse Only",
        ],
        PropertyInfo(alias="coverageLevel"),
    ]

    coverage_level_code: Annotated[
        Literal["CHD", "DEP", "ECH", "EMP", "ESP", "FAM", "IND", "SPC", "SPO"], PropertyInfo(alias="coverageLevelCode")
    ]

    eligibility_additional_information: Annotated[
        EligibilityResponseBenefitsInformationEligibilityAdditionalInformation,
        PropertyInfo(alias="eligibilityAdditionalInformation"),
    ]

    eligibility_additional_information_list: Annotated[
        Iterable[EligibilityResponseBenefitsInformationEligibilityAdditionalInformationList],
        PropertyInfo(alias="eligibilityAdditionalInformationList"),
    ]

    header_loop_identifier_code: Annotated[str, PropertyInfo(alias="headerLoopIdentifierCode")]

    in_plan_network_indicator: Annotated[
        Literal["Yes", "No", "Unknown", "Not Applicable"], PropertyInfo(alias="inPlanNetworkIndicator")
    ]

    in_plan_network_indicator_code: Annotated[
        Literal["Y", "N", "U", "W"], PropertyInfo(alias="inPlanNetworkIndicatorCode")
    ]

    insurance_type: Annotated[
        Literal[
            "Medicare Secondary Working Aged Beneficiary or Spouse with Employer Group Health Plan",
            "Medicare Secondary End-Stage Renal Disease Beneficiary in the Mandated Coordination Period with an Employer's Group Health Plan",
            "Medicare Secondary, No-fault Insurance including Auto is Primary",
            "Medicare Secondary Worker's Compensation",
            "Medicare Secondary Public Health Service (PHS)or Other Federal Agency",
            "Medicare Secondary Black Lung",
            "Medicare Secondary Veteran's Administration",
            "Medicare Secondary Disabled Beneficiary Under Age 65 with Large Group Health Plan (LGHP)",
            "Medicare Secondary, Other Liability Insurance is Primary",
            "Auto Insurance Policy",
            "Commercial",
            "Consolidated Omnibus Budget Reconciliation Act (COBRA)",
            "Medicare Conditionally Primary",
            "Disability",
            "Disability Benefits",
            "Exclusive Provider Organization",
            "Family or Friends",
            "Group Policy",
            "Health Maintenance Organization (HMO)",
            "Health Maintenance Organization (HMO) - Medicare Risk",
            "Special Low Income Medicare Beneficiary",
            "Indemnity",
            "Individual Policy",
            "Long Term Care",
            "Long Term Policy",
            "Life Insurance",
            "Litigation",
            "Medicare Part A",
            "Medicare Part B",
            "Medicaid",
            "Medigap Part A",
            "Medigap Part B",
            "Medicare Primary",
            "Other",
            "Property Insurance - Personal",
            "Personal",
            "Personal Payment (Cash - No Insurance)",
            "Preferred Provider Organization (PPO)",
            "Point of Service (POS)",
            "Qualified Medicare Beneficiary",
            "Property Insurance - Real",
            "Supplemental Policy",
            "Tax Equity Fiscal Responsibility Act (TEFRA)",
            "Workers Compensation",
            "Wrap Up Policy",
        ],
        PropertyInfo(alias="insuranceType"),
    ]

    insurance_type_code: Annotated[
        Literal[
            "12",
            "13",
            "14",
            "15",
            "16",
            "41",
            "42",
            "43",
            "47",
            "AP",
            "C1",
            "CO",
            "CP",
            "D",
            "DB",
            "EP",
            "FF",
            "GP",
            "HM",
            "HN",
            "HS",
            "IN",
            "IP",
            "LC",
            "LD",
            "LI",
            "LT",
            "MA",
            "MB",
            "MC",
            "MH",
            "MI",
            "MP",
            "OT",
            "PE",
            "PL",
            "PP",
            "PR",
            "PS",
            "QM",
            "RP",
            "SP",
            "TF",
            "WC",
            "WU",
        ],
        PropertyInfo(alias="insuranceTypeCode"),
    ]

    name: Literal[
        "Active Coverage",
        "Active - Full Risk Capitation",
        "Active - Services Capitated",
        "Active - Services Capitated to Primary Care Physician",
        "Active - Pending Investigation",
        "Inactive",
        "Inactive - Pending Eligibility Update",
        "Inactive - Pending Investigation",
        "Co-Insurance",
        "Co-Payment",
        "Deductible",
        "Coverage Basis",
        "Benefit Description",
        "Exclusions",
        "Limitations",
        "Out of Pocket (Stop Loss)",
        "Unlimited",
        "Non-Covered",
        "Cost Containment",
        "Reserve",
        "Primary Care Provider",
        "Pre-existing Condition",
        "Managed Care Coordinator",
        "Services Restricted to Following Provider",
        "Not Deemed a Medical Necessity",
        "Benefit Disclaimer",
        "Second Surgical Opinion Required",
        "Other or Additional Payor",
        "Prior Year(s) History",
        "Card(s) Reported Lost/Stolen",
        "Contact Following Entity for Eligibility or Benefit Information",
        "Cannot Process",
        "Other Source of Data",
        "Health Care Facility",
        "Spend Down",
    ]

    plan_coverage: Annotated[str, PropertyInfo(alias="planCoverage")]

    quantity_qualifier: Annotated[
        Literal[
            "Minimum",
            "Quantity Used",
            "Covered - Actual",
            "Covered - Estimated",
            "Number of Co-insurance Days",
            "Deductible Blood Units",
            "Days",
            "Hours",
            "Life-time Reserve - Actual",
            "Life-time Reserve - Estimated",
            "Maximum",
            "Month",
            "Number of Services or Procedures",
            "Quantity Approved",
            "Age, High Value",
            "Age, Low Value",
            "Visits",
            "Years",
        ],
        PropertyInfo(alias="quantityQualifier"),
    ]

    quantity_qualifier_code: Annotated[
        Literal[
            "8H", "99", "CA", "CE", "D3", "DB", "DY", "HS", "LA", "LE", "M2", "MN", "P6", "QA", "S7", "S8", "VS", "YY"
        ],
        PropertyInfo(alias="quantityQualifierCode"),
    ]

    service_type_codes: Annotated[
        List[
            Literal[
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
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
                "28",
                "30",
                "32",
                "33",
                "34",
                "35",
                "36",
                "37",
                "38",
                "39",
                "40",
                "41",
                "42",
                "43",
                "44",
                "45",
                "46",
                "47",
                "48",
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
                "59",
                "60",
                "61",
                "62",
                "63",
                "64",
                "65",
                "66",
                "67",
                "68",
                "69",
                "70",
                "71",
                "72",
                "73",
                "74",
                "75",
                "76",
                "77",
                "78",
                "79",
                "80",
                "81",
                "82",
                "83",
                "84",
                "85",
                "86",
                "87",
                "88",
                "89",
                "90",
                "91",
                "92",
                "93",
                "94",
                "95",
                "96",
                "97",
                "98",
                "99",
                "A0",
                "A1",
                "A2",
                "A3",
                "A4",
                "A5",
                "A6",
                "A7",
                "A8",
                "A9",
                "AA",
                "AB",
                "AC",
                "AD",
                "AE",
                "AF",
                "AG",
                "AH",
                "AI",
                "AJ",
                "AK",
                "AL",
                "AM",
                "AN",
                "AO",
                "AQ",
                "AR",
                "B1",
                "B2",
                "B3",
                "BA",
                "BB",
                "BC",
                "BD",
                "BE",
                "BF",
                "BG",
                "BH",
                "BI",
                "BJ",
                "BK",
                "BL",
                "BM",
                "BN",
                "BP",
                "BQ",
                "BR",
                "BS",
                "BT",
                "BU",
                "BV",
                "BW",
                "BX",
                "BY",
                "BZ",
                "C1",
                "CA",
                "CB",
                "CC",
                "CD",
                "CE",
                "CF",
                "CG",
                "CH",
                "CI",
                "CJ",
                "CK",
                "CL",
                "CM",
                "CN",
                "CO",
                "CP",
                "CQ",
                "DG",
                "DM",
                "DS",
                "GF",
                "GN",
                "GY",
                "IC",
                "MH",
                "NI",
                "ON",
                "PT",
                "PU",
                "RN",
                "RT",
                "TC",
                "TN",
                "UC",
            ]
        ],
        PropertyInfo(alias="serviceTypeCodes"),
    ]

    service_types: Annotated[
        List[
            Literal[
                "Medical Care",
                "Surgical",
                "Consultation",
                "Diagnostic X-Ray",
                "Diagnostic Lab",
                "Radiation Therapy",
                "Anesthesia",
                "Surgical Assistance",
                "Other Medical",
                "Blood Charges",
                "Used Durable Medical Equipment",
                "Durable Medical Equipment Purchase",
                "Ambulatory Service Center Facility",
                "Renal Supplies in the Home",
                "Alternate Method Dialysis",
                "Chronic Renal Disease (CRD) Equipment",
                "Pre-Admission Testing",
                "Durable Medical Equipment Rental",
                "Pneumonia Vaccine",
                "Second Surgical Opinion",
                "Third Surgical Opinion",
                "Social Work",
                "Diagnostic Dental",
                "Periodontics",
                "Restorative",
                "Endodontics",
                "Maxillofacial Prosthetics",
                "Adjunctive Dental Services",
                "Health Benefit Plan Coverage",
                "Plan Waiting Period",
                "Chiropractic",
                "Chiropractic Office Visits",
                "Dental Care",
                "Dental Crowns",
                "Dental Accident",
                "Orthodontics",
                "Prosthodontics",
                "Oral Surgery",
                "Routine (Preventive) Dental",
                "Home Health Care",
                "Home Health Prescriptions",
                "Home Health Visits",
                "Hospice",
                "Respite Care",
                "Hospital",
                "Hospital - Inpatient",
                "Hospital - Room and Board",
                "Hospital - Outpatient",
                "Hospital - Emergency Accident",
                "Hospital - Emergency Medical",
                "Hospital - Ambulatory Surgical",
                "Long Term Care",
                "Major Medical",
                "Medically Related Transportation",
                "Air Transportation",
                "Cabulance",
                "Licensed Ambulance",
                "General Benefits",
                "In-vitro Fertilization",
                "MRI/CAT Scan",
                "Donor Procedures",
                "Acupuncture",
                "Newborn Care",
                "Pathology",
                "Smoking Cessation",
                "Well Baby Care",
                "Maternity",
                "Transplants",
                "Audiology Exam",
                "Inhalation Therapy",
                "Diagnostic Medical",
                "Private Duty Nursing",
                "Prosthetic Device",
                "Dialysis",
                "Otological Exam",
                "Chemotherapy",
                "Allergy Testing",
                "Immunizations",
                "Routine Physical",
                "Family Planning",
                "Infertility",
                "Abortion",
                "AIDS",
                "Emergency Services",
                "Cancer",
                "Pharmacy",
                "Free Standing Prescription Drug",
                "Mail Order Prescription Drug",
                "Brand Name Prescription Drug",
                "Generic Prescription Drug",
                "Podiatry",
                "Podiatry - Office Visits",
                "Podiatry - Nursing Home Visits",
                "Professional (Physician)",
                "Anesthesiologist",
                "Professional (Physician) Visit - Office",
                "Professional (Physician) Visit - Inpatient",
                "Professional (Physician) Visit - Outpatient",
                "Professional (Physician) Visit - Nursing Home",
                "Professional (Physician) Visit - Skilled Nursing Facility",
                "Professional (Physician) Visit - Home",
                "Psychiatric",
                "Psychiatric - Room and Board",
                "Psychotherapy",
                "Psychiatric - Inpatient",
                "Psychiatric - Outpatient",
                "Rehabilitation",
                "Rehabilitation - Room and Board",
                "Rehabilitation - Inpatient",
                "Rehabilitation - Outpatient",
                "Occupational Therapy",
                "Physical Medicine",
                "Speech Therapy",
                "Skilled Nursing Care",
                "Skilled Nursing Care - Room and Board",
                "Substance Abuse",
                "Alcoholism",
                "Drug Addiction",
                "Vision (Optometry)",
                "Frames",
                "Routine Exam",
                "Lenses",
                "Nonmedically Necessary Physical",
                "Experimental Drug Therapy",
                "Burn Care",
                "Brand Name Prescription Drug - Formulary",
                "Brand Name Prescription Drug - Non-Formulary",
                "Independent Medical Evaluation",
                "Partial Hospitalization (Psychiatric)",
                "Day Care (Psychiatric)",
                "Cognitive Therapy",
                "Massage Therapy",
                "Pulmonary Rehabilitation",
                "Cardiac Rehabilitation",
                "Pediatric",
                "Nursery",
                "Skin",
                "Orthopedic",
                "Cardiac",
                "Lymphatic",
                "Gastrointestinal",
                "Endocrine",
                "Neurology",
                "Eye",
                "Invasive Procedures",
                "Gynecological",
                "Obstetrical",
                "Obstetrical/Gynecological",
                "Mail Order Prescription Drug - Formulary",
                "Mail Order Prescription Drug - Non-Formulary",
                "Physician Visit - Office: Sick",
                "Physician Visit - Office: Well",
                "Coronary Care",
                "Private Duty Nursing - Inpatient",
                "Private Duty Nursing - Home",
                "Surgical Benefits - Professional (Physician)",
                "Surgical Benefits - Facility",
                "Mental Health Provider- Inpatient",
                "Mental Health Provider - Outpatient",
                "Mental Health Facility - Inpatient",
                "Mental Health Facility - Outpatient",
                "Substance Abuse Facility - Inpatient",
                "Substance Abuse Facility - Outpatient",
                "Screening X-ray",
                "Screening laboratory",
                "Mammogram, High Risk Patient",
                "Mammogram, Low Risk Patient",
                "Flu Vaccination",
                "Eyewear and Eyewear Accessories",
                "Case Management",
                "Dermatology",
                "Durable Medical Equipment",
                "Diabetic Supplies",
                "Generic Prescription Drug - Formulary",
                "Generic Prescription Drug - Non-Formulary",
                "Allergy",
                "Intensive Care",
                "Mental Health",
                "Neonatol Intensive Care",
                "Oncology",
                "Physical Therapy",
                "Pulmonary",
                "Renal",
                "Residential Psychiatric Treatment",
                "Transitional Care",
                "Transitional Nursery Care",
                "Urgent Care",
            ]
        ],
        PropertyInfo(alias="serviceTypes"),
    ]

    time_qualifier: Annotated[
        Literal[
            "Hour",
            "Day",
            "24 Hours",
            "Years",
            "Service Year",
            "Calendar Year",
            "Year to Date",
            "Contract",
            "Episode",
            "Visit",
            "Outlier",
            "Remaining",
            "Exceeded",
            "Not Exceeded",
            "Lifetime",
            "Lifetime Remaining",
            "Month",
            "Week",
            "Admission",
        ],
        PropertyInfo(alias="timeQualifier"),
    ]

    time_qualifier_code: Annotated[
        Literal[
            "6",
            "7",
            "13",
            "21",
            "22",
            "23",
            "24",
            "25",
            "26",
            "27",
            "28",
            "29",
            "30",
            "31",
            "32",
            "33",
            "34",
            "35",
            "36",
        ],
        PropertyInfo(alias="timeQualifierCode"),
    ]

    trailer_loop_identifier_code: Annotated[str, PropertyInfo(alias="trailerLoopIdentifierCode")]


class EligibilityResponseDependentAaaError(TypedDict, total=False):
    code: Literal[
        "15",
        "33",
        "35",
        "42",
        "43",
        "45",
        "47",
        "48",
        "49",
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
        "63",
        "64",
        "65",
        "66",
        "67",
        "68",
        "69",
        "70",
        "71",
        "77",
        "98",
        "AA",
        "AE",
        "AF",
        "AG",
        "AO",
        "CI",
        "E8",
        "IA",
        "MA",
    ]

    description: str

    field: str

    followup_action: Annotated[
        Literal[
            "Please Correct and Resubmit",
            "Resubmission Not Allowed",
            "Resubmission Allowed",
            "Do Not Resubmit; Inquiry Initiated to a Third Party",
            "Please Wait 30 Days and Resubmit",
            "Please Wait 10 Days and Resubmit",
            "Do Not Resubmit; We Will Hold Your Request and Respond Again Shortly",
        ],
        PropertyInfo(alias="followupAction"),
    ]

    location: str

    possible_resolutions: Annotated[str, PropertyInfo(alias="possibleResolutions")]


class EligibilityResponseDependentAddress(TypedDict, total=False):
    address1: str

    address2: str

    city: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: Literal[
        "NL",
        "PE",
        "NS",
        "NB",
        "QC",
        "ON",
        "MB",
        "SK",
        "AB",
        "BC",
        "YT",
        "NT",
        "NU",
        "DC",
        "AS",
        "GU",
        "MP",
        "PR",
        "UM",
        "VI",
        "AK",
        "AL",
        "AR",
        "AZ",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "IA",
        "ID",
        "IL",
        "IN",
        "KS",
        "KY",
        "LA",
        "MA",
        "MD",
        "ME",
        "MI",
        "MN",
        "MO",
        "MS",
        "MT",
        "NC",
        "ND",
        "NE",
        "NH",
        "NJ",
        "NM",
        "NV",
        "NY",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VA",
        "VT",
        "WA",
        "WI",
        "WV",
        "WY",
    ]


class EligibilityResponseDependentHealthCareDiagnosisCode(TypedDict, total=False):
    diagnosis_code: Annotated[str, PropertyInfo(alias="diagnosisCode")]

    diagnosis_type_code: Annotated[str, PropertyInfo(alias="diagnosisTypeCode")]


class EligibilityResponseDependentResponseProviderAaaError(TypedDict, total=False):
    code: Literal["15", "41", "43", "44", "45", "46", "47", "48", "50", "51", "79", "97", "T4"]

    description: str

    field: str

    followup_action: Annotated[
        Literal[
            "Please Correct and Resubmit",
            "Resubmission Not Allowed",
            "Resubmission Allowed",
            "Do Not Resubmit; Inquiry Initiated to a Third Party",
            "Please Wait 30 Days and Resubmit",
            "Please Wait 10 Days and Resubmit",
            "Do Not Resubmit; We Will Hold Your Request and Respond Again Shortly",
        ],
        PropertyInfo(alias="followupAction"),
    ]

    location: str

    possible_resolutions: Annotated[str, PropertyInfo(alias="possibleResolutions")]


class EligibilityResponseDependentResponseProviderAddress(TypedDict, total=False):
    address1: str

    address2: str

    city: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: Literal[
        "NL",
        "PE",
        "NS",
        "NB",
        "QC",
        "ON",
        "MB",
        "SK",
        "AB",
        "BC",
        "YT",
        "NT",
        "NU",
        "DC",
        "AS",
        "GU",
        "MP",
        "PR",
        "UM",
        "VI",
        "AK",
        "AL",
        "AR",
        "AZ",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "IA",
        "ID",
        "IL",
        "IN",
        "KS",
        "KY",
        "LA",
        "MA",
        "MD",
        "ME",
        "MI",
        "MN",
        "MO",
        "MS",
        "MT",
        "NC",
        "ND",
        "NE",
        "NH",
        "NJ",
        "NM",
        "NV",
        "NY",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VA",
        "VT",
        "WA",
        "WI",
        "WV",
        "WY",
    ]


class EligibilityResponseDependentResponseProvider(TypedDict, total=False):
    aaa_errors: Annotated[
        Iterable[EligibilityResponseDependentResponseProviderAaaError], PropertyInfo(alias="aaaErrors")
    ]

    address: EligibilityResponseDependentResponseProviderAddress

    employers_id: Annotated[str, PropertyInfo(alias="employersId")]

    entity_identifier: Annotated[
        Literal[
            "Provider",
            "Third-Party Administrator",
            "Employer",
            "Hospital",
            "Facility",
            "Gateway Provider",
            "Plan Sponsor",
            "Payer",
        ],
        PropertyInfo(alias="entityIdentifier"),
    ]

    entity_type: Annotated[Literal["Person", "Non-Person Entity"], PropertyInfo(alias="entityType")]

    federal_taxpayers_id_number: Annotated[str, PropertyInfo(alias="federalTaxpayersIdNumber")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    npi: str

    payor_identification: Annotated[str, PropertyInfo(alias="payorIdentification")]

    pharmacy_processor_number: Annotated[str, PropertyInfo(alias="pharmacyProcessorNumber")]

    provider_code: Annotated[
        Literal[
            "AD", "AT", "BI", "CO", "CV", "H", "HH", "LA", "OT", "P1", "P2", "PC", "PE", "R", "RF", "SB", "SK", "SU"
        ],
        PropertyInfo(alias="providerCode"),
    ]

    provider_first_name: Annotated[str, PropertyInfo(alias="providerFirstName")]

    provider_name: Annotated[str, PropertyInfo(alias="providerName")]

    provider_org_name: Annotated[str, PropertyInfo(alias="providerOrgName")]

    reference_identification: Annotated[str, PropertyInfo(alias="referenceIdentification")]

    service_provider_number: Annotated[str, PropertyInfo(alias="serviceProviderNumber")]

    services_plan_id: Annotated[str, PropertyInfo(alias="servicesPlanID")]

    ssn: str

    suffix: str


class EligibilityResponseDependent(TypedDict, total=False):
    aaa_errors: Annotated[Iterable[EligibilityResponseDependentAaaError], PropertyInfo(alias="aaaErrors")]

    address: EligibilityResponseDependentAddress

    birth_sequence_number: Annotated[str, PropertyInfo(alias="birthSequenceNumber")]

    date_of_birth: Annotated[str, PropertyInfo(alias="dateOfBirth")]

    date_time_period: Annotated[str, PropertyInfo(alias="dateTimePeriod")]

    date_time_period_format_qualifier: Annotated[
        Literal["D8", "RD8"], PropertyInfo(alias="dateTimePeriodFormatQualifier")
    ]

    description: str

    employment_status_code: Annotated[
        Literal["AE", "AO", "AS", "AT", "AU", "CC", "DD", "HD", "IR", "LX", "PE", "RE", "RM", "RR", "RU"],
        PropertyInfo(alias="employmentStatusCode"),
    ]

    end_date_time_period: Annotated[str, PropertyInfo(alias="endDateTimePeriod")]

    entity_identifier: Annotated[Literal["Dependent"], PropertyInfo(alias="entityIdentifier")]

    entity_type: Annotated[Literal["Person", "Non-Person Entity"], PropertyInfo(alias="entityType")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    gender: Literal["M", "F", "U"]

    government_service_affiliation_code: Annotated[
        Literal["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "Q", "R", "S", "U", "W"],
        PropertyInfo(alias="governmentServiceAffiliationCode"),
    ]

    group_description: Annotated[str, PropertyInfo(alias="groupDescription")]

    group_number: Annotated[str, PropertyInfo(alias="groupNumber")]

    health_care_diagnosis_codes: Annotated[
        Iterable[EligibilityResponseDependentHealthCareDiagnosisCode], PropertyInfo(alias="healthCareDiagnosisCodes")
    ]

    information_status_code: Annotated[
        Literal["A", "C", "L", "O", "P", "S", "T"], PropertyInfo(alias="informationStatusCode")
    ]

    insured_indicator: Annotated[Literal["N"], PropertyInfo(alias="insuredIndicator")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    maintenance_reason_code: Annotated[Literal["25"], PropertyInfo(alias="maintenanceReasonCode")]

    maintenance_type_code: Annotated[Literal["001"], PropertyInfo(alias="maintenanceTypeCode")]

    member_id: Annotated[str, PropertyInfo(alias="memberId")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    military_service_rank_code: Annotated[
        Literal[
            "A1",
            "A2",
            "A3",
            "B1",
            "B2",
            "C1",
            "C2",
            "C3",
            "C4",
            "C5",
            "C6",
            "C7",
            "C8",
            "C9",
            "E1",
            "F1",
            "F2",
            "F3",
            "F4",
            "G1",
            "G4",
            "L1",
            "L2",
            "L3",
            "L4",
            "L5",
            "L6",
            "M1",
            "M2",
            "M3",
            "M4",
            "M5",
            "M6",
            "P1",
            "P2",
            "P3",
            "P4",
            "P5",
            "R1",
            "R2",
            "S1",
            "S2",
            "S3",
            "S4",
            "S5",
            "S6",
            "S7",
            "S8",
            "S9",
            "SA",
            "SB",
            "SC",
            "T1",
            "V1",
            "W1",
        ],
        PropertyInfo(alias="militaryServiceRankCode"),
    ]

    plan_description: Annotated[str, PropertyInfo(alias="planDescription")]

    plan_network_description: Annotated[str, PropertyInfo(alias="planNetworkDescription")]

    plan_network_id_number: Annotated[str, PropertyInfo(alias="planNetworkIdNumber")]

    plan_number: Annotated[str, PropertyInfo(alias="planNumber")]

    relation_to_subscriber: Annotated[
        Literal[
            "Spouse",
            "Child",
            "Employee",
            "Unknown",
            "Organ Donor",
            "Cadaver Donor",
            "Life Partner",
            "Other Relationship",
        ],
        PropertyInfo(alias="relationToSubscriber"),
    ]

    relation_to_subscriber_code: Annotated[
        Literal["01", "19", "20", "21", "39", "40", "53", "G8", "Unknown"],
        PropertyInfo(alias="relationToSubscriberCode"),
    ]

    response_provider: Annotated[EligibilityResponseDependentResponseProvider, PropertyInfo(alias="responseProvider")]

    ssn: str

    start_date_time_period: Annotated[str, PropertyInfo(alias="startDateTimePeriod")]

    suffix: str

    unique_health_identifier: Annotated[str, PropertyInfo(alias="uniqueHealthIdentifier")]


class EligibilityResponseError(TypedDict, total=False):
    code: Literal[
        "04",
        "15",
        "33",
        "35",
        "41",
        "42",
        "43",
        "44",
        "45",
        "46",
        "47",
        "48",
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
        "63",
        "64",
        "65",
        "66",
        "67",
        "68",
        "69",
        "70",
        "71",
        "72",
        "73",
        "74",
        "75",
        "76",
        "77",
        "78",
        "79",
        "80",
        "97",
        "98",
        "AA",
        "AE",
        "AF",
        "AG",
        "AO",
        "CI",
        "E8",
        "IA",
        "MA",
        "T4",
    ]

    description: str

    field: str

    followup_action: Annotated[
        Literal[
            "Please Correct and Resubmit",
            "Resubmission Not Allowed",
            "Please Resubmit Original Transaction",
            "Resubmission Allowed",
            "Do Not Resubmit; Inquiry Initiated to a Third Party",
            "Please Wait 30 Days and Resubmit",
            "Please Wait 10 Days and Resubmit",
            "Do Not Resubmit; We Will Hold Your Request and Respond Again Shortly",
        ],
        PropertyInfo(alias="followupAction"),
    ]

    location: str

    possible_resolutions: Annotated[str, PropertyInfo(alias="possibleResolutions")]


class EligibilityResponseMeta(TypedDict, total=False):
    application_mode: Annotated[Literal["production", "test", "information"], PropertyInfo(alias="applicationMode")]

    biller_id: Annotated[str, PropertyInfo(alias="billerId")]

    outbound_trace_id: Annotated[str, PropertyInfo(alias="outboundTraceId")]

    sender_id: Annotated[str, PropertyInfo(alias="senderId")]

    submitter_id: Annotated[str, PropertyInfo(alias="submitterId")]

    trace_id: Annotated[str, PropertyInfo(alias="traceId")]


class EligibilityResponsePayerAaaError(TypedDict, total=False):
    code: Literal["04", "41", "42", "79", "80", "T4"]

    description: str

    field: str

    followup_action: Annotated[
        Literal[
            "Please Correct and Resubmit",
            "Resubmission Not Allowed",
            "Please Resubmit Original Transaction",
            "Resubmission Allowed",
            "Do Not Resubmit; Inquiry Initiated to a Third Party",
            "Please Wait 30 Days and Resubmit",
            "Please Wait 10 Days and Resubmit",
            "Do Not Resubmit; We Will Hold Your Request and Respond Again Shortly",
        ],
        PropertyInfo(alias="followupAction"),
    ]

    location: str

    possible_resolutions: Annotated[str, PropertyInfo(alias="possibleResolutions")]


class EligibilityResponsePayerContactInformationContact(TypedDict, total=False):
    communication_mode: Annotated[
        Literal[
            "Electronic Data Interchange Access Number",
            "Electronic Mail",
            "Facsimile",
            "Telephone",
            "Uniform Resource Locator (URL)",
        ],
        PropertyInfo(alias="communicationMode"),
    ]

    communication_number: Annotated[str, PropertyInfo(alias="communicationNumber")]


class EligibilityResponsePayerContactInformation(TypedDict, total=False):
    contacts: Iterable[EligibilityResponsePayerContactInformationContact]

    name: str


class EligibilityResponsePayer(TypedDict, total=False):
    aaa_errors: Annotated[Iterable[EligibilityResponsePayerAaaError], PropertyInfo(alias="aaaErrors")]

    centers_for_medicare_and_medicaid_plan_id: Annotated[str, PropertyInfo(alias="centersForMedicareAndMedicaidPlanId")]

    contact_information: Annotated[EligibilityResponsePayerContactInformation, PropertyInfo(alias="contactInformation")]

    employers_id: Annotated[str, PropertyInfo(alias="employersId")]

    entity_identifier: Annotated[
        Literal["Third-Party Administrator", "Employer", "Gateway Provider", "Plan Sponsor", "Payer"],
        PropertyInfo(alias="entityIdentifier"),
    ]

    entity_type: Annotated[Literal["Person", "Non-Person Entity"], PropertyInfo(alias="entityType")]

    etin: str

    federal_taxpayers_id_number: Annotated[str, PropertyInfo(alias="federalTaxpayersIdNumber")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    naic: str

    name: str

    npi: str

    payor_identification: Annotated[str, PropertyInfo(alias="payorIdentification")]

    suffix: str


class EligibilityResponsePlanDateInformation(TypedDict, total=False):
    added: str

    admission: str

    benefit: str

    benefit_begin: Annotated[str, PropertyInfo(alias="benefitBegin")]

    benefit_end: Annotated[str, PropertyInfo(alias="benefitEnd")]

    certification: str

    cobra_begin: Annotated[str, PropertyInfo(alias="cobraBegin")]

    cobra_end: Annotated[str, PropertyInfo(alias="cobraEnd")]

    completion: str

    coordination_of_benefits: Annotated[str, PropertyInfo(alias="coordinationOfBenefits")]

    date_of_death: Annotated[str, PropertyInfo(alias="dateOfDeath")]

    date_of_last_update: Annotated[str, PropertyInfo(alias="dateOfLastUpdate")]

    discharge: str

    effective_date_of_change: Annotated[str, PropertyInfo(alias="effectiveDateOfChange")]

    eligibility: str

    eligibility_begin: Annotated[str, PropertyInfo(alias="eligibilityBegin")]

    eligibility_end: Annotated[str, PropertyInfo(alias="eligibilityEnd")]

    enrollment: str

    issue: str

    latest_visit_or_consultation: Annotated[str, PropertyInfo(alias="latestVisitOrConsultation")]

    period_end: Annotated[str, PropertyInfo(alias="periodEnd")]

    period_start: Annotated[str, PropertyInfo(alias="periodStart")]

    plan: str

    plan_begin: Annotated[str, PropertyInfo(alias="planBegin")]

    plan_end: Annotated[str, PropertyInfo(alias="planEnd")]

    policy_effective: Annotated[str, PropertyInfo(alias="policyEffective")]

    policy_expiration: Annotated[str, PropertyInfo(alias="policyExpiration")]

    premium_paid_to_date_begin: Annotated[str, PropertyInfo(alias="premiumPaidToDateBegin")]

    premium_paid_to_date_end: Annotated[str, PropertyInfo(alias="premiumPaidToDateEnd")]

    primary_care_provider: Annotated[str, PropertyInfo(alias="primaryCareProvider")]

    service: str

    status: str


class EligibilityResponsePlanInformation(TypedDict, total=False):
    agency_claim_number: Annotated[str, PropertyInfo(alias="agencyClaimNumber")]

    alternative_list_id: Annotated[str, PropertyInfo(alias="alternativeListId")]

    case_number: Annotated[str, PropertyInfo(alias="caseNumber")]

    centers_for_medicare_and_medicaid_services_npi: Annotated[
        str, PropertyInfo(alias="centersForMedicareAndMedicaidServicesNPI")
    ]

    class_of_contract_code: Annotated[str, PropertyInfo(alias="classOfContractCode")]

    contract_number: Annotated[str, PropertyInfo(alias="contractNumber")]

    coverage_list_id: Annotated[str, PropertyInfo(alias="coverageListId")]

    drug_formulary_number: Annotated[str, PropertyInfo(alias="drugFormularyNumber")]

    electronic_device_pin: Annotated[str, PropertyInfo(alias="electronicDevicePin")]

    eligibility_category: Annotated[str, PropertyInfo(alias="eligibilityCategory")]

    facility_id_number: Annotated[str, PropertyInfo(alias="facilityIdNumber")]

    facility_network_identification_number: Annotated[str, PropertyInfo(alias="facilityNetworkIdentificationNumber")]

    family_unit_number: Annotated[str, PropertyInfo(alias="familyUnitNumber")]

    federal_taxpayers_identification_number: Annotated[str, PropertyInfo(alias="federalTaxpayersIdentificationNumber")]

    group_description: Annotated[str, PropertyInfo(alias="groupDescription")]

    group_number: Annotated[str, PropertyInfo(alias="groupNumber")]

    hic_number: Annotated[str, PropertyInfo(alias="hicNumber")]

    id_card_number: Annotated[str, PropertyInfo(alias="idCardNumber")]

    id_card_serial_number: Annotated[str, PropertyInfo(alias="idCardSerialNumber")]

    insurance_policy_number: Annotated[str, PropertyInfo(alias="insurancePolicyNumber")]

    issue_number: Annotated[str, PropertyInfo(alias="issueNumber")]

    medicaid_provider_number: Annotated[str, PropertyInfo(alias="medicaidProviderNumber")]

    medicaid_recipient_id_number: Annotated[str, PropertyInfo(alias="medicaidRecipientIdNumber")]

    medical_assistance_category: Annotated[str, PropertyInfo(alias="medicalAssistanceCategory")]

    medical_record_identification_number: Annotated[str, PropertyInfo(alias="medicalRecordIdentificationNumber")]

    medicare_provider_number: Annotated[str, PropertyInfo(alias="medicareProviderNumber")]

    member_id: Annotated[str, PropertyInfo(alias="memberId")]

    patient_account_number: Annotated[str, PropertyInfo(alias="patientAccountNumber")]

    personal_identification_number: Annotated[str, PropertyInfo(alias="personalIdentificationNumber")]

    plan_description: Annotated[str, PropertyInfo(alias="planDescription")]

    plan_network_id_description: Annotated[str, PropertyInfo(alias="planNetworkIdDescription")]

    plan_network_id_number: Annotated[str, PropertyInfo(alias="planNetworkIdNumber")]

    plan_number: Annotated[str, PropertyInfo(alias="planNumber")]

    policy_number: Annotated[str, PropertyInfo(alias="policyNumber")]

    prior_authorization_number: Annotated[str, PropertyInfo(alias="priorAuthorizationNumber")]

    prior_id_number: Annotated[str, PropertyInfo(alias="priorIdNumber")]

    referral_number: Annotated[str, PropertyInfo(alias="referralNumber")]

    social_security_number: Annotated[str, PropertyInfo(alias="socialSecurityNumber")]

    state_license_number: Annotated[str, PropertyInfo(alias="stateLicenseNumber")]

    submitter_identification_number: Annotated[str, PropertyInfo(alias="submitterIdentificationNumber")]

    user_identification: Annotated[str, PropertyInfo(alias="userIdentification")]


class EligibilityResponsePlanStatus(TypedDict, total=False):
    plan_details: Annotated[str, PropertyInfo(alias="planDetails")]

    service_type_codes: Annotated[
        List[
            Literal[
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
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
                "28",
                "30",
                "32",
                "33",
                "34",
                "35",
                "36",
                "37",
                "38",
                "39",
                "40",
                "41",
                "42",
                "43",
                "44",
                "45",
                "46",
                "47",
                "48",
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
                "59",
                "60",
                "61",
                "62",
                "63",
                "64",
                "65",
                "66",
                "67",
                "68",
                "69",
                "70",
                "71",
                "72",
                "73",
                "74",
                "75",
                "76",
                "77",
                "78",
                "79",
                "80",
                "81",
                "82",
                "83",
                "84",
                "85",
                "86",
                "87",
                "88",
                "89",
                "90",
                "91",
                "92",
                "93",
                "94",
                "95",
                "96",
                "97",
                "98",
                "99",
                "A0",
                "A1",
                "A2",
                "A3",
                "A4",
                "A5",
                "A6",
                "A7",
                "A8",
                "A9",
                "AA",
                "AB",
                "AC",
                "AD",
                "AE",
                "AF",
                "AG",
                "AH",
                "AI",
                "AJ",
                "AK",
                "AL",
                "AM",
                "AN",
                "AO",
                "AQ",
                "AR",
                "B1",
                "B2",
                "B3",
                "BA",
                "BB",
                "BC",
                "BD",
                "BE",
                "BF",
                "BG",
                "BH",
                "BI",
                "BJ",
                "BK",
                "BL",
                "BM",
                "BN",
                "BP",
                "BQ",
                "BR",
                "BS",
                "BT",
                "BU",
                "BV",
                "BW",
                "BX",
                "BY",
                "BZ",
                "C1",
                "CA",
                "CB",
                "CC",
                "CD",
                "CE",
                "CF",
                "CG",
                "CH",
                "CI",
                "CJ",
                "CK",
                "CL",
                "CM",
                "CN",
                "CO",
                "CP",
                "CQ",
                "DG",
                "DM",
                "DS",
                "GF",
                "GN",
                "GY",
                "IC",
                "MH",
                "NI",
                "ON",
                "PT",
                "PU",
                "RN",
                "RT",
                "TC",
                "TN",
                "UC",
            ]
        ],
        PropertyInfo(alias="serviceTypeCodes"),
    ]

    status: str

    status_code: Annotated[str, PropertyInfo(alias="statusCode")]


class EligibilityResponseProviderAaaError(TypedDict, total=False):
    code: Literal["15", "41", "43", "44", "45", "46", "47", "48", "50", "51", "79", "97", "T4"]

    description: str

    field: str

    followup_action: Annotated[
        Literal[
            "Please Correct and Resubmit",
            "Resubmission Not Allowed",
            "Resubmission Allowed",
            "Do Not Resubmit; Inquiry Initiated to a Third Party",
            "Please Wait 30 Days and Resubmit",
            "Please Wait 10 Days and Resubmit",
            "Do Not Resubmit; We Will Hold Your Request and Respond Again Shortly",
        ],
        PropertyInfo(alias="followupAction"),
    ]

    location: str

    possible_resolutions: Annotated[str, PropertyInfo(alias="possibleResolutions")]


class EligibilityResponseProviderAddress(TypedDict, total=False):
    address1: str

    address2: str

    city: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: Literal[
        "NL",
        "PE",
        "NS",
        "NB",
        "QC",
        "ON",
        "MB",
        "SK",
        "AB",
        "BC",
        "YT",
        "NT",
        "NU",
        "DC",
        "AS",
        "GU",
        "MP",
        "PR",
        "UM",
        "VI",
        "AK",
        "AL",
        "AR",
        "AZ",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "IA",
        "ID",
        "IL",
        "IN",
        "KS",
        "KY",
        "LA",
        "MA",
        "MD",
        "ME",
        "MI",
        "MN",
        "MO",
        "MS",
        "MT",
        "NC",
        "ND",
        "NE",
        "NH",
        "NJ",
        "NM",
        "NV",
        "NY",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VA",
        "VT",
        "WA",
        "WI",
        "WV",
        "WY",
    ]


class EligibilityResponseProvider(TypedDict, total=False):
    aaa_errors: Annotated[Iterable[EligibilityResponseProviderAaaError], PropertyInfo(alias="aaaErrors")]

    address: EligibilityResponseProviderAddress

    employers_id: Annotated[str, PropertyInfo(alias="employersId")]

    entity_identifier: Annotated[
        Literal[
            "Provider",
            "Third-Party Administrator",
            "Employer",
            "Hospital",
            "Facility",
            "Gateway Provider",
            "Plan Sponsor",
            "Payer",
        ],
        PropertyInfo(alias="entityIdentifier"),
    ]

    entity_type: Annotated[Literal["Person", "Non-Person Entity"], PropertyInfo(alias="entityType")]

    federal_taxpayers_id_number: Annotated[str, PropertyInfo(alias="federalTaxpayersIdNumber")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    npi: str

    payor_identification: Annotated[str, PropertyInfo(alias="payorIdentification")]

    pharmacy_processor_number: Annotated[str, PropertyInfo(alias="pharmacyProcessorNumber")]

    provider_code: Annotated[
        Literal[
            "AD", "AT", "BI", "CO", "CV", "H", "HH", "LA", "OT", "P1", "P2", "PC", "PE", "R", "RF", "SB", "SK", "SU"
        ],
        PropertyInfo(alias="providerCode"),
    ]

    provider_first_name: Annotated[str, PropertyInfo(alias="providerFirstName")]

    provider_name: Annotated[str, PropertyInfo(alias="providerName")]

    provider_org_name: Annotated[str, PropertyInfo(alias="providerOrgName")]

    reference_identification: Annotated[str, PropertyInfo(alias="referenceIdentification")]

    service_provider_number: Annotated[str, PropertyInfo(alias="serviceProviderNumber")]

    services_plan_id: Annotated[str, PropertyInfo(alias="servicesPlanID")]

    ssn: str

    suffix: str


class EligibilityResponseSubscriberAaaError(TypedDict, total=False):
    code: Literal[
        "15",
        "33",
        "35",
        "42",
        "43",
        "45",
        "47",
        "48",
        "49",
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
        "63",
        "69",
        "70",
        "71",
        "72",
        "73",
        "74",
        "75",
        "76",
        "78",
        "98",
        "AA",
        "AE",
        "AF",
        "AG",
        "AO",
        "CI",
        "E8",
        "IA",
        "MA",
    ]

    description: str

    field: str

    followup_action: Annotated[
        Literal[
            "Please Correct and Resubmit",
            "Resubmission Not Allowed",
            "Resubmission Allowed",
            "Do Not Resubmit; Inquiry Initiated to a Third Party",
            "Please Wait 30 Days and Resubmit",
            "Please Wait 10 Days and Resubmit",
            "Do Not Resubmit; We Will Hold Your Request and Respond Again Shortly",
        ],
        PropertyInfo(alias="followupAction"),
    ]

    location: str

    possible_resolutions: Annotated[str, PropertyInfo(alias="possibleResolutions")]


class EligibilityResponseSubscriberAddress(TypedDict, total=False):
    address1: str

    address2: str

    city: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: Literal[
        "NL",
        "PE",
        "NS",
        "NB",
        "QC",
        "ON",
        "MB",
        "SK",
        "AB",
        "BC",
        "YT",
        "NT",
        "NU",
        "DC",
        "AS",
        "GU",
        "MP",
        "PR",
        "UM",
        "VI",
        "AK",
        "AL",
        "AR",
        "AZ",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "IA",
        "ID",
        "IL",
        "IN",
        "KS",
        "KY",
        "LA",
        "MA",
        "MD",
        "ME",
        "MI",
        "MN",
        "MO",
        "MS",
        "MT",
        "NC",
        "ND",
        "NE",
        "NH",
        "NJ",
        "NM",
        "NV",
        "NY",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VA",
        "VT",
        "WA",
        "WI",
        "WV",
        "WY",
    ]


class EligibilityResponseSubscriberHealthCareDiagnosisCode(TypedDict, total=False):
    diagnosis_code: Annotated[str, PropertyInfo(alias="diagnosisCode")]

    diagnosis_type_code: Annotated[str, PropertyInfo(alias="diagnosisTypeCode")]


class EligibilityResponseSubscriberResponseProviderAaaError(TypedDict, total=False):
    code: Literal["15", "41", "43", "44", "45", "46", "47", "48", "50", "51", "79", "97", "T4"]

    description: str

    field: str

    followup_action: Annotated[
        Literal[
            "Please Correct and Resubmit",
            "Resubmission Not Allowed",
            "Resubmission Allowed",
            "Do Not Resubmit; Inquiry Initiated to a Third Party",
            "Please Wait 30 Days and Resubmit",
            "Please Wait 10 Days and Resubmit",
            "Do Not Resubmit; We Will Hold Your Request and Respond Again Shortly",
        ],
        PropertyInfo(alias="followupAction"),
    ]

    location: str

    possible_resolutions: Annotated[str, PropertyInfo(alias="possibleResolutions")]


class EligibilityResponseSubscriberResponseProviderAddress(TypedDict, total=False):
    address1: str

    address2: str

    city: str

    country_code: Annotated[str, PropertyInfo(alias="countryCode")]

    country_sub_division_code: Annotated[str, PropertyInfo(alias="countrySubDivisionCode")]

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]

    state: Literal[
        "NL",
        "PE",
        "NS",
        "NB",
        "QC",
        "ON",
        "MB",
        "SK",
        "AB",
        "BC",
        "YT",
        "NT",
        "NU",
        "DC",
        "AS",
        "GU",
        "MP",
        "PR",
        "UM",
        "VI",
        "AK",
        "AL",
        "AR",
        "AZ",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "IA",
        "ID",
        "IL",
        "IN",
        "KS",
        "KY",
        "LA",
        "MA",
        "MD",
        "ME",
        "MI",
        "MN",
        "MO",
        "MS",
        "MT",
        "NC",
        "ND",
        "NE",
        "NH",
        "NJ",
        "NM",
        "NV",
        "NY",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VA",
        "VT",
        "WA",
        "WI",
        "WV",
        "WY",
    ]


class EligibilityResponseSubscriberResponseProvider(TypedDict, total=False):
    aaa_errors: Annotated[
        Iterable[EligibilityResponseSubscriberResponseProviderAaaError], PropertyInfo(alias="aaaErrors")
    ]

    address: EligibilityResponseSubscriberResponseProviderAddress

    employers_id: Annotated[str, PropertyInfo(alias="employersId")]

    entity_identifier: Annotated[
        Literal[
            "Provider",
            "Third-Party Administrator",
            "Employer",
            "Hospital",
            "Facility",
            "Gateway Provider",
            "Plan Sponsor",
            "Payer",
        ],
        PropertyInfo(alias="entityIdentifier"),
    ]

    entity_type: Annotated[Literal["Person", "Non-Person Entity"], PropertyInfo(alias="entityType")]

    federal_taxpayers_id_number: Annotated[str, PropertyInfo(alias="federalTaxpayersIdNumber")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    npi: str

    payor_identification: Annotated[str, PropertyInfo(alias="payorIdentification")]

    pharmacy_processor_number: Annotated[str, PropertyInfo(alias="pharmacyProcessorNumber")]

    provider_code: Annotated[
        Literal[
            "AD", "AT", "BI", "CO", "CV", "H", "HH", "LA", "OT", "P1", "P2", "PC", "PE", "R", "RF", "SB", "SK", "SU"
        ],
        PropertyInfo(alias="providerCode"),
    ]

    provider_first_name: Annotated[str, PropertyInfo(alias="providerFirstName")]

    provider_name: Annotated[str, PropertyInfo(alias="providerName")]

    provider_org_name: Annotated[str, PropertyInfo(alias="providerOrgName")]

    reference_identification: Annotated[str, PropertyInfo(alias="referenceIdentification")]

    service_provider_number: Annotated[str, PropertyInfo(alias="serviceProviderNumber")]

    services_plan_id: Annotated[str, PropertyInfo(alias="servicesPlanID")]

    ssn: str

    suffix: str


class EligibilityResponseSubscriber(TypedDict, total=False):
    aaa_errors: Annotated[Iterable[EligibilityResponseSubscriberAaaError], PropertyInfo(alias="aaaErrors")]

    address: EligibilityResponseSubscriberAddress

    birth_sequence_number: Annotated[str, PropertyInfo(alias="birthSequenceNumber")]

    date_of_birth: Annotated[str, PropertyInfo(alias="dateOfBirth")]

    date_time_period: Annotated[str, PropertyInfo(alias="dateTimePeriod")]

    date_time_period_format_qualifier: Annotated[
        Literal["D8", "RD8"], PropertyInfo(alias="dateTimePeriodFormatQualifier")
    ]

    description: str

    employment_status_code: Annotated[
        Literal["AE", "AO", "AS", "AT", "AU", "CC", "DD", "HD", "IR", "LX", "PE", "RE", "RM", "RR", "RU"],
        PropertyInfo(alias="employmentStatusCode"),
    ]

    end_date_time_period: Annotated[str, PropertyInfo(alias="endDateTimePeriod")]

    entity_identifier: Annotated[Literal["Insured or Subscriber"], PropertyInfo(alias="entityIdentifier")]

    entity_type: Annotated[Literal["Person", "Non-Person Entity"], PropertyInfo(alias="entityType")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    gender: Literal["M", "F", "U"]

    government_service_affiliation_code: Annotated[
        Literal["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "Q", "R", "S", "U", "W"],
        PropertyInfo(alias="governmentServiceAffiliationCode"),
    ]

    group_description: Annotated[str, PropertyInfo(alias="groupDescription")]

    group_number: Annotated[str, PropertyInfo(alias="groupNumber")]

    health_care_diagnosis_codes: Annotated[
        Iterable[EligibilityResponseSubscriberHealthCareDiagnosisCode], PropertyInfo(alias="healthCareDiagnosisCodes")
    ]

    information_status_code: Annotated[
        Literal["A", "C", "L", "O", "P", "S", "T"], PropertyInfo(alias="informationStatusCode")
    ]

    insured_indicator: Annotated[Literal["Y"], PropertyInfo(alias="insuredIndicator")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    maintenance_reason_code: Annotated[Literal["25"], PropertyInfo(alias="maintenanceReasonCode")]

    maintenance_type_code: Annotated[Literal["001"], PropertyInfo(alias="maintenanceTypeCode")]

    member_id: Annotated[str, PropertyInfo(alias="memberId")]

    middle_name: Annotated[str, PropertyInfo(alias="middleName")]

    military_service_rank_code: Annotated[
        Literal[
            "A1",
            "A2",
            "A3",
            "B1",
            "B2",
            "C1",
            "C2",
            "C3",
            "C4",
            "C5",
            "C6",
            "C7",
            "C8",
            "C9",
            "E1",
            "F1",
            "F2",
            "F3",
            "F4",
            "G1",
            "G4",
            "L1",
            "L2",
            "L3",
            "L4",
            "L5",
            "L6",
            "M1",
            "M2",
            "M3",
            "M4",
            "M5",
            "M6",
            "P1",
            "P2",
            "P3",
            "P4",
            "P5",
            "R1",
            "R2",
            "S1",
            "S2",
            "S3",
            "S4",
            "S5",
            "S6",
            "S7",
            "S8",
            "S9",
            "SA",
            "SB",
            "SC",
            "T1",
            "V1",
            "W1",
        ],
        PropertyInfo(alias="militaryServiceRankCode"),
    ]

    plan_description: Annotated[str, PropertyInfo(alias="planDescription")]

    plan_network_description: Annotated[str, PropertyInfo(alias="planNetworkDescription")]

    plan_network_id_number: Annotated[str, PropertyInfo(alias="planNetworkIdNumber")]

    plan_number: Annotated[str, PropertyInfo(alias="planNumber")]

    relation_to_subscriber: Annotated[Literal["Self"], PropertyInfo(alias="relationToSubscriber")]

    relation_to_subscriber_code: Annotated[Literal["18"], PropertyInfo(alias="relationToSubscriberCode")]

    response_provider: Annotated[EligibilityResponseSubscriberResponseProvider, PropertyInfo(alias="responseProvider")]

    ssn: str

    start_date_time_period: Annotated[str, PropertyInfo(alias="startDateTimePeriod")]

    suffix: str

    unique_health_identifier: Annotated[str, PropertyInfo(alias="uniqueHealthIdentifier")]


class EligibilityResponseSubscriberTraceNumber(TypedDict, total=False):
    originating_company_identifier: Annotated[str, PropertyInfo(alias="originatingCompanyIdentifier")]

    reference_identification: Annotated[str, PropertyInfo(alias="referenceIdentification")]

    secondary_reference_identification: Annotated[str, PropertyInfo(alias="secondaryReferenceIdentification")]

    trace_type: Annotated[str, PropertyInfo(alias="traceType")]

    trace_type_code: Annotated[str, PropertyInfo(alias="traceTypeCode")]


class EligibilityResponseWarning(TypedDict, total=False):
    code: str

    description: str


class EligibilityResponse(TypedDict, total=False):
    in_network: Required[Annotated[bool, PropertyInfo(alias="inNetwork")]]

    benefits_information: Annotated[
        Iterable[EligibilityResponseBenefitsInformation], PropertyInfo(alias="benefitsInformation")
    ]

    control_number: Annotated[str, PropertyInfo(alias="controlNumber")]

    dependents: Iterable[EligibilityResponseDependent]

    errors: Iterable[EligibilityResponseError]

    implementation_transaction_set_syntax_error: Annotated[
        str, PropertyInfo(alias="implementationTransactionSetSyntaxError")
    ]

    meta: EligibilityResponseMeta

    payer: EligibilityResponsePayer

    plan_date_information: Annotated[EligibilityResponsePlanDateInformation, PropertyInfo(alias="planDateInformation")]

    plan_information: Annotated[EligibilityResponsePlanInformation, PropertyInfo(alias="planInformation")]

    plan_status: Annotated[Iterable[EligibilityResponsePlanStatus], PropertyInfo(alias="planStatus")]

    provider: EligibilityResponseProvider

    reassociation_key: Annotated[str, PropertyInfo(alias="reassociationKey")]

    status: str

    subscriber: EligibilityResponseSubscriber

    subscriber_trace_numbers: Annotated[
        Iterable[EligibilityResponseSubscriberTraceNumber], PropertyInfo(alias="subscriberTraceNumbers")
    ]

    trading_partner_service_id: Annotated[str, PropertyInfo(alias="tradingPartnerServiceId")]

    transaction_set_acknowledgement: Annotated[str, PropertyInfo(alias="transactionSetAcknowledgement")]

    warnings: Iterable[EligibilityResponseWarning]

    x12: str


class LineItem(TypedDict, total=False):
    id: Required[str]

    cpt_code: Required[Annotated[str, PropertyInfo(alias="cptCode")]]

    service_amount: Required[Annotated[float, PropertyInfo(alias="serviceAmount")]]

    service_date: Required[Annotated[str, PropertyInfo(alias="serviceDate")]]
