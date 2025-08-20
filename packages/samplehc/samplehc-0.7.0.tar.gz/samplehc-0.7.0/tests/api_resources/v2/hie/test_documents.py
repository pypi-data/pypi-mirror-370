# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.hie import DocumentQueryResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDocuments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_query(self, client: SampleHealthcare) -> None:
        document = client.v2.hie.documents.query(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
        )
        assert_matches_type(DocumentQueryResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_query_with_all_params(self, client: SampleHealthcare) -> None:
        document = client.v2.hie.documents.query(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                    "address_line2": "addressLine2",
                    "country": "country",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
            contact=[
                {
                    "email": "email",
                    "phone": "phone",
                }
            ],
            personal_identifiers=[
                {
                    "type": "driversLicense",
                    "value": "value",
                    "state": "state",
                }
            ],
        )
        assert_matches_type(DocumentQueryResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_query(self, client: SampleHealthcare) -> None:
        response = client.v2.hie.documents.with_raw_response.query(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentQueryResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_query(self, client: SampleHealthcare) -> None:
        with client.v2.hie.documents.with_streaming_response.query(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentQueryResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload(self, client: SampleHealthcare) -> None:
        document = client.v2.hie.documents.upload(
            description="description",
            document_type={"text": "text"},
            file_metadata_id="fileMetadataId",
            patient_id="patientId",
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload_with_all_params(self, client: SampleHealthcare) -> None:
        document = client.v2.hie.documents.upload(
            description="description",
            document_type={
                "text": "text",
                "coding": [
                    {
                        "code": "code",
                        "display": "display",
                        "system": "system",
                    }
                ],
            },
            file_metadata_id="fileMetadataId",
            patient_id="patientId",
            date_end="dateEnd",
            date_start="dateStart",
            facility_name="facilityName",
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_upload(self, client: SampleHealthcare) -> None:
        response = client.v2.hie.documents.with_raw_response.upload(
            description="description",
            document_type={"text": "text"},
            file_metadata_id="fileMetadataId",
            patient_id="patientId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_upload(self, client: SampleHealthcare) -> None:
        with client.v2.hie.documents.with_streaming_response.upload(
            description="description",
            document_type={"text": "text"},
            file_metadata_id="fileMetadataId",
            patient_id="patientId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(object, document, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDocuments:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_query(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.hie.documents.query(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
        )
        assert_matches_type(DocumentQueryResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_query_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.hie.documents.query(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                    "address_line2": "addressLine2",
                    "country": "country",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
            contact=[
                {
                    "email": "email",
                    "phone": "phone",
                }
            ],
            personal_identifiers=[
                {
                    "type": "driversLicense",
                    "value": "value",
                    "state": "state",
                }
            ],
        )
        assert_matches_type(DocumentQueryResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_query(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.hie.documents.with_raw_response.query(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentQueryResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_query(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.hie.documents.with_streaming_response.query(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentQueryResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.hie.documents.upload(
            description="description",
            document_type={"text": "text"},
            file_metadata_id="fileMetadataId",
            patient_id="patientId",
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.hie.documents.upload(
            description="description",
            document_type={
                "text": "text",
                "coding": [
                    {
                        "code": "code",
                        "display": "display",
                        "system": "system",
                    }
                ],
            },
            file_metadata_id="fileMetadataId",
            patient_id="patientId",
            date_end="dateEnd",
            date_start="dateStart",
            facility_name="facilityName",
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_upload(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.hie.documents.with_raw_response.upload(
            description="description",
            document_type={"text": "text"},
            file_metadata_id="fileMetadataId",
            patient_id="patientId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_upload(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.hie.documents.with_streaming_response.upload(
            description="description",
            document_type={"text": "text"},
            file_metadata_id="fileMetadataId",
            patient_id="patientId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(object, document, path=["response"])

        assert cast(Any, response.is_closed) is True
