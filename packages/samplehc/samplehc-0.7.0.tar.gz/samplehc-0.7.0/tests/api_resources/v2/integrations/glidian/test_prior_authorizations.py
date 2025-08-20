# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.integrations.glidian import (
    PriorAuthorizationSubmitResponse,
    PriorAuthorizationCreateDraftResponse,
    PriorAuthorizationUpdateRecordResponse,
    PriorAuthorizationRetrieveRecordResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPriorAuthorizations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_draft(self, client: SampleHealthcare) -> None:
        prior_authorization = client.v2.integrations.glidian.prior_authorizations.create_draft(
            slug="slug",
            attachments=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            glidian_payer_id=0,
            glidian_service_id="glidianServiceId",
            reference_number="referenceNumber",
            submission_requirements={"foo": "string"},
        )
        assert_matches_type(PriorAuthorizationCreateDraftResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_draft_with_all_params(self, client: SampleHealthcare) -> None:
        prior_authorization = client.v2.integrations.glidian.prior_authorizations.create_draft(
            slug="slug",
            attachments=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            glidian_payer_id=0,
            glidian_service_id="glidianServiceId",
            reference_number="referenceNumber",
            submission_requirements={"foo": "string"},
            reference_number_two="referenceNumberTwo",
            state="state",
        )
        assert_matches_type(PriorAuthorizationCreateDraftResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_draft(self, client: SampleHealthcare) -> None:
        response = client.v2.integrations.glidian.prior_authorizations.with_raw_response.create_draft(
            slug="slug",
            attachments=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            glidian_payer_id=0,
            glidian_service_id="glidianServiceId",
            reference_number="referenceNumber",
            submission_requirements={"foo": "string"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prior_authorization = response.parse()
        assert_matches_type(PriorAuthorizationCreateDraftResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_draft(self, client: SampleHealthcare) -> None:
        with client.v2.integrations.glidian.prior_authorizations.with_streaming_response.create_draft(
            slug="slug",
            attachments=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            glidian_payer_id=0,
            glidian_service_id="glidianServiceId",
            reference_number="referenceNumber",
            submission_requirements={"foo": "string"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prior_authorization = response.parse()
            assert_matches_type(PriorAuthorizationCreateDraftResponse, prior_authorization, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_draft(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            client.v2.integrations.glidian.prior_authorizations.with_raw_response.create_draft(
                slug="",
                attachments=[
                    {
                        "id": "id",
                        "file_name": "fileName",
                    }
                ],
                glidian_payer_id=0,
                glidian_service_id="glidianServiceId",
                reference_number="referenceNumber",
                submission_requirements={"foo": "string"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_record(self, client: SampleHealthcare) -> None:
        prior_authorization = client.v2.integrations.glidian.prior_authorizations.retrieve_record(
            record_id="recordId",
            slug="slug",
        )
        assert_matches_type(PriorAuthorizationRetrieveRecordResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_record(self, client: SampleHealthcare) -> None:
        response = client.v2.integrations.glidian.prior_authorizations.with_raw_response.retrieve_record(
            record_id="recordId",
            slug="slug",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prior_authorization = response.parse()
        assert_matches_type(PriorAuthorizationRetrieveRecordResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_record(self, client: SampleHealthcare) -> None:
        with client.v2.integrations.glidian.prior_authorizations.with_streaming_response.retrieve_record(
            record_id="recordId",
            slug="slug",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prior_authorization = response.parse()
            assert_matches_type(PriorAuthorizationRetrieveRecordResponse, prior_authorization, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_record(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            client.v2.integrations.glidian.prior_authorizations.with_raw_response.retrieve_record(
                record_id="recordId",
                slug="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `record_id` but received ''"):
            client.v2.integrations.glidian.prior_authorizations.with_raw_response.retrieve_record(
                record_id="",
                slug="slug",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_submit(self, client: SampleHealthcare) -> None:
        prior_authorization = client.v2.integrations.glidian.prior_authorizations.submit(
            record_id="recordId",
            slug="slug",
        )
        assert_matches_type(PriorAuthorizationSubmitResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_submit(self, client: SampleHealthcare) -> None:
        response = client.v2.integrations.glidian.prior_authorizations.with_raw_response.submit(
            record_id="recordId",
            slug="slug",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prior_authorization = response.parse()
        assert_matches_type(PriorAuthorizationSubmitResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_submit(self, client: SampleHealthcare) -> None:
        with client.v2.integrations.glidian.prior_authorizations.with_streaming_response.submit(
            record_id="recordId",
            slug="slug",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prior_authorization = response.parse()
            assert_matches_type(PriorAuthorizationSubmitResponse, prior_authorization, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_submit(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            client.v2.integrations.glidian.prior_authorizations.with_raw_response.submit(
                record_id="recordId",
                slug="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `record_id` but received ''"):
            client.v2.integrations.glidian.prior_authorizations.with_raw_response.submit(
                record_id="",
                slug="slug",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_record(self, client: SampleHealthcare) -> None:
        prior_authorization = client.v2.integrations.glidian.prior_authorizations.update_record(
            record_id="recordId",
            slug="slug",
        )
        assert_matches_type(PriorAuthorizationUpdateRecordResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_record_with_all_params(self, client: SampleHealthcare) -> None:
        prior_authorization = client.v2.integrations.glidian.prior_authorizations.update_record(
            record_id="recordId",
            slug="slug",
            reference_number="referenceNumber",
            reference_number_two="referenceNumberTwo",
            submission_requirements={"foo": "string"},
        )
        assert_matches_type(PriorAuthorizationUpdateRecordResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_record(self, client: SampleHealthcare) -> None:
        response = client.v2.integrations.glidian.prior_authorizations.with_raw_response.update_record(
            record_id="recordId",
            slug="slug",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prior_authorization = response.parse()
        assert_matches_type(PriorAuthorizationUpdateRecordResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_record(self, client: SampleHealthcare) -> None:
        with client.v2.integrations.glidian.prior_authorizations.with_streaming_response.update_record(
            record_id="recordId",
            slug="slug",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prior_authorization = response.parse()
            assert_matches_type(PriorAuthorizationUpdateRecordResponse, prior_authorization, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_record(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            client.v2.integrations.glidian.prior_authorizations.with_raw_response.update_record(
                record_id="recordId",
                slug="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `record_id` but received ''"):
            client.v2.integrations.glidian.prior_authorizations.with_raw_response.update_record(
                record_id="",
                slug="slug",
            )


class TestAsyncPriorAuthorizations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_draft(self, async_client: AsyncSampleHealthcare) -> None:
        prior_authorization = await async_client.v2.integrations.glidian.prior_authorizations.create_draft(
            slug="slug",
            attachments=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            glidian_payer_id=0,
            glidian_service_id="glidianServiceId",
            reference_number="referenceNumber",
            submission_requirements={"foo": "string"},
        )
        assert_matches_type(PriorAuthorizationCreateDraftResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_draft_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        prior_authorization = await async_client.v2.integrations.glidian.prior_authorizations.create_draft(
            slug="slug",
            attachments=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            glidian_payer_id=0,
            glidian_service_id="glidianServiceId",
            reference_number="referenceNumber",
            submission_requirements={"foo": "string"},
            reference_number_two="referenceNumberTwo",
            state="state",
        )
        assert_matches_type(PriorAuthorizationCreateDraftResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_draft(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.integrations.glidian.prior_authorizations.with_raw_response.create_draft(
            slug="slug",
            attachments=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            glidian_payer_id=0,
            glidian_service_id="glidianServiceId",
            reference_number="referenceNumber",
            submission_requirements={"foo": "string"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prior_authorization = await response.parse()
        assert_matches_type(PriorAuthorizationCreateDraftResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_draft(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.integrations.glidian.prior_authorizations.with_streaming_response.create_draft(
            slug="slug",
            attachments=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            glidian_payer_id=0,
            glidian_service_id="glidianServiceId",
            reference_number="referenceNumber",
            submission_requirements={"foo": "string"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prior_authorization = await response.parse()
            assert_matches_type(PriorAuthorizationCreateDraftResponse, prior_authorization, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_draft(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            await async_client.v2.integrations.glidian.prior_authorizations.with_raw_response.create_draft(
                slug="",
                attachments=[
                    {
                        "id": "id",
                        "file_name": "fileName",
                    }
                ],
                glidian_payer_id=0,
                glidian_service_id="glidianServiceId",
                reference_number="referenceNumber",
                submission_requirements={"foo": "string"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_record(self, async_client: AsyncSampleHealthcare) -> None:
        prior_authorization = await async_client.v2.integrations.glidian.prior_authorizations.retrieve_record(
            record_id="recordId",
            slug="slug",
        )
        assert_matches_type(PriorAuthorizationRetrieveRecordResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_record(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.integrations.glidian.prior_authorizations.with_raw_response.retrieve_record(
            record_id="recordId",
            slug="slug",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prior_authorization = await response.parse()
        assert_matches_type(PriorAuthorizationRetrieveRecordResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_record(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.integrations.glidian.prior_authorizations.with_streaming_response.retrieve_record(
            record_id="recordId",
            slug="slug",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prior_authorization = await response.parse()
            assert_matches_type(PriorAuthorizationRetrieveRecordResponse, prior_authorization, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_record(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            await async_client.v2.integrations.glidian.prior_authorizations.with_raw_response.retrieve_record(
                record_id="recordId",
                slug="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `record_id` but received ''"):
            await async_client.v2.integrations.glidian.prior_authorizations.with_raw_response.retrieve_record(
                record_id="",
                slug="slug",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_submit(self, async_client: AsyncSampleHealthcare) -> None:
        prior_authorization = await async_client.v2.integrations.glidian.prior_authorizations.submit(
            record_id="recordId",
            slug="slug",
        )
        assert_matches_type(PriorAuthorizationSubmitResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_submit(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.integrations.glidian.prior_authorizations.with_raw_response.submit(
            record_id="recordId",
            slug="slug",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prior_authorization = await response.parse()
        assert_matches_type(PriorAuthorizationSubmitResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_submit(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.integrations.glidian.prior_authorizations.with_streaming_response.submit(
            record_id="recordId",
            slug="slug",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prior_authorization = await response.parse()
            assert_matches_type(PriorAuthorizationSubmitResponse, prior_authorization, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_submit(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            await async_client.v2.integrations.glidian.prior_authorizations.with_raw_response.submit(
                record_id="recordId",
                slug="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `record_id` but received ''"):
            await async_client.v2.integrations.glidian.prior_authorizations.with_raw_response.submit(
                record_id="",
                slug="slug",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_record(self, async_client: AsyncSampleHealthcare) -> None:
        prior_authorization = await async_client.v2.integrations.glidian.prior_authorizations.update_record(
            record_id="recordId",
            slug="slug",
        )
        assert_matches_type(PriorAuthorizationUpdateRecordResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_record_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        prior_authorization = await async_client.v2.integrations.glidian.prior_authorizations.update_record(
            record_id="recordId",
            slug="slug",
            reference_number="referenceNumber",
            reference_number_two="referenceNumberTwo",
            submission_requirements={"foo": "string"},
        )
        assert_matches_type(PriorAuthorizationUpdateRecordResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_record(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.integrations.glidian.prior_authorizations.with_raw_response.update_record(
            record_id="recordId",
            slug="slug",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prior_authorization = await response.parse()
        assert_matches_type(PriorAuthorizationUpdateRecordResponse, prior_authorization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_record(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.integrations.glidian.prior_authorizations.with_streaming_response.update_record(
            record_id="recordId",
            slug="slug",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prior_authorization = await response.parse()
            assert_matches_type(PriorAuthorizationUpdateRecordResponse, prior_authorization, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_record(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            await async_client.v2.integrations.glidian.prior_authorizations.with_raw_response.update_record(
                record_id="recordId",
                slug="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `record_id` but received ''"):
            await async_client.v2.integrations.glidian.prior_authorizations.with_raw_response.update_record(
                record_id="",
                slug="slug",
            )
