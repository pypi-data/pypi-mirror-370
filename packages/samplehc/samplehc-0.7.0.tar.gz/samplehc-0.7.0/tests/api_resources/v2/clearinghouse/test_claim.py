# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.clearinghouse import ClaimSubmitResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClaim:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cancel(self, client: SampleHealthcare) -> None:
        claim = client.v2.clearinghouse.claim.cancel(
            "claimId",
        )
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_cancel(self, client: SampleHealthcare) -> None:
        response = client.v2.clearinghouse.claim.with_raw_response.cancel(
            "claimId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        claim = response.parse()
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_cancel(self, client: SampleHealthcare) -> None:
        with client.v2.clearinghouse.claim.with_streaming_response.cancel(
            "claimId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            claim = response.parse()
            assert_matches_type(object, claim, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_cancel(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `claim_id` but received ''"):
            client.v2.clearinghouse.claim.with_raw_response.cancel(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_status(self, client: SampleHealthcare) -> None:
        claim = client.v2.clearinghouse.claim.retrieve_status(
            "claimId",
        )
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_status(self, client: SampleHealthcare) -> None:
        response = client.v2.clearinghouse.claim.with_raw_response.retrieve_status(
            "claimId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        claim = response.parse()
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_status(self, client: SampleHealthcare) -> None:
        with client.v2.clearinghouse.claim.with_streaming_response.retrieve_status(
            "claimId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            claim = response.parse()
            assert_matches_type(object, claim, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_status(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `claim_id` but received ''"):
            client.v2.clearinghouse.claim.with_raw_response.retrieve_status(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_submit(self, client: SampleHealthcare) -> None:
        claim = client.v2.clearinghouse.claim.submit(
            billing={},
            claim_information={
                "benefits_assignment_certification_indicator": "N",
                "claim_charge_amount": "321669910225",
                "claim_filing_code": "11",
                "claim_frequency_code": "1",
                "health_care_code_information": [
                    {
                        "diagnosis_code": "diagnosisCode",
                        "diagnosis_type_code": "BK",
                    }
                ],
                "place_of_service_code": "01",
                "plan_participation_code": "A",
                "release_information_code": "I",
                "service_lines": [
                    {
                        "professional_service": {
                            "composite_diagnosis_code_pointers": {"diagnosis_code_pointers": ["string"]},
                            "line_item_charge_amount": "321669910225",
                            "measurement_unit": "MJ",
                            "procedure_code": "procedureCode",
                            "procedure_identifier": "ER",
                            "service_unit_count": "serviceUnitCount",
                        },
                        "service_date": "73210630",
                    }
                ],
                "signature_indicator": "N",
            },
            is_testing=True,
            receiver={"organization_name": "x"},
            submitter={"contact_information": {}},
            subscriber={},
            trading_partner_service_id="x",
        )
        assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_submit_with_all_params(self, client: SampleHealthcare) -> None:
        claim = client.v2.clearinghouse.claim.submit(
            billing={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "commercial_number": "commercialNumber",
                "contact_information": {
                    "email": "email",
                    "fax_number": "faxNumber",
                    "name": "name",
                    "phone_extension": "phoneExtension",
                    "phone_number": "phoneNumber",
                },
                "employer_id": "employerId",
                "first_name": "firstName",
                "last_name": "lastName",
                "location_number": "locationNumber",
                "middle_name": "middleName",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "provider_type": "providerType",
                "provider_upin_number": "providerUpinNumber",
                "ssn": "732166991",
                "state_license_number": "stateLicenseNumber",
                "suffix": "suffix",
                "taxonomy_code": "2E02VLfW09",
            },
            claim_information={
                "benefits_assignment_certification_indicator": "N",
                "claim_charge_amount": "321669910225",
                "claim_filing_code": "11",
                "claim_frequency_code": "1",
                "health_care_code_information": [
                    {
                        "diagnosis_code": "diagnosisCode",
                        "diagnosis_type_code": "BK",
                    }
                ],
                "place_of_service_code": "01",
                "plan_participation_code": "A",
                "release_information_code": "I",
                "service_lines": [
                    {
                        "professional_service": {
                            "composite_diagnosis_code_pointers": {"diagnosis_code_pointers": ["string"]},
                            "line_item_charge_amount": "321669910225",
                            "measurement_unit": "MJ",
                            "procedure_code": "procedureCode",
                            "procedure_identifier": "ER",
                            "service_unit_count": "serviceUnitCount",
                            "copay_status_code": "0",
                            "description": "x",
                            "emergency_indicator": "Y",
                            "epsdt_indicator": "Y",
                            "family_planning_indicator": "Y",
                            "place_of_service_code": "placeOfServiceCode",
                            "procedure_modifiers": ["string"],
                        },
                        "service_date": "73210630",
                        "additional_notes": "additionalNotes",
                        "ambulance_certification": [
                            {
                                "certification_condition_indicator": "N",
                                "condition_codes": ["01"],
                            }
                        ],
                        "ambulance_drop_off_location": {
                            "address1": "address1",
                            "city": "city",
                            "address2": "address2",
                            "country_code": "countryCode",
                            "country_sub_division_code": "countrySubDivisionCode",
                            "postal_code": "postalCode",
                            "state": "state",
                        },
                        "ambulance_patient_count": 0,
                        "ambulance_pick_up_location": {
                            "address1": "address1",
                            "city": "city",
                            "address2": "address2",
                            "country_code": "countryCode",
                            "country_sub_division_code": "countrySubDivisionCode",
                            "postal_code": "postalCode",
                            "state": "state",
                        },
                        "ambulance_transport_information": {
                            "ambulance_transport_reason_code": "A",
                            "transport_distance_in_miles": "transportDistanceInMiles",
                            "patient_weight_in_pounds": "patientWeightInPounds",
                            "round_trip_purpose_description": "roundTripPurposeDescription",
                            "stretcher_purpose_description": "stretcherPurposeDescription",
                        },
                        "assigned_number": "assignedNumber",
                        "condition_indicator_durable_medical_equipment": {
                            "certification_condition_indicator": "Y",
                            "condition_indicator": "38",
                            "condition_indicator_code": "38",
                        },
                        "contract_information": {
                            "contract_type_code": "01",
                            "contract_amount": "321669910225",
                            "contract_code": "contractCode",
                            "contract_percentage": "contractPercentage",
                            "contract_version_identifier": "contractVersionIdentifier",
                            "terms_discount_percentage": "termsDiscountPercentage",
                        },
                        "drug_identification": {
                            "measurement_unit_code": "F2",
                            "national_drug_code": "nationalDrugCode",
                            "national_drug_unit_count": "nationalDrugUnitCount",
                            "service_id_qualifier": "EN",
                            "link_sequence_number": "linkSequenceNumber",
                            "pharmacy_prescription_number": "pharmacyPrescriptionNumber",
                        },
                        "durable_medical_equipment_certificate_of_medical_necessity": {
                            "attachment_transmission_code": "AB"
                        },
                        "durable_medical_equipment_certification": {
                            "certification_type_code": "I",
                            "durable_medical_equipment_duration_in_months": "durableMedicalEquipmentDurationInMonths",
                        },
                        "durable_medical_equipment_service": {
                            "days": "days",
                            "frequency_code": "1",
                            "purchase_price": "purchasePrice",
                            "rental_price": "rentalPrice",
                        },
                        "file_information": ["string"],
                        "form_identification": [
                            {
                                "form_identifier": "formIdentifier",
                                "form_type_code": "AS",
                                "supporting_documentation": [
                                    {
                                        "question_number": "questionNumber",
                                        "question_response": "questionResponse",
                                        "question_response_as_date": "questionResponseAsDate",
                                        "question_response_as_percent": "questionResponseAsPercent",
                                        "question_response_code": "N",
                                    }
                                ],
                            }
                        ],
                        "goal_rehab_or_discharge_plans": "goalRehabOrDischargePlans",
                        "hospice_employee_indicator": True,
                        "line_adjudication_information": [
                            {
                                "adjudication_or_payment_date": "73210630",
                                "other_payer_primary_identifier": "otherPayerPrimaryIdentifier",
                                "paid_service_unit_count": "paidServiceUnitCount",
                                "procedure_code": "procedureCode",
                                "service_id_qualifier": "ER",
                                "service_line_paid_amount": "321669910225",
                                "bundled_or_unbundled_line_number": "bundledOrUnbundledLineNumber",
                                "claim_adjustment_information": [
                                    {
                                        "adjustment_details": [
                                            {
                                                "adjustment_amount": "321669910225",
                                                "adjustment_reason_code": "adjustmentReasonCode",
                                                "adjustment_quantity": "adjustmentQuantity",
                                            }
                                        ],
                                        "adjustment_group_code": "CO",
                                    }
                                ],
                                "procedure_code_description": "procedureCodeDescription",
                                "procedure_modifier": ["string"],
                                "remaining_patient_liability": "321669910225",
                            }
                        ],
                        "line_pricing_repricing_information": {
                            "pricing_methodology_code": "00",
                            "repriced_allowed_amount": "321669910225",
                            "exception_code": "1",
                            "policy_compliance_code": "1",
                            "reject_reason_code": "T1",
                            "repriced_approved_ambulatory_patient_group_amount": "321669910225",
                            "repriced_approved_ambulatory_patient_group_code": "repricedApprovedAmbulatoryPatientGroupCode",
                            "repriced_saving_amount": "321669910225",
                            "repricing_organization_identifier": "repricingOrganizationIdentifier",
                            "repricing_per_diem_or_flat_rate_amount": "repricingPerDiemOrFlatRateAmount",
                        },
                        "obstetric_anesthesia_additional_units": 0,
                        "ordering_provider": {
                            "address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "countryCode",
                                "country_sub_division_code": "countrySubDivisionCode",
                                "postal_code": "postalCode",
                                "state": "state",
                            },
                            "claim_office_number": "claimOfficeNumber",
                            "commercial_number": "commercialNumber",
                            "contact_information": {
                                "name": "name",
                                "email": "email",
                                "fax_number": "faxNumber",
                                "phone_extension": "phoneExtension",
                                "phone_number": "phoneNumber",
                            },
                            "employer_id": "employerId",
                            "employer_identification_number": "employerIdentificationNumber",
                            "first_name": "firstName",
                            "last_name": "lastName",
                            "location_number": "locationNumber",
                            "middle_name": "middleName",
                            "naic": "naic",
                            "npi": "7321669910",
                            "organization_name": "organizationName",
                            "other_identifier": "otherIdentifier",
                            "payer_identification_number": "payerIdentificationNumber",
                            "provider_type": "providerType",
                            "provider_upin_number": "providerUpinNumber",
                            "secondary_identifier": [
                                {
                                    "identifier": "identifier",
                                    "qualifier": "qualifier",
                                    "other_identifier": "otherIdentifier",
                                }
                            ],
                            "ssn": "732166991",
                            "state_license_number": "stateLicenseNumber",
                            "suffix": "suffix",
                            "taxonomy_code": "2E02VLfW09",
                        },
                        "postage_tax_amount": "321669910225",
                        "purchased_service_information": {
                            "purchased_service_charge_amount": "purchasedServiceChargeAmount",
                            "purchased_service_provider_identifier": "purchasedServiceProviderIdentifier",
                        },
                        "purchased_service_provider": {
                            "address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "countryCode",
                                "country_sub_division_code": "countrySubDivisionCode",
                                "postal_code": "postalCode",
                                "state": "state",
                            },
                            "claim_office_number": "claimOfficeNumber",
                            "commercial_number": "commercialNumber",
                            "contact_information": {
                                "email": "email",
                                "fax_number": "faxNumber",
                                "name": "name",
                                "phone_extension": "phoneExtension",
                                "phone_number": "phoneNumber",
                            },
                            "employer_id": "employerId",
                            "employer_identification_number": "employerIdentificationNumber",
                            "first_name": "firstName",
                            "last_name": "lastName",
                            "location_number": "locationNumber",
                            "middle_name": "middleName",
                            "naic": "naic",
                            "npi": "7321669910",
                            "organization_name": "organizationName",
                            "other_identifier": "otherIdentifier",
                            "payer_identification_number": "payerIdentificationNumber",
                            "provider_type": "providerType",
                            "provider_upin_number": "providerUpinNumber",
                            "secondary_identifier": [
                                {
                                    "identifier": "identifier",
                                    "qualifier": "qualifier",
                                    "other_identifier": "otherIdentifier",
                                }
                            ],
                            "ssn": "732166991",
                            "state_license_number": "stateLicenseNumber",
                            "suffix": "suffix",
                            "taxonomy_code": "2E02VLfW09",
                        },
                        "referring_provider": {
                            "provider_type": "providerType",
                            "address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "countryCode",
                                "country_sub_division_code": "countrySubDivisionCode",
                                "postal_code": "postalCode",
                                "state": "state",
                            },
                            "claim_office_number": "claimOfficeNumber",
                            "commercial_number": "commercialNumber",
                            "contact_information": {
                                "email": "email",
                                "fax_number": "faxNumber",
                                "name": "name",
                                "phone_extension": "phoneExtension",
                                "phone_number": "phoneNumber",
                            },
                            "employer_id": "employerId",
                            "employer_identification_number": "employerIdentificationNumber",
                            "first_name": "firstName",
                            "last_name": "lastName",
                            "location_number": "locationNumber",
                            "middle_name": "middleName",
                            "naic": "naic",
                            "npi": "7321669910",
                            "organization_name": "organizationName",
                            "other_identifier": "otherIdentifier",
                            "payer_identification_number": "payerIdentificationNumber",
                            "provider_upin_number": "providerUpinNumber",
                            "secondary_identifier": [
                                {
                                    "identifier": "identifier",
                                    "qualifier": "qualifier",
                                    "other_identifier": "otherIdentifier",
                                }
                            ],
                            "ssn": "732166991",
                            "state_license_number": "stateLicenseNumber",
                            "suffix": "suffix",
                            "taxonomy_code": "2E02VLfW09",
                        },
                        "rendering_provider": {
                            "provider_type": "providerType",
                            "address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "countryCode",
                                "country_sub_division_code": "countrySubDivisionCode",
                                "postal_code": "postalCode",
                                "state": "state",
                            },
                            "claim_office_number": "claimOfficeNumber",
                            "commercial_number": "commercialNumber",
                            "contact_information": {
                                "email": "email",
                                "fax_number": "faxNumber",
                                "name": "name",
                                "phone_extension": "phoneExtension",
                                "phone_number": "phoneNumber",
                            },
                            "employer_id": "employerId",
                            "employer_identification_number": "employerIdentificationNumber",
                            "first_name": "firstName",
                            "last_name": "lastName",
                            "location_number": "locationNumber",
                            "middle_name": "middleName",
                            "naic": "naic",
                            "npi": "7321669910",
                            "organization_name": "organizationName",
                            "other_identifier": "otherIdentifier",
                            "payer_identification_number": "payerIdentificationNumber",
                            "provider_upin_number": "providerUpinNumber",
                            "secondary_identifier": [
                                {
                                    "identifier": "identifier",
                                    "qualifier": "qualifier",
                                    "other_identifier": "otherIdentifier",
                                }
                            ],
                            "ssn": "732166991",
                            "state_license_number": "stateLicenseNumber",
                            "suffix": "suffix",
                            "taxonomy_code": "2E02VLfW09",
                        },
                        "sales_tax_amount": "salesTaxAmount",
                        "service_date_end": "73210630",
                        "service_facility_location": {
                            "address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "countryCode",
                                "country_sub_division_code": "countrySubDivisionCode",
                                "postal_code": "postalCode",
                                "state": "state",
                            },
                            "organization_name": "organizationName",
                            "npi": "7321669910",
                            "phone_extension": "phoneExtension",
                            "phone_name": "phoneName",
                            "phone_number": "phoneNumber",
                            "secondary_identifier": [
                                {
                                    "identifier": "identifier",
                                    "qualifier": "qualifier",
                                    "other_identifier": "otherIdentifier",
                                }
                            ],
                        },
                        "service_line_date_information": {
                            "begin_therapy_date": "73210630",
                            "certification_revision_or_recertification_date": "73210630",
                            "hemoglobin_test_date": "73210630",
                            "initial_treatment_date": "73210630",
                            "last_certification_date": "73210630",
                            "last_x_ray_date": "73210630",
                            "prescription_date": "73210630",
                            "serum_creatine_test_date": "73210630",
                            "shipped_date": "73210630",
                            "treatment_or_therapy_date": "73210630",
                        },
                        "service_line_reference_information": {
                            "adjusted_repriced_line_item_reference_number": "adjustedRepricedLineItemReferenceNumber",
                            "clinical_laboratory_improvement_amendment_number": "clinicalLaboratoryImprovementAmendmentNumber",
                            "immunization_batch_number": "immunizationBatchNumber",
                            "mammography_certification_number": "mammographyCertificationNumber",
                            "prior_authorization": [
                                {
                                    "prior_authorization_or_referral_number": "priorAuthorizationOrReferralNumber",
                                    "other_payer_primary_identifier": "otherPayerPrimaryIdentifier",
                                }
                            ],
                            "referral_number": ["string"],
                            "referring_clia_number": "referringCliaNumber",
                            "repriced_line_item_reference_number": "repricedLineItemReferenceNumber",
                        },
                        "service_line_supplemental_information": [
                            {
                                "attachment_report_type_code": "03",
                                "attachment_transmission_code": "AA",
                                "attachment_control_number": "attachmentControlNumber",
                            }
                        ],
                        "supervising_provider": {
                            "provider_type": "providerType",
                            "address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "countryCode",
                                "country_sub_division_code": "countrySubDivisionCode",
                                "postal_code": "postalCode",
                                "state": "state",
                            },
                            "claim_office_number": "claimOfficeNumber",
                            "commercial_number": "commercialNumber",
                            "contact_information": {
                                "email": "email",
                                "fax_number": "faxNumber",
                                "name": "name",
                                "phone_extension": "phoneExtension",
                                "phone_number": "phoneNumber",
                            },
                            "employer_id": "employerId",
                            "employer_identification_number": "employerIdentificationNumber",
                            "first_name": "firstName",
                            "last_name": "lastName",
                            "location_number": "locationNumber",
                            "middle_name": "middleName",
                            "naic": "naic",
                            "npi": "7321669910",
                            "organization_name": "organizationName",
                            "other_identifier": "otherIdentifier",
                            "payer_identification_number": "payerIdentificationNumber",
                            "provider_upin_number": "providerUpinNumber",
                            "secondary_identifier": [
                                {
                                    "identifier": "identifier",
                                    "qualifier": "qualifier",
                                    "other_identifier": "otherIdentifier",
                                }
                            ],
                            "ssn": "732166991",
                            "state_license_number": "stateLicenseNumber",
                            "suffix": "suffix",
                            "taxonomy_code": "2E02VLfW09",
                        },
                        "test_results": [
                            {
                                "measurement_qualifier": "HT",
                                "measurement_reference_identification_code": "OG",
                                "test_results": "testResults",
                            }
                        ],
                        "third_party_organization_notes": "thirdPartyOrganizationNotes",
                    }
                ],
                "signature_indicator": "N",
                "ambulance_certification": [
                    {
                        "certification_condition_indicator": "N",
                        "condition_codes": ["01"],
                    }
                ],
                "ambulance_drop_off_location": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "ambulance_pick_up_location": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "ambulance_transport_information": {
                    "ambulance_transport_reason_code": "A",
                    "transport_distance_in_miles": "transportDistanceInMiles",
                    "patient_weight_in_pounds": "patientWeightInPounds",
                    "round_trip_purpose_description": "roundTripPurposeDescription",
                    "stretcher_purpose_description": "stretcherPurposeDescription",
                },
                "anesthesia_related_surgical_procedure": ["string"],
                "auto_accident_country_code": "autoAccidentCountryCode",
                "auto_accident_state_code": "autoAccidentStateCode",
                "claim_contract_information": {
                    "contract_type_code": "01",
                    "contract_amount": "321669910225",
                    "contract_code": "contractCode",
                    "contract_percentage": "contractPercentage",
                    "contract_version_identifier": "contractVersionIdentifier",
                    "terms_discount_percentage": "termsDiscountPercentage",
                },
                "claim_date_information": {
                    "accident_date": "accidentDate",
                    "acute_manifestation_date": "acuteManifestationDate",
                    "admission_date": "admissionDate",
                    "assumed_and_relinquished_care_begin_date": "assumedAndRelinquishedCareBeginDate",
                    "assumed_and_relinquished_care_end_date": "assumedAndRelinquishedCareEndDate",
                    "authorized_return_to_work_date": "authorizedReturnToWorkDate",
                    "disability_begin_date": "disabilityBeginDate",
                    "disability_end_date": "disabilityEndDate",
                    "discharge_date": "dischargeDate",
                    "first_contact_date": "firstContactDate",
                    "hearing_and_vision_prescription_date": "hearingAndVisionPrescriptionDate",
                    "initial_treatment_date": "initialTreatmentDate",
                    "last_menstrual_period_date": "lastMenstrualPeriodDate",
                    "last_seen_date": "lastSeenDate",
                    "last_worked_date": "lastWorkedDate",
                    "last_x_ray_date": "lastXRayDate",
                    "repricer_received_date": "repricerReceivedDate",
                    "symptom_date": "symptomDate",
                },
                "claim_note": {
                    "additional_information": "additionalInformation",
                    "certification_narrative": "certificationNarrative",
                    "diagnosis_description": "diagnosisDescription",
                    "goal_rehab_or_discharge_plans": "goalRehabOrDischargePlans",
                    "third_part_org_notes": "thirdPartOrgNotes",
                },
                "claim_pricing_repricing_information": {
                    "pricing_methodology_code": "00",
                    "repriced_allowed_amount": "321669910225",
                    "exception_code": "1",
                    "policy_compliance_code": "1",
                    "reject_reason_code": "T1",
                    "repriced_approved_ambulatory_patient_group_amount": "321669910225",
                    "repriced_approved_ambulatory_patient_group_code": "repricedApprovedAmbulatoryPatientGroupCode",
                    "repriced_saving_amount": "321669910225",
                    "repricing_organization_identifier": "repricingOrganizationIdentifier",
                    "repricing_per_diem_or_flat_rate_amount": "repricingPerDiemOrFlatRateAmount",
                },
                "claim_supplemental_information": {
                    "adjusted_repriced_claim_number": "adjustedRepricedClaimNumber",
                    "care_plan_oversight_number": "carePlanOversightNumber",
                    "claim_control_number": "claimControlNumber",
                    "claim_number": "claimNumber",
                    "clia_number": "cliaNumber",
                    "demo_project_identifier": "demoProjectIdentifier",
                    "investigational_device_exemption_number": "investigationalDeviceExemptionNumber",
                    "mammography_certification_number": "mammographyCertificationNumber",
                    "medical_record_number": "medicalRecordNumber",
                    "medicare_crossover_reference_id": "medicareCrossoverReferenceId",
                    "prior_authorization_number": "priorAuthorizationNumber",
                    "referral_number": "referralNumber",
                    "report_information": {
                        "attachment_report_type_code": "03",
                        "attachment_transmission_code": "AA",
                        "attachment_control_number": "attachmentControlNumber",
                    },
                    "report_informations": [
                        {
                            "attachment_report_type_code": "03",
                            "attachment_transmission_code": "AA",
                            "attachment_control_number": "attachmentControlNumber",
                        }
                    ],
                    "repriced_claim_number": "repricedClaimNumber",
                    "service_authorization_exception_code": "1",
                },
                "condition_information": [{"condition_codes": ["string"]}],
                "death_date": "73210630",
                "delay_reason_code": "1",
                "epsdt_referral": {
                    "certification_condition_code_applies_indicator": "N",
                    "condition_codes": ["AV"],
                },
                "file_information": "fileInformation",
                "file_information_list": ["string"],
                "homebound_indicator": True,
                "other_subscriber_information": [
                    {
                        "benefits_assignment_certification_indicator": "N",
                        "claim_filing_indicator_code": "11",
                        "individual_relationship_code": "01",
                        "other_payer_name": {
                            "other_payer_identifier": "otherPayerIdentifier",
                            "other_payer_identifier_type_code": "PI",
                            "other_payer_organization_name": "otherPayerOrganizationName",
                            "other_payer_address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "countryCode",
                                "country_sub_division_code": "countrySubDivisionCode",
                                "postal_code": "postalCode",
                                "state": "state",
                            },
                            "other_payer_adjudication_or_payment_date": "otherPayerAdjudicationOrPaymentDate",
                            "other_payer_claim_adjustment_indicator": True,
                            "other_payer_claim_control_number": "otherPayerClaimControlNumber",
                            "other_payer_prior_authorization_number": "otherPayerPriorAuthorizationNumber",
                            "other_payer_prior_authorization_or_referral_number": "otherPayerPriorAuthorizationOrReferralNumber",
                            "other_payer_secondary_identifier": [
                                {
                                    "identifier": "identifier",
                                    "qualifier": "qualifier",
                                    "other_identifier": "otherIdentifier",
                                }
                            ],
                        },
                        "other_subscriber_name": {
                            "other_insured_identifier": "otherInsuredIdentifier",
                            "other_insured_identifier_type_code": "II",
                            "other_insured_last_name": "otherInsuredLastName",
                            "other_insured_qualifier": "1",
                            "other_insured_additional_identifier": "otherInsuredAdditionalIdentifier",
                            "other_insured_address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "countryCode",
                                "country_sub_division_code": "countrySubDivisionCode",
                                "postal_code": "postalCode",
                                "state": "state",
                            },
                            "other_insured_first_name": "otherInsuredFirstName",
                            "other_insured_middle_name": "otherInsuredMiddleName",
                            "other_insured_name_suffix": "otherInsuredNameSuffix",
                        },
                        "payment_responsibility_level_code": "A",
                        "release_of_information_code": "I",
                        "claim_level_adjustments": [
                            {
                                "adjustment_details": [
                                    {
                                        "adjustment_amount": "321669910225",
                                        "adjustment_reason_code": "adjustmentReasonCode",
                                        "adjustment_quantity": "adjustmentQuantity",
                                    }
                                ],
                                "adjustment_group_code": "CO",
                            }
                        ],
                        "insurance_group_or_policy_number": "insuranceGroupOrPolicyNumber",
                        "insurance_type_code": "12",
                        "medicare_outpatient_adjudication": {
                            "claim_payment_remark_code": ["string"],
                            "end_stage_renal_disease_payment_amount": "321669910225",
                            "hcpcs_payable_amount": "321669910225",
                            "non_payable_professional_component_billed_amount": "321669910225",
                            "reimbursement_rate": "reimbursementRate",
                        },
                        "non_covered_charge_amount": "321669910225",
                        "other_insured_group_name": "otherInsuredGroupName",
                        "other_payer_billing_provider": [
                            {
                                "entity_type_qualifier": "1",
                                "other_payer_billing_provider_identifier": [
                                    {
                                        "identifier": "identifier",
                                        "qualifier": "qualifier",
                                        "other_identifier": "otherIdentifier",
                                    }
                                ],
                            }
                        ],
                        "other_payer_referring_provider": [
                            {
                                "other_payer_referring_provider_identifier": [
                                    {
                                        "identifier": "identifier",
                                        "qualifier": "qualifier",
                                        "other_identifier": "otherIdentifier",
                                    }
                                ]
                            }
                        ],
                        "other_payer_rendering_provider": [
                            {
                                "entity_type_qualifier": "1",
                                "other_payer_rendering_provider_secondary_identifier": [
                                    {
                                        "identifier": "identifier",
                                        "qualifier": "qualifier",
                                        "other_identifier": "otherIdentifier",
                                    }
                                ],
                            }
                        ],
                        "other_payer_service_facility_location": [
                            {
                                "other_payer_service_facility_location_secondary_identifier": [
                                    {
                                        "identifier": "identifier",
                                        "qualifier": "qualifier",
                                        "other_identifier": "otherIdentifier",
                                    }
                                ]
                            }
                        ],
                        "other_payer_supervising_provider": [
                            {
                                "other_payer_supervising_provider_identifier": [
                                    {
                                        "identifier": "identifier",
                                        "qualifier": "qualifier",
                                        "other_identifier": "otherIdentifier",
                                    }
                                ]
                            }
                        ],
                        "patient_signature_generated_for_patient": True,
                        "payer_paid_amount": "321669910225",
                        "remaining_patient_liability": "321669910225",
                    }
                ],
                "patient_amount_paid": "321669910225",
                "patient_condition_information_vision": [
                    {
                        "certification_condition_indicator": "N",
                        "code_category": "E1",
                        "condition_codes": ["L1"],
                    }
                ],
                "patient_signature_source_code": True,
                "patient_weight": "patientWeight",
                "pregnancy_indicator": "Y",
                "property_casualty_claim_number": "propertyCasualtyClaimNumber",
                "related_causes_code": ["AA"],
                "service_facility_location": {
                    "address": {
                        "address1": "address1",
                        "city": "city",
                        "address2": "address2",
                        "country_code": "countryCode",
                        "country_sub_division_code": "countrySubDivisionCode",
                        "postal_code": "postalCode",
                        "state": "state",
                    },
                    "organization_name": "organizationName",
                    "npi": "7321669910",
                    "phone_extension": "phoneExtension",
                    "phone_name": "phoneName",
                    "phone_number": "phoneNumber",
                    "secondary_identifier": [
                        {
                            "identifier": "identifier",
                            "qualifier": "qualifier",
                            "other_identifier": "otherIdentifier",
                        }
                    ],
                },
                "special_program_code": "02",
                "spinal_manipulation_service_information": {
                    "patient_condition_code": "patientConditionCode",
                    "patient_condition_description1": "A",
                    "patient_condition_description2": "patientConditionDescription2",
                },
            },
            is_testing=True,
            receiver={"organization_name": "x"},
            submitter={
                "contact_information": {
                    "email": "email",
                    "fax_number": "faxNumber",
                    "name": "name",
                    "phone_extension": "phoneExtension",
                    "phone_number": "phoneNumber",
                },
                "first_name": "x",
                "last_name": "x",
                "middle_name": "x",
                "organization_name": "x",
                "submitter_identification": "xx",
            },
            subscriber={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "contact_information": {
                    "name": "name",
                    "email": "email",
                    "fax_number": "faxNumber",
                    "phone_extension": "phoneExtension",
                    "phone_number": "phoneNumber",
                },
                "date_of_birth": "73210630",
                "first_name": "firstName",
                "gender": "M",
                "group_number": "groupNumber",
                "insurance_type_code": "12",
                "last_name": "lastName",
                "member_id": "xx",
                "middle_name": "middleName",
                "organization_name": "organizationName",
                "payment_responsibility_level_code": "A",
                "policy_number": "policyNumber",
                "ssn": "732166991",
                "subscriber_group_name": "subscriberGroupName",
                "suffix": "suffix",
            },
            trading_partner_service_id="x",
            control_number="controlNumber",
            dependent={
                "date_of_birth": "73210630",
                "first_name": "firstName",
                "gender": "M",
                "last_name": "lastName",
                "relationship_to_subscriber_code": "01",
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "contact_information": {
                    "name": "name",
                    "email": "email",
                    "fax_number": "faxNumber",
                    "phone_extension": "phoneExtension",
                    "phone_number": "phoneNumber",
                },
                "member_id": "memberId",
                "middle_name": "middleName",
                "ssn": "732166991",
                "suffix": "suffix",
            },
            ordering={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "claim_office_number": "claimOfficeNumber",
                "commercial_number": "commercialNumber",
                "contact_information": {
                    "email": "email",
                    "fax_number": "faxNumber",
                    "name": "name",
                    "phone_extension": "phoneExtension",
                    "phone_number": "phoneNumber",
                },
                "employer_id": "employerId",
                "employer_identification_number": "employerIdentificationNumber",
                "first_name": "firstName",
                "last_name": "lastName",
                "location_number": "locationNumber",
                "middle_name": "middleName",
                "naic": "naic",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "payer_identification_number": "payerIdentificationNumber",
                "provider_type": "providerType",
                "provider_upin_number": "providerUpinNumber",
                "ssn": "732166991",
                "state_license_number": "stateLicenseNumber",
                "suffix": "suffix",
                "taxonomy_code": "2E02VLfW09",
            },
            payer_address={
                "address1": "address1",
                "city": "city",
                "address2": "address2",
                "country_code": "countryCode",
                "country_sub_division_code": "countrySubDivisionCode",
                "postal_code": "postalCode",
                "state": "state",
            },
            pay_to_address={
                "address1": "address1",
                "city": "city",
                "address2": "address2",
                "country_code": "countryCode",
                "country_sub_division_code": "countrySubDivisionCode",
                "postal_code": "postalCode",
                "state": "state",
            },
            pay_to_plan={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "organization_name": "organizationName",
                "primary_identifier": "primaryIdentifier",
                "primary_identifier_type_code": "PI",
                "tax_identification_number": "xxxxxxxxx",
                "secondary_identifier": "secondaryIdentifier",
                "secondary_identifier_type_code": "2U",
            },
            providers=[
                {
                    "address": {
                        "address1": "address1",
                        "city": "city",
                        "address2": "address2",
                        "country_code": "countryCode",
                        "country_sub_division_code": "countrySubDivisionCode",
                        "postal_code": "postalCode",
                        "state": "state",
                    },
                    "commercial_number": "commercialNumber",
                    "contact_information": {
                        "email": "email",
                        "fax_number": "faxNumber",
                        "name": "name",
                        "phone_extension": "phoneExtension",
                        "phone_number": "phoneNumber",
                    },
                    "employer_id": "employerId",
                    "first_name": "firstName",
                    "last_name": "lastName",
                    "location_number": "locationNumber",
                    "middle_name": "middleName",
                    "npi": "7321669910",
                    "organization_name": "organizationName",
                    "provider_type": "providerType",
                    "provider_upin_number": "providerUpinNumber",
                    "ssn": "732166991",
                    "state_license_number": "stateLicenseNumber",
                    "suffix": "suffix",
                    "taxonomy_code": "2E02VLfW09",
                }
            ],
            referring={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "commercial_number": "commercialNumber",
                "contact_information": {
                    "email": "email",
                    "fax_number": "faxNumber",
                    "name": "name",
                    "phone_extension": "phoneExtension",
                    "phone_number": "phoneNumber",
                },
                "first_name": "firstName",
                "last_name": "lastName",
                "middle_name": "middleName",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "provider_type": "providerType",
                "provider_upin_number": "providerUpinNumber",
                "state_license_number": "stateLicenseNumber",
                "suffix": "suffix",
                "taxonomy_code": "2E02VLfW09",
            },
            rendering={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "commercial_number": "commercialNumber",
                "contact_information": {
                    "email": "email",
                    "fax_number": "faxNumber",
                    "name": "name",
                    "phone_extension": "phoneExtension",
                    "phone_number": "phoneNumber",
                },
                "first_name": "firstName",
                "last_name": "lastName",
                "location_number": "locationNumber",
                "middle_name": "middleName",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "provider_type": "providerType",
                "provider_upin_number": "providerUpinNumber",
                "state_license_number": "stateLicenseNumber",
                "suffix": "suffix",
                "taxonomy_code": "2E02VLfW09",
            },
            supervising={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "commercial_number": "commercialNumber",
                "contact_information": {
                    "email": "email",
                    "fax_number": "faxNumber",
                    "name": "name",
                    "phone_extension": "phoneExtension",
                    "phone_number": "phoneNumber",
                },
                "employer_id": "employerId",
                "first_name": "firstName",
                "last_name": "lastName",
                "location_number": "locationNumber",
                "middle_name": "middleName",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "provider_type": "providerType",
                "provider_upin_number": "providerUpinNumber",
                "ssn": "732166991",
                "state_license_number": "stateLicenseNumber",
                "suffix": "suffix",
                "taxonomy_code": "2E02VLfW09",
            },
            trading_partner_name="tradingPartnerName",
        )
        assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_submit(self, client: SampleHealthcare) -> None:
        response = client.v2.clearinghouse.claim.with_raw_response.submit(
            billing={},
            claim_information={
                "benefits_assignment_certification_indicator": "N",
                "claim_charge_amount": "321669910225",
                "claim_filing_code": "11",
                "claim_frequency_code": "1",
                "health_care_code_information": [
                    {
                        "diagnosis_code": "diagnosisCode",
                        "diagnosis_type_code": "BK",
                    }
                ],
                "place_of_service_code": "01",
                "plan_participation_code": "A",
                "release_information_code": "I",
                "service_lines": [
                    {
                        "professional_service": {
                            "composite_diagnosis_code_pointers": {"diagnosis_code_pointers": ["string"]},
                            "line_item_charge_amount": "321669910225",
                            "measurement_unit": "MJ",
                            "procedure_code": "procedureCode",
                            "procedure_identifier": "ER",
                            "service_unit_count": "serviceUnitCount",
                        },
                        "service_date": "73210630",
                    }
                ],
                "signature_indicator": "N",
            },
            is_testing=True,
            receiver={"organization_name": "x"},
            submitter={"contact_information": {}},
            subscriber={},
            trading_partner_service_id="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        claim = response.parse()
        assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_submit(self, client: SampleHealthcare) -> None:
        with client.v2.clearinghouse.claim.with_streaming_response.submit(
            billing={},
            claim_information={
                "benefits_assignment_certification_indicator": "N",
                "claim_charge_amount": "321669910225",
                "claim_filing_code": "11",
                "claim_frequency_code": "1",
                "health_care_code_information": [
                    {
                        "diagnosis_code": "diagnosisCode",
                        "diagnosis_type_code": "BK",
                    }
                ],
                "place_of_service_code": "01",
                "plan_participation_code": "A",
                "release_information_code": "I",
                "service_lines": [
                    {
                        "professional_service": {
                            "composite_diagnosis_code_pointers": {"diagnosis_code_pointers": ["string"]},
                            "line_item_charge_amount": "321669910225",
                            "measurement_unit": "MJ",
                            "procedure_code": "procedureCode",
                            "procedure_identifier": "ER",
                            "service_unit_count": "serviceUnitCount",
                        },
                        "service_date": "73210630",
                    }
                ],
                "signature_indicator": "N",
            },
            is_testing=True,
            receiver={"organization_name": "x"},
            submitter={"contact_information": {}},
            subscriber={},
            trading_partner_service_id="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            claim = response.parse()
            assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncClaim:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cancel(self, async_client: AsyncSampleHealthcare) -> None:
        claim = await async_client.v2.clearinghouse.claim.cancel(
            "claimId",
        )
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.clearinghouse.claim.with_raw_response.cancel(
            "claimId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        claim = await response.parse()
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.clearinghouse.claim.with_streaming_response.cancel(
            "claimId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            claim = await response.parse()
            assert_matches_type(object, claim, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `claim_id` but received ''"):
            await async_client.v2.clearinghouse.claim.with_raw_response.cancel(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_status(self, async_client: AsyncSampleHealthcare) -> None:
        claim = await async_client.v2.clearinghouse.claim.retrieve_status(
            "claimId",
        )
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_status(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.clearinghouse.claim.with_raw_response.retrieve_status(
            "claimId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        claim = await response.parse()
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_status(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.clearinghouse.claim.with_streaming_response.retrieve_status(
            "claimId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            claim = await response.parse()
            assert_matches_type(object, claim, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_status(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `claim_id` but received ''"):
            await async_client.v2.clearinghouse.claim.with_raw_response.retrieve_status(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_submit(self, async_client: AsyncSampleHealthcare) -> None:
        claim = await async_client.v2.clearinghouse.claim.submit(
            billing={},
            claim_information={
                "benefits_assignment_certification_indicator": "N",
                "claim_charge_amount": "321669910225",
                "claim_filing_code": "11",
                "claim_frequency_code": "1",
                "health_care_code_information": [
                    {
                        "diagnosis_code": "diagnosisCode",
                        "diagnosis_type_code": "BK",
                    }
                ],
                "place_of_service_code": "01",
                "plan_participation_code": "A",
                "release_information_code": "I",
                "service_lines": [
                    {
                        "professional_service": {
                            "composite_diagnosis_code_pointers": {"diagnosis_code_pointers": ["string"]},
                            "line_item_charge_amount": "321669910225",
                            "measurement_unit": "MJ",
                            "procedure_code": "procedureCode",
                            "procedure_identifier": "ER",
                            "service_unit_count": "serviceUnitCount",
                        },
                        "service_date": "73210630",
                    }
                ],
                "signature_indicator": "N",
            },
            is_testing=True,
            receiver={"organization_name": "x"},
            submitter={"contact_information": {}},
            subscriber={},
            trading_partner_service_id="x",
        )
        assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_submit_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        claim = await async_client.v2.clearinghouse.claim.submit(
            billing={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "commercial_number": "commercialNumber",
                "contact_information": {
                    "email": "email",
                    "fax_number": "faxNumber",
                    "name": "name",
                    "phone_extension": "phoneExtension",
                    "phone_number": "phoneNumber",
                },
                "employer_id": "employerId",
                "first_name": "firstName",
                "last_name": "lastName",
                "location_number": "locationNumber",
                "middle_name": "middleName",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "provider_type": "providerType",
                "provider_upin_number": "providerUpinNumber",
                "ssn": "732166991",
                "state_license_number": "stateLicenseNumber",
                "suffix": "suffix",
                "taxonomy_code": "2E02VLfW09",
            },
            claim_information={
                "benefits_assignment_certification_indicator": "N",
                "claim_charge_amount": "321669910225",
                "claim_filing_code": "11",
                "claim_frequency_code": "1",
                "health_care_code_information": [
                    {
                        "diagnosis_code": "diagnosisCode",
                        "diagnosis_type_code": "BK",
                    }
                ],
                "place_of_service_code": "01",
                "plan_participation_code": "A",
                "release_information_code": "I",
                "service_lines": [
                    {
                        "professional_service": {
                            "composite_diagnosis_code_pointers": {"diagnosis_code_pointers": ["string"]},
                            "line_item_charge_amount": "321669910225",
                            "measurement_unit": "MJ",
                            "procedure_code": "procedureCode",
                            "procedure_identifier": "ER",
                            "service_unit_count": "serviceUnitCount",
                            "copay_status_code": "0",
                            "description": "x",
                            "emergency_indicator": "Y",
                            "epsdt_indicator": "Y",
                            "family_planning_indicator": "Y",
                            "place_of_service_code": "placeOfServiceCode",
                            "procedure_modifiers": ["string"],
                        },
                        "service_date": "73210630",
                        "additional_notes": "additionalNotes",
                        "ambulance_certification": [
                            {
                                "certification_condition_indicator": "N",
                                "condition_codes": ["01"],
                            }
                        ],
                        "ambulance_drop_off_location": {
                            "address1": "address1",
                            "city": "city",
                            "address2": "address2",
                            "country_code": "countryCode",
                            "country_sub_division_code": "countrySubDivisionCode",
                            "postal_code": "postalCode",
                            "state": "state",
                        },
                        "ambulance_patient_count": 0,
                        "ambulance_pick_up_location": {
                            "address1": "address1",
                            "city": "city",
                            "address2": "address2",
                            "country_code": "countryCode",
                            "country_sub_division_code": "countrySubDivisionCode",
                            "postal_code": "postalCode",
                            "state": "state",
                        },
                        "ambulance_transport_information": {
                            "ambulance_transport_reason_code": "A",
                            "transport_distance_in_miles": "transportDistanceInMiles",
                            "patient_weight_in_pounds": "patientWeightInPounds",
                            "round_trip_purpose_description": "roundTripPurposeDescription",
                            "stretcher_purpose_description": "stretcherPurposeDescription",
                        },
                        "assigned_number": "assignedNumber",
                        "condition_indicator_durable_medical_equipment": {
                            "certification_condition_indicator": "Y",
                            "condition_indicator": "38",
                            "condition_indicator_code": "38",
                        },
                        "contract_information": {
                            "contract_type_code": "01",
                            "contract_amount": "321669910225",
                            "contract_code": "contractCode",
                            "contract_percentage": "contractPercentage",
                            "contract_version_identifier": "contractVersionIdentifier",
                            "terms_discount_percentage": "termsDiscountPercentage",
                        },
                        "drug_identification": {
                            "measurement_unit_code": "F2",
                            "national_drug_code": "nationalDrugCode",
                            "national_drug_unit_count": "nationalDrugUnitCount",
                            "service_id_qualifier": "EN",
                            "link_sequence_number": "linkSequenceNumber",
                            "pharmacy_prescription_number": "pharmacyPrescriptionNumber",
                        },
                        "durable_medical_equipment_certificate_of_medical_necessity": {
                            "attachment_transmission_code": "AB"
                        },
                        "durable_medical_equipment_certification": {
                            "certification_type_code": "I",
                            "durable_medical_equipment_duration_in_months": "durableMedicalEquipmentDurationInMonths",
                        },
                        "durable_medical_equipment_service": {
                            "days": "days",
                            "frequency_code": "1",
                            "purchase_price": "purchasePrice",
                            "rental_price": "rentalPrice",
                        },
                        "file_information": ["string"],
                        "form_identification": [
                            {
                                "form_identifier": "formIdentifier",
                                "form_type_code": "AS",
                                "supporting_documentation": [
                                    {
                                        "question_number": "questionNumber",
                                        "question_response": "questionResponse",
                                        "question_response_as_date": "questionResponseAsDate",
                                        "question_response_as_percent": "questionResponseAsPercent",
                                        "question_response_code": "N",
                                    }
                                ],
                            }
                        ],
                        "goal_rehab_or_discharge_plans": "goalRehabOrDischargePlans",
                        "hospice_employee_indicator": True,
                        "line_adjudication_information": [
                            {
                                "adjudication_or_payment_date": "73210630",
                                "other_payer_primary_identifier": "otherPayerPrimaryIdentifier",
                                "paid_service_unit_count": "paidServiceUnitCount",
                                "procedure_code": "procedureCode",
                                "service_id_qualifier": "ER",
                                "service_line_paid_amount": "321669910225",
                                "bundled_or_unbundled_line_number": "bundledOrUnbundledLineNumber",
                                "claim_adjustment_information": [
                                    {
                                        "adjustment_details": [
                                            {
                                                "adjustment_amount": "321669910225",
                                                "adjustment_reason_code": "adjustmentReasonCode",
                                                "adjustment_quantity": "adjustmentQuantity",
                                            }
                                        ],
                                        "adjustment_group_code": "CO",
                                    }
                                ],
                                "procedure_code_description": "procedureCodeDescription",
                                "procedure_modifier": ["string"],
                                "remaining_patient_liability": "321669910225",
                            }
                        ],
                        "line_pricing_repricing_information": {
                            "pricing_methodology_code": "00",
                            "repriced_allowed_amount": "321669910225",
                            "exception_code": "1",
                            "policy_compliance_code": "1",
                            "reject_reason_code": "T1",
                            "repriced_approved_ambulatory_patient_group_amount": "321669910225",
                            "repriced_approved_ambulatory_patient_group_code": "repricedApprovedAmbulatoryPatientGroupCode",
                            "repriced_saving_amount": "321669910225",
                            "repricing_organization_identifier": "repricingOrganizationIdentifier",
                            "repricing_per_diem_or_flat_rate_amount": "repricingPerDiemOrFlatRateAmount",
                        },
                        "obstetric_anesthesia_additional_units": 0,
                        "ordering_provider": {
                            "address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "countryCode",
                                "country_sub_division_code": "countrySubDivisionCode",
                                "postal_code": "postalCode",
                                "state": "state",
                            },
                            "claim_office_number": "claimOfficeNumber",
                            "commercial_number": "commercialNumber",
                            "contact_information": {
                                "name": "name",
                                "email": "email",
                                "fax_number": "faxNumber",
                                "phone_extension": "phoneExtension",
                                "phone_number": "phoneNumber",
                            },
                            "employer_id": "employerId",
                            "employer_identification_number": "employerIdentificationNumber",
                            "first_name": "firstName",
                            "last_name": "lastName",
                            "location_number": "locationNumber",
                            "middle_name": "middleName",
                            "naic": "naic",
                            "npi": "7321669910",
                            "organization_name": "organizationName",
                            "other_identifier": "otherIdentifier",
                            "payer_identification_number": "payerIdentificationNumber",
                            "provider_type": "providerType",
                            "provider_upin_number": "providerUpinNumber",
                            "secondary_identifier": [
                                {
                                    "identifier": "identifier",
                                    "qualifier": "qualifier",
                                    "other_identifier": "otherIdentifier",
                                }
                            ],
                            "ssn": "732166991",
                            "state_license_number": "stateLicenseNumber",
                            "suffix": "suffix",
                            "taxonomy_code": "2E02VLfW09",
                        },
                        "postage_tax_amount": "321669910225",
                        "purchased_service_information": {
                            "purchased_service_charge_amount": "purchasedServiceChargeAmount",
                            "purchased_service_provider_identifier": "purchasedServiceProviderIdentifier",
                        },
                        "purchased_service_provider": {
                            "address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "countryCode",
                                "country_sub_division_code": "countrySubDivisionCode",
                                "postal_code": "postalCode",
                                "state": "state",
                            },
                            "claim_office_number": "claimOfficeNumber",
                            "commercial_number": "commercialNumber",
                            "contact_information": {
                                "email": "email",
                                "fax_number": "faxNumber",
                                "name": "name",
                                "phone_extension": "phoneExtension",
                                "phone_number": "phoneNumber",
                            },
                            "employer_id": "employerId",
                            "employer_identification_number": "employerIdentificationNumber",
                            "first_name": "firstName",
                            "last_name": "lastName",
                            "location_number": "locationNumber",
                            "middle_name": "middleName",
                            "naic": "naic",
                            "npi": "7321669910",
                            "organization_name": "organizationName",
                            "other_identifier": "otherIdentifier",
                            "payer_identification_number": "payerIdentificationNumber",
                            "provider_type": "providerType",
                            "provider_upin_number": "providerUpinNumber",
                            "secondary_identifier": [
                                {
                                    "identifier": "identifier",
                                    "qualifier": "qualifier",
                                    "other_identifier": "otherIdentifier",
                                }
                            ],
                            "ssn": "732166991",
                            "state_license_number": "stateLicenseNumber",
                            "suffix": "suffix",
                            "taxonomy_code": "2E02VLfW09",
                        },
                        "referring_provider": {
                            "provider_type": "providerType",
                            "address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "countryCode",
                                "country_sub_division_code": "countrySubDivisionCode",
                                "postal_code": "postalCode",
                                "state": "state",
                            },
                            "claim_office_number": "claimOfficeNumber",
                            "commercial_number": "commercialNumber",
                            "contact_information": {
                                "email": "email",
                                "fax_number": "faxNumber",
                                "name": "name",
                                "phone_extension": "phoneExtension",
                                "phone_number": "phoneNumber",
                            },
                            "employer_id": "employerId",
                            "employer_identification_number": "employerIdentificationNumber",
                            "first_name": "firstName",
                            "last_name": "lastName",
                            "location_number": "locationNumber",
                            "middle_name": "middleName",
                            "naic": "naic",
                            "npi": "7321669910",
                            "organization_name": "organizationName",
                            "other_identifier": "otherIdentifier",
                            "payer_identification_number": "payerIdentificationNumber",
                            "provider_upin_number": "providerUpinNumber",
                            "secondary_identifier": [
                                {
                                    "identifier": "identifier",
                                    "qualifier": "qualifier",
                                    "other_identifier": "otherIdentifier",
                                }
                            ],
                            "ssn": "732166991",
                            "state_license_number": "stateLicenseNumber",
                            "suffix": "suffix",
                            "taxonomy_code": "2E02VLfW09",
                        },
                        "rendering_provider": {
                            "provider_type": "providerType",
                            "address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "countryCode",
                                "country_sub_division_code": "countrySubDivisionCode",
                                "postal_code": "postalCode",
                                "state": "state",
                            },
                            "claim_office_number": "claimOfficeNumber",
                            "commercial_number": "commercialNumber",
                            "contact_information": {
                                "email": "email",
                                "fax_number": "faxNumber",
                                "name": "name",
                                "phone_extension": "phoneExtension",
                                "phone_number": "phoneNumber",
                            },
                            "employer_id": "employerId",
                            "employer_identification_number": "employerIdentificationNumber",
                            "first_name": "firstName",
                            "last_name": "lastName",
                            "location_number": "locationNumber",
                            "middle_name": "middleName",
                            "naic": "naic",
                            "npi": "7321669910",
                            "organization_name": "organizationName",
                            "other_identifier": "otherIdentifier",
                            "payer_identification_number": "payerIdentificationNumber",
                            "provider_upin_number": "providerUpinNumber",
                            "secondary_identifier": [
                                {
                                    "identifier": "identifier",
                                    "qualifier": "qualifier",
                                    "other_identifier": "otherIdentifier",
                                }
                            ],
                            "ssn": "732166991",
                            "state_license_number": "stateLicenseNumber",
                            "suffix": "suffix",
                            "taxonomy_code": "2E02VLfW09",
                        },
                        "sales_tax_amount": "salesTaxAmount",
                        "service_date_end": "73210630",
                        "service_facility_location": {
                            "address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "countryCode",
                                "country_sub_division_code": "countrySubDivisionCode",
                                "postal_code": "postalCode",
                                "state": "state",
                            },
                            "organization_name": "organizationName",
                            "npi": "7321669910",
                            "phone_extension": "phoneExtension",
                            "phone_name": "phoneName",
                            "phone_number": "phoneNumber",
                            "secondary_identifier": [
                                {
                                    "identifier": "identifier",
                                    "qualifier": "qualifier",
                                    "other_identifier": "otherIdentifier",
                                }
                            ],
                        },
                        "service_line_date_information": {
                            "begin_therapy_date": "73210630",
                            "certification_revision_or_recertification_date": "73210630",
                            "hemoglobin_test_date": "73210630",
                            "initial_treatment_date": "73210630",
                            "last_certification_date": "73210630",
                            "last_x_ray_date": "73210630",
                            "prescription_date": "73210630",
                            "serum_creatine_test_date": "73210630",
                            "shipped_date": "73210630",
                            "treatment_or_therapy_date": "73210630",
                        },
                        "service_line_reference_information": {
                            "adjusted_repriced_line_item_reference_number": "adjustedRepricedLineItemReferenceNumber",
                            "clinical_laboratory_improvement_amendment_number": "clinicalLaboratoryImprovementAmendmentNumber",
                            "immunization_batch_number": "immunizationBatchNumber",
                            "mammography_certification_number": "mammographyCertificationNumber",
                            "prior_authorization": [
                                {
                                    "prior_authorization_or_referral_number": "priorAuthorizationOrReferralNumber",
                                    "other_payer_primary_identifier": "otherPayerPrimaryIdentifier",
                                }
                            ],
                            "referral_number": ["string"],
                            "referring_clia_number": "referringCliaNumber",
                            "repriced_line_item_reference_number": "repricedLineItemReferenceNumber",
                        },
                        "service_line_supplemental_information": [
                            {
                                "attachment_report_type_code": "03",
                                "attachment_transmission_code": "AA",
                                "attachment_control_number": "attachmentControlNumber",
                            }
                        ],
                        "supervising_provider": {
                            "provider_type": "providerType",
                            "address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "countryCode",
                                "country_sub_division_code": "countrySubDivisionCode",
                                "postal_code": "postalCode",
                                "state": "state",
                            },
                            "claim_office_number": "claimOfficeNumber",
                            "commercial_number": "commercialNumber",
                            "contact_information": {
                                "email": "email",
                                "fax_number": "faxNumber",
                                "name": "name",
                                "phone_extension": "phoneExtension",
                                "phone_number": "phoneNumber",
                            },
                            "employer_id": "employerId",
                            "employer_identification_number": "employerIdentificationNumber",
                            "first_name": "firstName",
                            "last_name": "lastName",
                            "location_number": "locationNumber",
                            "middle_name": "middleName",
                            "naic": "naic",
                            "npi": "7321669910",
                            "organization_name": "organizationName",
                            "other_identifier": "otherIdentifier",
                            "payer_identification_number": "payerIdentificationNumber",
                            "provider_upin_number": "providerUpinNumber",
                            "secondary_identifier": [
                                {
                                    "identifier": "identifier",
                                    "qualifier": "qualifier",
                                    "other_identifier": "otherIdentifier",
                                }
                            ],
                            "ssn": "732166991",
                            "state_license_number": "stateLicenseNumber",
                            "suffix": "suffix",
                            "taxonomy_code": "2E02VLfW09",
                        },
                        "test_results": [
                            {
                                "measurement_qualifier": "HT",
                                "measurement_reference_identification_code": "OG",
                                "test_results": "testResults",
                            }
                        ],
                        "third_party_organization_notes": "thirdPartyOrganizationNotes",
                    }
                ],
                "signature_indicator": "N",
                "ambulance_certification": [
                    {
                        "certification_condition_indicator": "N",
                        "condition_codes": ["01"],
                    }
                ],
                "ambulance_drop_off_location": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "ambulance_pick_up_location": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "ambulance_transport_information": {
                    "ambulance_transport_reason_code": "A",
                    "transport_distance_in_miles": "transportDistanceInMiles",
                    "patient_weight_in_pounds": "patientWeightInPounds",
                    "round_trip_purpose_description": "roundTripPurposeDescription",
                    "stretcher_purpose_description": "stretcherPurposeDescription",
                },
                "anesthesia_related_surgical_procedure": ["string"],
                "auto_accident_country_code": "autoAccidentCountryCode",
                "auto_accident_state_code": "autoAccidentStateCode",
                "claim_contract_information": {
                    "contract_type_code": "01",
                    "contract_amount": "321669910225",
                    "contract_code": "contractCode",
                    "contract_percentage": "contractPercentage",
                    "contract_version_identifier": "contractVersionIdentifier",
                    "terms_discount_percentage": "termsDiscountPercentage",
                },
                "claim_date_information": {
                    "accident_date": "accidentDate",
                    "acute_manifestation_date": "acuteManifestationDate",
                    "admission_date": "admissionDate",
                    "assumed_and_relinquished_care_begin_date": "assumedAndRelinquishedCareBeginDate",
                    "assumed_and_relinquished_care_end_date": "assumedAndRelinquishedCareEndDate",
                    "authorized_return_to_work_date": "authorizedReturnToWorkDate",
                    "disability_begin_date": "disabilityBeginDate",
                    "disability_end_date": "disabilityEndDate",
                    "discharge_date": "dischargeDate",
                    "first_contact_date": "firstContactDate",
                    "hearing_and_vision_prescription_date": "hearingAndVisionPrescriptionDate",
                    "initial_treatment_date": "initialTreatmentDate",
                    "last_menstrual_period_date": "lastMenstrualPeriodDate",
                    "last_seen_date": "lastSeenDate",
                    "last_worked_date": "lastWorkedDate",
                    "last_x_ray_date": "lastXRayDate",
                    "repricer_received_date": "repricerReceivedDate",
                    "symptom_date": "symptomDate",
                },
                "claim_note": {
                    "additional_information": "additionalInformation",
                    "certification_narrative": "certificationNarrative",
                    "diagnosis_description": "diagnosisDescription",
                    "goal_rehab_or_discharge_plans": "goalRehabOrDischargePlans",
                    "third_part_org_notes": "thirdPartOrgNotes",
                },
                "claim_pricing_repricing_information": {
                    "pricing_methodology_code": "00",
                    "repriced_allowed_amount": "321669910225",
                    "exception_code": "1",
                    "policy_compliance_code": "1",
                    "reject_reason_code": "T1",
                    "repriced_approved_ambulatory_patient_group_amount": "321669910225",
                    "repriced_approved_ambulatory_patient_group_code": "repricedApprovedAmbulatoryPatientGroupCode",
                    "repriced_saving_amount": "321669910225",
                    "repricing_organization_identifier": "repricingOrganizationIdentifier",
                    "repricing_per_diem_or_flat_rate_amount": "repricingPerDiemOrFlatRateAmount",
                },
                "claim_supplemental_information": {
                    "adjusted_repriced_claim_number": "adjustedRepricedClaimNumber",
                    "care_plan_oversight_number": "carePlanOversightNumber",
                    "claim_control_number": "claimControlNumber",
                    "claim_number": "claimNumber",
                    "clia_number": "cliaNumber",
                    "demo_project_identifier": "demoProjectIdentifier",
                    "investigational_device_exemption_number": "investigationalDeviceExemptionNumber",
                    "mammography_certification_number": "mammographyCertificationNumber",
                    "medical_record_number": "medicalRecordNumber",
                    "medicare_crossover_reference_id": "medicareCrossoverReferenceId",
                    "prior_authorization_number": "priorAuthorizationNumber",
                    "referral_number": "referralNumber",
                    "report_information": {
                        "attachment_report_type_code": "03",
                        "attachment_transmission_code": "AA",
                        "attachment_control_number": "attachmentControlNumber",
                    },
                    "report_informations": [
                        {
                            "attachment_report_type_code": "03",
                            "attachment_transmission_code": "AA",
                            "attachment_control_number": "attachmentControlNumber",
                        }
                    ],
                    "repriced_claim_number": "repricedClaimNumber",
                    "service_authorization_exception_code": "1",
                },
                "condition_information": [{"condition_codes": ["string"]}],
                "death_date": "73210630",
                "delay_reason_code": "1",
                "epsdt_referral": {
                    "certification_condition_code_applies_indicator": "N",
                    "condition_codes": ["AV"],
                },
                "file_information": "fileInformation",
                "file_information_list": ["string"],
                "homebound_indicator": True,
                "other_subscriber_information": [
                    {
                        "benefits_assignment_certification_indicator": "N",
                        "claim_filing_indicator_code": "11",
                        "individual_relationship_code": "01",
                        "other_payer_name": {
                            "other_payer_identifier": "otherPayerIdentifier",
                            "other_payer_identifier_type_code": "PI",
                            "other_payer_organization_name": "otherPayerOrganizationName",
                            "other_payer_address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "countryCode",
                                "country_sub_division_code": "countrySubDivisionCode",
                                "postal_code": "postalCode",
                                "state": "state",
                            },
                            "other_payer_adjudication_or_payment_date": "otherPayerAdjudicationOrPaymentDate",
                            "other_payer_claim_adjustment_indicator": True,
                            "other_payer_claim_control_number": "otherPayerClaimControlNumber",
                            "other_payer_prior_authorization_number": "otherPayerPriorAuthorizationNumber",
                            "other_payer_prior_authorization_or_referral_number": "otherPayerPriorAuthorizationOrReferralNumber",
                            "other_payer_secondary_identifier": [
                                {
                                    "identifier": "identifier",
                                    "qualifier": "qualifier",
                                    "other_identifier": "otherIdentifier",
                                }
                            ],
                        },
                        "other_subscriber_name": {
                            "other_insured_identifier": "otherInsuredIdentifier",
                            "other_insured_identifier_type_code": "II",
                            "other_insured_last_name": "otherInsuredLastName",
                            "other_insured_qualifier": "1",
                            "other_insured_additional_identifier": "otherInsuredAdditionalIdentifier",
                            "other_insured_address": {
                                "address1": "address1",
                                "city": "city",
                                "address2": "address2",
                                "country_code": "countryCode",
                                "country_sub_division_code": "countrySubDivisionCode",
                                "postal_code": "postalCode",
                                "state": "state",
                            },
                            "other_insured_first_name": "otherInsuredFirstName",
                            "other_insured_middle_name": "otherInsuredMiddleName",
                            "other_insured_name_suffix": "otherInsuredNameSuffix",
                        },
                        "payment_responsibility_level_code": "A",
                        "release_of_information_code": "I",
                        "claim_level_adjustments": [
                            {
                                "adjustment_details": [
                                    {
                                        "adjustment_amount": "321669910225",
                                        "adjustment_reason_code": "adjustmentReasonCode",
                                        "adjustment_quantity": "adjustmentQuantity",
                                    }
                                ],
                                "adjustment_group_code": "CO",
                            }
                        ],
                        "insurance_group_or_policy_number": "insuranceGroupOrPolicyNumber",
                        "insurance_type_code": "12",
                        "medicare_outpatient_adjudication": {
                            "claim_payment_remark_code": ["string"],
                            "end_stage_renal_disease_payment_amount": "321669910225",
                            "hcpcs_payable_amount": "321669910225",
                            "non_payable_professional_component_billed_amount": "321669910225",
                            "reimbursement_rate": "reimbursementRate",
                        },
                        "non_covered_charge_amount": "321669910225",
                        "other_insured_group_name": "otherInsuredGroupName",
                        "other_payer_billing_provider": [
                            {
                                "entity_type_qualifier": "1",
                                "other_payer_billing_provider_identifier": [
                                    {
                                        "identifier": "identifier",
                                        "qualifier": "qualifier",
                                        "other_identifier": "otherIdentifier",
                                    }
                                ],
                            }
                        ],
                        "other_payer_referring_provider": [
                            {
                                "other_payer_referring_provider_identifier": [
                                    {
                                        "identifier": "identifier",
                                        "qualifier": "qualifier",
                                        "other_identifier": "otherIdentifier",
                                    }
                                ]
                            }
                        ],
                        "other_payer_rendering_provider": [
                            {
                                "entity_type_qualifier": "1",
                                "other_payer_rendering_provider_secondary_identifier": [
                                    {
                                        "identifier": "identifier",
                                        "qualifier": "qualifier",
                                        "other_identifier": "otherIdentifier",
                                    }
                                ],
                            }
                        ],
                        "other_payer_service_facility_location": [
                            {
                                "other_payer_service_facility_location_secondary_identifier": [
                                    {
                                        "identifier": "identifier",
                                        "qualifier": "qualifier",
                                        "other_identifier": "otherIdentifier",
                                    }
                                ]
                            }
                        ],
                        "other_payer_supervising_provider": [
                            {
                                "other_payer_supervising_provider_identifier": [
                                    {
                                        "identifier": "identifier",
                                        "qualifier": "qualifier",
                                        "other_identifier": "otherIdentifier",
                                    }
                                ]
                            }
                        ],
                        "patient_signature_generated_for_patient": True,
                        "payer_paid_amount": "321669910225",
                        "remaining_patient_liability": "321669910225",
                    }
                ],
                "patient_amount_paid": "321669910225",
                "patient_condition_information_vision": [
                    {
                        "certification_condition_indicator": "N",
                        "code_category": "E1",
                        "condition_codes": ["L1"],
                    }
                ],
                "patient_signature_source_code": True,
                "patient_weight": "patientWeight",
                "pregnancy_indicator": "Y",
                "property_casualty_claim_number": "propertyCasualtyClaimNumber",
                "related_causes_code": ["AA"],
                "service_facility_location": {
                    "address": {
                        "address1": "address1",
                        "city": "city",
                        "address2": "address2",
                        "country_code": "countryCode",
                        "country_sub_division_code": "countrySubDivisionCode",
                        "postal_code": "postalCode",
                        "state": "state",
                    },
                    "organization_name": "organizationName",
                    "npi": "7321669910",
                    "phone_extension": "phoneExtension",
                    "phone_name": "phoneName",
                    "phone_number": "phoneNumber",
                    "secondary_identifier": [
                        {
                            "identifier": "identifier",
                            "qualifier": "qualifier",
                            "other_identifier": "otherIdentifier",
                        }
                    ],
                },
                "special_program_code": "02",
                "spinal_manipulation_service_information": {
                    "patient_condition_code": "patientConditionCode",
                    "patient_condition_description1": "A",
                    "patient_condition_description2": "patientConditionDescription2",
                },
            },
            is_testing=True,
            receiver={"organization_name": "x"},
            submitter={
                "contact_information": {
                    "email": "email",
                    "fax_number": "faxNumber",
                    "name": "name",
                    "phone_extension": "phoneExtension",
                    "phone_number": "phoneNumber",
                },
                "first_name": "x",
                "last_name": "x",
                "middle_name": "x",
                "organization_name": "x",
                "submitter_identification": "xx",
            },
            subscriber={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "contact_information": {
                    "name": "name",
                    "email": "email",
                    "fax_number": "faxNumber",
                    "phone_extension": "phoneExtension",
                    "phone_number": "phoneNumber",
                },
                "date_of_birth": "73210630",
                "first_name": "firstName",
                "gender": "M",
                "group_number": "groupNumber",
                "insurance_type_code": "12",
                "last_name": "lastName",
                "member_id": "xx",
                "middle_name": "middleName",
                "organization_name": "organizationName",
                "payment_responsibility_level_code": "A",
                "policy_number": "policyNumber",
                "ssn": "732166991",
                "subscriber_group_name": "subscriberGroupName",
                "suffix": "suffix",
            },
            trading_partner_service_id="x",
            control_number="controlNumber",
            dependent={
                "date_of_birth": "73210630",
                "first_name": "firstName",
                "gender": "M",
                "last_name": "lastName",
                "relationship_to_subscriber_code": "01",
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "contact_information": {
                    "name": "name",
                    "email": "email",
                    "fax_number": "faxNumber",
                    "phone_extension": "phoneExtension",
                    "phone_number": "phoneNumber",
                },
                "member_id": "memberId",
                "middle_name": "middleName",
                "ssn": "732166991",
                "suffix": "suffix",
            },
            ordering={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "claim_office_number": "claimOfficeNumber",
                "commercial_number": "commercialNumber",
                "contact_information": {
                    "email": "email",
                    "fax_number": "faxNumber",
                    "name": "name",
                    "phone_extension": "phoneExtension",
                    "phone_number": "phoneNumber",
                },
                "employer_id": "employerId",
                "employer_identification_number": "employerIdentificationNumber",
                "first_name": "firstName",
                "last_name": "lastName",
                "location_number": "locationNumber",
                "middle_name": "middleName",
                "naic": "naic",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "payer_identification_number": "payerIdentificationNumber",
                "provider_type": "providerType",
                "provider_upin_number": "providerUpinNumber",
                "ssn": "732166991",
                "state_license_number": "stateLicenseNumber",
                "suffix": "suffix",
                "taxonomy_code": "2E02VLfW09",
            },
            payer_address={
                "address1": "address1",
                "city": "city",
                "address2": "address2",
                "country_code": "countryCode",
                "country_sub_division_code": "countrySubDivisionCode",
                "postal_code": "postalCode",
                "state": "state",
            },
            pay_to_address={
                "address1": "address1",
                "city": "city",
                "address2": "address2",
                "country_code": "countryCode",
                "country_sub_division_code": "countrySubDivisionCode",
                "postal_code": "postalCode",
                "state": "state",
            },
            pay_to_plan={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "organization_name": "organizationName",
                "primary_identifier": "primaryIdentifier",
                "primary_identifier_type_code": "PI",
                "tax_identification_number": "xxxxxxxxx",
                "secondary_identifier": "secondaryIdentifier",
                "secondary_identifier_type_code": "2U",
            },
            providers=[
                {
                    "address": {
                        "address1": "address1",
                        "city": "city",
                        "address2": "address2",
                        "country_code": "countryCode",
                        "country_sub_division_code": "countrySubDivisionCode",
                        "postal_code": "postalCode",
                        "state": "state",
                    },
                    "commercial_number": "commercialNumber",
                    "contact_information": {
                        "email": "email",
                        "fax_number": "faxNumber",
                        "name": "name",
                        "phone_extension": "phoneExtension",
                        "phone_number": "phoneNumber",
                    },
                    "employer_id": "employerId",
                    "first_name": "firstName",
                    "last_name": "lastName",
                    "location_number": "locationNumber",
                    "middle_name": "middleName",
                    "npi": "7321669910",
                    "organization_name": "organizationName",
                    "provider_type": "providerType",
                    "provider_upin_number": "providerUpinNumber",
                    "ssn": "732166991",
                    "state_license_number": "stateLicenseNumber",
                    "suffix": "suffix",
                    "taxonomy_code": "2E02VLfW09",
                }
            ],
            referring={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "commercial_number": "commercialNumber",
                "contact_information": {
                    "email": "email",
                    "fax_number": "faxNumber",
                    "name": "name",
                    "phone_extension": "phoneExtension",
                    "phone_number": "phoneNumber",
                },
                "first_name": "firstName",
                "last_name": "lastName",
                "middle_name": "middleName",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "provider_type": "providerType",
                "provider_upin_number": "providerUpinNumber",
                "state_license_number": "stateLicenseNumber",
                "suffix": "suffix",
                "taxonomy_code": "2E02VLfW09",
            },
            rendering={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "commercial_number": "commercialNumber",
                "contact_information": {
                    "email": "email",
                    "fax_number": "faxNumber",
                    "name": "name",
                    "phone_extension": "phoneExtension",
                    "phone_number": "phoneNumber",
                },
                "first_name": "firstName",
                "last_name": "lastName",
                "location_number": "locationNumber",
                "middle_name": "middleName",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "provider_type": "providerType",
                "provider_upin_number": "providerUpinNumber",
                "state_license_number": "stateLicenseNumber",
                "suffix": "suffix",
                "taxonomy_code": "2E02VLfW09",
            },
            supervising={
                "address": {
                    "address1": "address1",
                    "city": "city",
                    "address2": "address2",
                    "country_code": "countryCode",
                    "country_sub_division_code": "countrySubDivisionCode",
                    "postal_code": "postalCode",
                    "state": "state",
                },
                "commercial_number": "commercialNumber",
                "contact_information": {
                    "email": "email",
                    "fax_number": "faxNumber",
                    "name": "name",
                    "phone_extension": "phoneExtension",
                    "phone_number": "phoneNumber",
                },
                "employer_id": "employerId",
                "first_name": "firstName",
                "last_name": "lastName",
                "location_number": "locationNumber",
                "middle_name": "middleName",
                "npi": "7321669910",
                "organization_name": "organizationName",
                "provider_type": "providerType",
                "provider_upin_number": "providerUpinNumber",
                "ssn": "732166991",
                "state_license_number": "stateLicenseNumber",
                "suffix": "suffix",
                "taxonomy_code": "2E02VLfW09",
            },
            trading_partner_name="tradingPartnerName",
        )
        assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_submit(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.clearinghouse.claim.with_raw_response.submit(
            billing={},
            claim_information={
                "benefits_assignment_certification_indicator": "N",
                "claim_charge_amount": "321669910225",
                "claim_filing_code": "11",
                "claim_frequency_code": "1",
                "health_care_code_information": [
                    {
                        "diagnosis_code": "diagnosisCode",
                        "diagnosis_type_code": "BK",
                    }
                ],
                "place_of_service_code": "01",
                "plan_participation_code": "A",
                "release_information_code": "I",
                "service_lines": [
                    {
                        "professional_service": {
                            "composite_diagnosis_code_pointers": {"diagnosis_code_pointers": ["string"]},
                            "line_item_charge_amount": "321669910225",
                            "measurement_unit": "MJ",
                            "procedure_code": "procedureCode",
                            "procedure_identifier": "ER",
                            "service_unit_count": "serviceUnitCount",
                        },
                        "service_date": "73210630",
                    }
                ],
                "signature_indicator": "N",
            },
            is_testing=True,
            receiver={"organization_name": "x"},
            submitter={"contact_information": {}},
            subscriber={},
            trading_partner_service_id="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        claim = await response.parse()
        assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_submit(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.clearinghouse.claim.with_streaming_response.submit(
            billing={},
            claim_information={
                "benefits_assignment_certification_indicator": "N",
                "claim_charge_amount": "321669910225",
                "claim_filing_code": "11",
                "claim_frequency_code": "1",
                "health_care_code_information": [
                    {
                        "diagnosis_code": "diagnosisCode",
                        "diagnosis_type_code": "BK",
                    }
                ],
                "place_of_service_code": "01",
                "plan_participation_code": "A",
                "release_information_code": "I",
                "service_lines": [
                    {
                        "professional_service": {
                            "composite_diagnosis_code_pointers": {"diagnosis_code_pointers": ["string"]},
                            "line_item_charge_amount": "321669910225",
                            "measurement_unit": "MJ",
                            "procedure_code": "procedureCode",
                            "procedure_identifier": "ER",
                            "service_unit_count": "serviceUnitCount",
                        },
                        "service_date": "73210630",
                    }
                ],
                "signature_indicator": "N",
            },
            is_testing=True,
            receiver={"organization_name": "x"},
            submitter={"contact_information": {}},
            subscriber={},
            trading_partner_service_id="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            claim = await response.parse()
            assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

        assert cast(Any, response.is_closed) is True
