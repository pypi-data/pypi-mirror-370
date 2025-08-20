# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.integrations import CarevisoGetPayersResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCareviso:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_payers(self, client: SampleHealthcare) -> None:
        careviso = client.v2.integrations.careviso.get_payers()
        assert_matches_type(CarevisoGetPayersResponse, careviso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_payers(self, client: SampleHealthcare) -> None:
        response = client.v2.integrations.careviso.with_raw_response.get_payers()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        careviso = response.parse()
        assert_matches_type(CarevisoGetPayersResponse, careviso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_payers(self, client: SampleHealthcare) -> None:
        with client.v2.integrations.careviso.with_streaming_response.get_payers() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            careviso = response.parse()
            assert_matches_type(CarevisoGetPayersResponse, careviso, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_submit_prior_authorization(self, client: SampleHealthcare) -> None:
        careviso = client.v2.integrations.careviso.submit_prior_authorization(
            slug="slug",
            attachments=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            case_type="prior_auth_request",
            cpt_codes=["string"],
            group_id="groupId",
            icd10_codes=["string"],
            insurance_name="insuranceName",
            lab_order_id="labOrderId",
            member_id="memberId",
            patient_dob="patientDob",
            patient_first_name="patientFirstName",
            patient_id="patientId",
            patient_last_name="patientLastName",
            patient_phone="patientPhone",
            provider_fax="providerFax",
            provider_first_name="providerFirstName",
            provider_id="providerId",
            provider_last_name="providerLastName",
            provider_npi="providerNpi",
            provider_phone="providerPhone",
            service_date="serviceDate",
            test_names=["string"],
        )
        assert_matches_type(object, careviso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_submit_prior_authorization_with_all_params(self, client: SampleHealthcare) -> None:
        careviso = client.v2.integrations.careviso.submit_prior_authorization(
            slug="slug",
            attachments=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            case_type="prior_auth_request",
            cpt_codes=["string"],
            group_id="groupId",
            icd10_codes=["string"],
            insurance_name="insuranceName",
            lab_order_id="labOrderId",
            member_id="memberId",
            patient_dob="patientDob",
            patient_first_name="patientFirstName",
            patient_id="patientId",
            patient_last_name="patientLastName",
            patient_phone="patientPhone",
            provider_fax="providerFax",
            provider_first_name="providerFirstName",
            provider_id="providerId",
            provider_last_name="providerLastName",
            provider_npi="providerNpi",
            provider_phone="providerPhone",
            service_date="serviceDate",
            test_names=["string"],
            accession_date="accessionDate",
            collection_date="collectionDate",
            collection_type="collectionType",
            insurance_id="insuranceId",
            patient_city="patientCity",
            patient_gender="M",
            patient_state="patientState",
            patient_street="patientStreet",
            patient_street2="patientStreet2",
            patient_zip="patientZip",
            test_identifiers=["string"],
            test_type="testType",
        )
        assert_matches_type(object, careviso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_submit_prior_authorization(self, client: SampleHealthcare) -> None:
        response = client.v2.integrations.careviso.with_raw_response.submit_prior_authorization(
            slug="slug",
            attachments=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            case_type="prior_auth_request",
            cpt_codes=["string"],
            group_id="groupId",
            icd10_codes=["string"],
            insurance_name="insuranceName",
            lab_order_id="labOrderId",
            member_id="memberId",
            patient_dob="patientDob",
            patient_first_name="patientFirstName",
            patient_id="patientId",
            patient_last_name="patientLastName",
            patient_phone="patientPhone",
            provider_fax="providerFax",
            provider_first_name="providerFirstName",
            provider_id="providerId",
            provider_last_name="providerLastName",
            provider_npi="providerNpi",
            provider_phone="providerPhone",
            service_date="serviceDate",
            test_names=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        careviso = response.parse()
        assert_matches_type(object, careviso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_submit_prior_authorization(self, client: SampleHealthcare) -> None:
        with client.v2.integrations.careviso.with_streaming_response.submit_prior_authorization(
            slug="slug",
            attachments=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            case_type="prior_auth_request",
            cpt_codes=["string"],
            group_id="groupId",
            icd10_codes=["string"],
            insurance_name="insuranceName",
            lab_order_id="labOrderId",
            member_id="memberId",
            patient_dob="patientDob",
            patient_first_name="patientFirstName",
            patient_id="patientId",
            patient_last_name="patientLastName",
            patient_phone="patientPhone",
            provider_fax="providerFax",
            provider_first_name="providerFirstName",
            provider_id="providerId",
            provider_last_name="providerLastName",
            provider_npi="providerNpi",
            provider_phone="providerPhone",
            service_date="serviceDate",
            test_names=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            careviso = response.parse()
            assert_matches_type(object, careviso, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_submit_prior_authorization(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            client.v2.integrations.careviso.with_raw_response.submit_prior_authorization(
                slug="",
                attachments=[
                    {
                        "id": "id",
                        "file_name": "fileName",
                    }
                ],
                case_type="prior_auth_request",
                cpt_codes=["string"],
                group_id="groupId",
                icd10_codes=["string"],
                insurance_name="insuranceName",
                lab_order_id="labOrderId",
                member_id="memberId",
                patient_dob="patientDob",
                patient_first_name="patientFirstName",
                patient_id="patientId",
                patient_last_name="patientLastName",
                patient_phone="patientPhone",
                provider_fax="providerFax",
                provider_first_name="providerFirstName",
                provider_id="providerId",
                provider_last_name="providerLastName",
                provider_npi="providerNpi",
                provider_phone="providerPhone",
                service_date="serviceDate",
                test_names=["string"],
            )


class TestAsyncCareviso:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_payers(self, async_client: AsyncSampleHealthcare) -> None:
        careviso = await async_client.v2.integrations.careviso.get_payers()
        assert_matches_type(CarevisoGetPayersResponse, careviso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_payers(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.integrations.careviso.with_raw_response.get_payers()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        careviso = await response.parse()
        assert_matches_type(CarevisoGetPayersResponse, careviso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_payers(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.integrations.careviso.with_streaming_response.get_payers() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            careviso = await response.parse()
            assert_matches_type(CarevisoGetPayersResponse, careviso, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_submit_prior_authorization(self, async_client: AsyncSampleHealthcare) -> None:
        careviso = await async_client.v2.integrations.careviso.submit_prior_authorization(
            slug="slug",
            attachments=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            case_type="prior_auth_request",
            cpt_codes=["string"],
            group_id="groupId",
            icd10_codes=["string"],
            insurance_name="insuranceName",
            lab_order_id="labOrderId",
            member_id="memberId",
            patient_dob="patientDob",
            patient_first_name="patientFirstName",
            patient_id="patientId",
            patient_last_name="patientLastName",
            patient_phone="patientPhone",
            provider_fax="providerFax",
            provider_first_name="providerFirstName",
            provider_id="providerId",
            provider_last_name="providerLastName",
            provider_npi="providerNpi",
            provider_phone="providerPhone",
            service_date="serviceDate",
            test_names=["string"],
        )
        assert_matches_type(object, careviso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_submit_prior_authorization_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        careviso = await async_client.v2.integrations.careviso.submit_prior_authorization(
            slug="slug",
            attachments=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            case_type="prior_auth_request",
            cpt_codes=["string"],
            group_id="groupId",
            icd10_codes=["string"],
            insurance_name="insuranceName",
            lab_order_id="labOrderId",
            member_id="memberId",
            patient_dob="patientDob",
            patient_first_name="patientFirstName",
            patient_id="patientId",
            patient_last_name="patientLastName",
            patient_phone="patientPhone",
            provider_fax="providerFax",
            provider_first_name="providerFirstName",
            provider_id="providerId",
            provider_last_name="providerLastName",
            provider_npi="providerNpi",
            provider_phone="providerPhone",
            service_date="serviceDate",
            test_names=["string"],
            accession_date="accessionDate",
            collection_date="collectionDate",
            collection_type="collectionType",
            insurance_id="insuranceId",
            patient_city="patientCity",
            patient_gender="M",
            patient_state="patientState",
            patient_street="patientStreet",
            patient_street2="patientStreet2",
            patient_zip="patientZip",
            test_identifiers=["string"],
            test_type="testType",
        )
        assert_matches_type(object, careviso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_submit_prior_authorization(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.integrations.careviso.with_raw_response.submit_prior_authorization(
            slug="slug",
            attachments=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            case_type="prior_auth_request",
            cpt_codes=["string"],
            group_id="groupId",
            icd10_codes=["string"],
            insurance_name="insuranceName",
            lab_order_id="labOrderId",
            member_id="memberId",
            patient_dob="patientDob",
            patient_first_name="patientFirstName",
            patient_id="patientId",
            patient_last_name="patientLastName",
            patient_phone="patientPhone",
            provider_fax="providerFax",
            provider_first_name="providerFirstName",
            provider_id="providerId",
            provider_last_name="providerLastName",
            provider_npi="providerNpi",
            provider_phone="providerPhone",
            service_date="serviceDate",
            test_names=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        careviso = await response.parse()
        assert_matches_type(object, careviso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_submit_prior_authorization(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.integrations.careviso.with_streaming_response.submit_prior_authorization(
            slug="slug",
            attachments=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            case_type="prior_auth_request",
            cpt_codes=["string"],
            group_id="groupId",
            icd10_codes=["string"],
            insurance_name="insuranceName",
            lab_order_id="labOrderId",
            member_id="memberId",
            patient_dob="patientDob",
            patient_first_name="patientFirstName",
            patient_id="patientId",
            patient_last_name="patientLastName",
            patient_phone="patientPhone",
            provider_fax="providerFax",
            provider_first_name="providerFirstName",
            provider_id="providerId",
            provider_last_name="providerLastName",
            provider_npi="providerNpi",
            provider_phone="providerPhone",
            service_date="serviceDate",
            test_names=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            careviso = await response.parse()
            assert_matches_type(object, careviso, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_submit_prior_authorization(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            await async_client.v2.integrations.careviso.with_raw_response.submit_prior_authorization(
                slug="",
                attachments=[
                    {
                        "id": "id",
                        "file_name": "fileName",
                    }
                ],
                case_type="prior_auth_request",
                cpt_codes=["string"],
                group_id="groupId",
                icd10_codes=["string"],
                insurance_name="insuranceName",
                lab_order_id="labOrderId",
                member_id="memberId",
                patient_dob="patientDob",
                patient_first_name="patientFirstName",
                patient_id="patientId",
                patient_last_name="patientLastName",
                patient_phone="patientPhone",
                provider_fax="providerFax",
                provider_first_name="providerFirstName",
                provider_id="providerId",
                provider_last_name="providerLastName",
                provider_npi="providerNpi",
                provider_phone="providerPhone",
                service_date="serviceDate",
                test_names=["string"],
            )
