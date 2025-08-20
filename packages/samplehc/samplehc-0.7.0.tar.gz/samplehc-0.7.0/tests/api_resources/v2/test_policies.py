# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2 import (
    PolicyListResponse,
    PolicyListPlansResponse,
    PolicyRetrieveTextResponse,
    PolicyListCompaniesResponse,
    PolicyRetrievePresignedURLResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPolicies:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: SampleHealthcare) -> None:
        policy = client.v2.policies.list()
        assert_matches_type(PolicyListResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: SampleHealthcare) -> None:
        policy = client.v2.policies.list(
            active_at="activeAt",
            company_id="companyId",
            hcpcs_codes="hcpcsCodes",
            icd10_cm_codes="icd10CmCodes",
            limit=0,
            plan_id="planId",
            policy_topic="policyTopic",
            policy_topic_for_keyword_extraction="policyTopicForKeywordExtraction",
            policy_type="policyType",
            skip=0,
            updated_at_max="updatedAtMax",
            updated_at_min="updatedAtMin",
        )
        assert_matches_type(PolicyListResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: SampleHealthcare) -> None:
        response = client.v2.policies.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        policy = response.parse()
        assert_matches_type(PolicyListResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: SampleHealthcare) -> None:
        with client.v2.policies.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            policy = response.parse()
            assert_matches_type(PolicyListResponse, policy, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_companies(self, client: SampleHealthcare) -> None:
        policy = client.v2.policies.list_companies()
        assert_matches_type(PolicyListCompaniesResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_companies_with_all_params(self, client: SampleHealthcare) -> None:
        policy = client.v2.policies.list_companies(
            company_name="company_name",
            limit=0,
            skip=0,
        )
        assert_matches_type(PolicyListCompaniesResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_companies(self, client: SampleHealthcare) -> None:
        response = client.v2.policies.with_raw_response.list_companies()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        policy = response.parse()
        assert_matches_type(PolicyListCompaniesResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_companies(self, client: SampleHealthcare) -> None:
        with client.v2.policies.with_streaming_response.list_companies() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            policy = response.parse()
            assert_matches_type(PolicyListCompaniesResponse, policy, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_plans(self, client: SampleHealthcare) -> None:
        policy = client.v2.policies.list_plans()
        assert_matches_type(PolicyListPlansResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_plans_with_all_params(self, client: SampleHealthcare) -> None:
        policy = client.v2.policies.list_plans(
            limit=0,
            plan_name="plan_name",
            skip=0,
        )
        assert_matches_type(PolicyListPlansResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_plans(self, client: SampleHealthcare) -> None:
        response = client.v2.policies.with_raw_response.list_plans()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        policy = response.parse()
        assert_matches_type(PolicyListPlansResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_plans(self, client: SampleHealthcare) -> None:
        with client.v2.policies.with_streaming_response.list_plans() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            policy = response.parse()
            assert_matches_type(PolicyListPlansResponse, policy, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_presigned_url(self, client: SampleHealthcare) -> None:
        policy = client.v2.policies.retrieve_presigned_url(
            "policyId",
        )
        assert_matches_type(PolicyRetrievePresignedURLResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_presigned_url(self, client: SampleHealthcare) -> None:
        response = client.v2.policies.with_raw_response.retrieve_presigned_url(
            "policyId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        policy = response.parse()
        assert_matches_type(PolicyRetrievePresignedURLResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_presigned_url(self, client: SampleHealthcare) -> None:
        with client.v2.policies.with_streaming_response.retrieve_presigned_url(
            "policyId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            policy = response.parse()
            assert_matches_type(PolicyRetrievePresignedURLResponse, policy, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_presigned_url(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `policy_id` but received ''"):
            client.v2.policies.with_raw_response.retrieve_presigned_url(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_text(self, client: SampleHealthcare) -> None:
        policy = client.v2.policies.retrieve_text(
            "policyId",
        )
        assert_matches_type(PolicyRetrieveTextResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_text(self, client: SampleHealthcare) -> None:
        response = client.v2.policies.with_raw_response.retrieve_text(
            "policyId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        policy = response.parse()
        assert_matches_type(PolicyRetrieveTextResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_text(self, client: SampleHealthcare) -> None:
        with client.v2.policies.with_streaming_response.retrieve_text(
            "policyId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            policy = response.parse()
            assert_matches_type(PolicyRetrieveTextResponse, policy, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_text(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `policy_id` but received ''"):
            client.v2.policies.with_raw_response.retrieve_text(
                "",
            )


class TestAsyncPolicies:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncSampleHealthcare) -> None:
        policy = await async_client.v2.policies.list()
        assert_matches_type(PolicyListResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        policy = await async_client.v2.policies.list(
            active_at="activeAt",
            company_id="companyId",
            hcpcs_codes="hcpcsCodes",
            icd10_cm_codes="icd10CmCodes",
            limit=0,
            plan_id="planId",
            policy_topic="policyTopic",
            policy_topic_for_keyword_extraction="policyTopicForKeywordExtraction",
            policy_type="policyType",
            skip=0,
            updated_at_max="updatedAtMax",
            updated_at_min="updatedAtMin",
        )
        assert_matches_type(PolicyListResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.policies.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        policy = await response.parse()
        assert_matches_type(PolicyListResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.policies.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            policy = await response.parse()
            assert_matches_type(PolicyListResponse, policy, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_companies(self, async_client: AsyncSampleHealthcare) -> None:
        policy = await async_client.v2.policies.list_companies()
        assert_matches_type(PolicyListCompaniesResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_companies_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        policy = await async_client.v2.policies.list_companies(
            company_name="company_name",
            limit=0,
            skip=0,
        )
        assert_matches_type(PolicyListCompaniesResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_companies(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.policies.with_raw_response.list_companies()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        policy = await response.parse()
        assert_matches_type(PolicyListCompaniesResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_companies(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.policies.with_streaming_response.list_companies() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            policy = await response.parse()
            assert_matches_type(PolicyListCompaniesResponse, policy, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_plans(self, async_client: AsyncSampleHealthcare) -> None:
        policy = await async_client.v2.policies.list_plans()
        assert_matches_type(PolicyListPlansResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_plans_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        policy = await async_client.v2.policies.list_plans(
            limit=0,
            plan_name="plan_name",
            skip=0,
        )
        assert_matches_type(PolicyListPlansResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_plans(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.policies.with_raw_response.list_plans()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        policy = await response.parse()
        assert_matches_type(PolicyListPlansResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_plans(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.policies.with_streaming_response.list_plans() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            policy = await response.parse()
            assert_matches_type(PolicyListPlansResponse, policy, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_presigned_url(self, async_client: AsyncSampleHealthcare) -> None:
        policy = await async_client.v2.policies.retrieve_presigned_url(
            "policyId",
        )
        assert_matches_type(PolicyRetrievePresignedURLResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_presigned_url(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.policies.with_raw_response.retrieve_presigned_url(
            "policyId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        policy = await response.parse()
        assert_matches_type(PolicyRetrievePresignedURLResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_presigned_url(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.policies.with_streaming_response.retrieve_presigned_url(
            "policyId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            policy = await response.parse()
            assert_matches_type(PolicyRetrievePresignedURLResponse, policy, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_presigned_url(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `policy_id` but received ''"):
            await async_client.v2.policies.with_raw_response.retrieve_presigned_url(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_text(self, async_client: AsyncSampleHealthcare) -> None:
        policy = await async_client.v2.policies.retrieve_text(
            "policyId",
        )
        assert_matches_type(PolicyRetrieveTextResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_text(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.policies.with_raw_response.retrieve_text(
            "policyId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        policy = await response.parse()
        assert_matches_type(PolicyRetrieveTextResponse, policy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_text(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.policies.with_streaming_response.retrieve_text(
            "policyId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            policy = await response.parse()
            assert_matches_type(PolicyRetrieveTextResponse, policy, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_text(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `policy_id` but received ''"):
            await async_client.v2.policies.with_raw_response.retrieve_text(
                "",
            )
