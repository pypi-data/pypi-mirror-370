# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.integrations.glidian.prior_authorizations import (
    ClinicalQuestionListResponse,
    ClinicalQuestionUpdateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClinicalQuestions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: SampleHealthcare) -> None:
        clinical_question = client.v2.integrations.glidian.prior_authorizations.clinical_questions.update(
            record_id="recordId",
            slug="slug",
            responses={"foo": {"value": "string"}},
        )
        assert_matches_type(ClinicalQuestionUpdateResponse, clinical_question, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: SampleHealthcare) -> None:
        response = client.v2.integrations.glidian.prior_authorizations.clinical_questions.with_raw_response.update(
            record_id="recordId",
            slug="slug",
            responses={"foo": {"value": "string"}},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clinical_question = response.parse()
        assert_matches_type(ClinicalQuestionUpdateResponse, clinical_question, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: SampleHealthcare) -> None:
        with client.v2.integrations.glidian.prior_authorizations.clinical_questions.with_streaming_response.update(
            record_id="recordId",
            slug="slug",
            responses={"foo": {"value": "string"}},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clinical_question = response.parse()
            assert_matches_type(ClinicalQuestionUpdateResponse, clinical_question, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            client.v2.integrations.glidian.prior_authorizations.clinical_questions.with_raw_response.update(
                record_id="recordId",
                slug="",
                responses={"foo": {"value": "string"}},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `record_id` but received ''"):
            client.v2.integrations.glidian.prior_authorizations.clinical_questions.with_raw_response.update(
                record_id="",
                slug="slug",
                responses={"foo": {"value": "string"}},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: SampleHealthcare) -> None:
        clinical_question = client.v2.integrations.glidian.prior_authorizations.clinical_questions.list(
            record_id="recordId",
            slug="slug",
        )
        assert_matches_type(ClinicalQuestionListResponse, clinical_question, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: SampleHealthcare) -> None:
        response = client.v2.integrations.glidian.prior_authorizations.clinical_questions.with_raw_response.list(
            record_id="recordId",
            slug="slug",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clinical_question = response.parse()
        assert_matches_type(ClinicalQuestionListResponse, clinical_question, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: SampleHealthcare) -> None:
        with client.v2.integrations.glidian.prior_authorizations.clinical_questions.with_streaming_response.list(
            record_id="recordId",
            slug="slug",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clinical_question = response.parse()
            assert_matches_type(ClinicalQuestionListResponse, clinical_question, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            client.v2.integrations.glidian.prior_authorizations.clinical_questions.with_raw_response.list(
                record_id="recordId",
                slug="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `record_id` but received ''"):
            client.v2.integrations.glidian.prior_authorizations.clinical_questions.with_raw_response.list(
                record_id="",
                slug="slug",
            )


class TestAsyncClinicalQuestions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncSampleHealthcare) -> None:
        clinical_question = await async_client.v2.integrations.glidian.prior_authorizations.clinical_questions.update(
            record_id="recordId",
            slug="slug",
            responses={"foo": {"value": "string"}},
        )
        assert_matches_type(ClinicalQuestionUpdateResponse, clinical_question, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncSampleHealthcare) -> None:
        response = (
            await async_client.v2.integrations.glidian.prior_authorizations.clinical_questions.with_raw_response.update(
                record_id="recordId",
                slug="slug",
                responses={"foo": {"value": "string"}},
            )
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clinical_question = await response.parse()
        assert_matches_type(ClinicalQuestionUpdateResponse, clinical_question, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncSampleHealthcare) -> None:
        async with (
            async_client.v2.integrations.glidian.prior_authorizations.clinical_questions.with_streaming_response.update(
                record_id="recordId",
                slug="slug",
                responses={"foo": {"value": "string"}},
            )
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clinical_question = await response.parse()
            assert_matches_type(ClinicalQuestionUpdateResponse, clinical_question, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            await async_client.v2.integrations.glidian.prior_authorizations.clinical_questions.with_raw_response.update(
                record_id="recordId",
                slug="",
                responses={"foo": {"value": "string"}},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `record_id` but received ''"):
            await async_client.v2.integrations.glidian.prior_authorizations.clinical_questions.with_raw_response.update(
                record_id="",
                slug="slug",
                responses={"foo": {"value": "string"}},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncSampleHealthcare) -> None:
        clinical_question = await async_client.v2.integrations.glidian.prior_authorizations.clinical_questions.list(
            record_id="recordId",
            slug="slug",
        )
        assert_matches_type(ClinicalQuestionListResponse, clinical_question, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncSampleHealthcare) -> None:
        response = (
            await async_client.v2.integrations.glidian.prior_authorizations.clinical_questions.with_raw_response.list(
                record_id="recordId",
                slug="slug",
            )
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clinical_question = await response.parse()
        assert_matches_type(ClinicalQuestionListResponse, clinical_question, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncSampleHealthcare) -> None:
        async with (
            async_client.v2.integrations.glidian.prior_authorizations.clinical_questions.with_streaming_response.list(
                record_id="recordId",
                slug="slug",
            )
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clinical_question = await response.parse()
            assert_matches_type(ClinicalQuestionListResponse, clinical_question, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            await async_client.v2.integrations.glidian.prior_authorizations.clinical_questions.with_raw_response.list(
                record_id="recordId",
                slug="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `record_id` but received ''"):
            await async_client.v2.integrations.glidian.prior_authorizations.clinical_questions.with_raw_response.list(
                record_id="",
                slug="slug",
            )
