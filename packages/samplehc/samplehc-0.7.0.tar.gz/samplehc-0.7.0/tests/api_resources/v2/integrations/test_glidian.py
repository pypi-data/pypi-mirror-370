# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.integrations import (
    GlidianListPayersResponse,
    GlidianListServicesResponse,
    GlidianGetSubmissionRequirementsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestGlidian:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_submission_requirements(self, client: SampleHealthcare) -> None:
        glidian = client.v2.integrations.glidian.get_submission_requirements(
            slug="slug",
            insurance_id=0,
            service_id=0,
        )
        assert_matches_type(GlidianGetSubmissionRequirementsResponse, glidian, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_submission_requirements_with_all_params(self, client: SampleHealthcare) -> None:
        glidian = client.v2.integrations.glidian.get_submission_requirements(
            slug="slug",
            insurance_id=0,
            service_id=0,
            state="state",
        )
        assert_matches_type(GlidianGetSubmissionRequirementsResponse, glidian, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_submission_requirements(self, client: SampleHealthcare) -> None:
        response = client.v2.integrations.glidian.with_raw_response.get_submission_requirements(
            slug="slug",
            insurance_id=0,
            service_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        glidian = response.parse()
        assert_matches_type(GlidianGetSubmissionRequirementsResponse, glidian, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_submission_requirements(self, client: SampleHealthcare) -> None:
        with client.v2.integrations.glidian.with_streaming_response.get_submission_requirements(
            slug="slug",
            insurance_id=0,
            service_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            glidian = response.parse()
            assert_matches_type(GlidianGetSubmissionRequirementsResponse, glidian, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_submission_requirements(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            client.v2.integrations.glidian.with_raw_response.get_submission_requirements(
                slug="",
                insurance_id=0,
                service_id=0,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_payers(self, client: SampleHealthcare) -> None:
        glidian = client.v2.integrations.glidian.list_payers(
            slug="slug",
        )
        assert_matches_type(GlidianListPayersResponse, glidian, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_payers_with_all_params(self, client: SampleHealthcare) -> None:
        glidian = client.v2.integrations.glidian.list_payers(
            slug="slug",
            state="state",
        )
        assert_matches_type(GlidianListPayersResponse, glidian, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_payers(self, client: SampleHealthcare) -> None:
        response = client.v2.integrations.glidian.with_raw_response.list_payers(
            slug="slug",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        glidian = response.parse()
        assert_matches_type(GlidianListPayersResponse, glidian, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_payers(self, client: SampleHealthcare) -> None:
        with client.v2.integrations.glidian.with_streaming_response.list_payers(
            slug="slug",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            glidian = response.parse()
            assert_matches_type(GlidianListPayersResponse, glidian, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_payers(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            client.v2.integrations.glidian.with_raw_response.list_payers(
                slug="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_services(self, client: SampleHealthcare) -> None:
        glidian = client.v2.integrations.glidian.list_services(
            slug="slug",
        )
        assert_matches_type(GlidianListServicesResponse, glidian, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_services_with_all_params(self, client: SampleHealthcare) -> None:
        glidian = client.v2.integrations.glidian.list_services(
            slug="slug",
            insurance_id=0,
        )
        assert_matches_type(GlidianListServicesResponse, glidian, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_services(self, client: SampleHealthcare) -> None:
        response = client.v2.integrations.glidian.with_raw_response.list_services(
            slug="slug",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        glidian = response.parse()
        assert_matches_type(GlidianListServicesResponse, glidian, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_services(self, client: SampleHealthcare) -> None:
        with client.v2.integrations.glidian.with_streaming_response.list_services(
            slug="slug",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            glidian = response.parse()
            assert_matches_type(GlidianListServicesResponse, glidian, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_services(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            client.v2.integrations.glidian.with_raw_response.list_services(
                slug="",
            )


class TestAsyncGlidian:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_submission_requirements(self, async_client: AsyncSampleHealthcare) -> None:
        glidian = await async_client.v2.integrations.glidian.get_submission_requirements(
            slug="slug",
            insurance_id=0,
            service_id=0,
        )
        assert_matches_type(GlidianGetSubmissionRequirementsResponse, glidian, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_submission_requirements_with_all_params(
        self, async_client: AsyncSampleHealthcare
    ) -> None:
        glidian = await async_client.v2.integrations.glidian.get_submission_requirements(
            slug="slug",
            insurance_id=0,
            service_id=0,
            state="state",
        )
        assert_matches_type(GlidianGetSubmissionRequirementsResponse, glidian, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_submission_requirements(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.integrations.glidian.with_raw_response.get_submission_requirements(
            slug="slug",
            insurance_id=0,
            service_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        glidian = await response.parse()
        assert_matches_type(GlidianGetSubmissionRequirementsResponse, glidian, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_submission_requirements(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.integrations.glidian.with_streaming_response.get_submission_requirements(
            slug="slug",
            insurance_id=0,
            service_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            glidian = await response.parse()
            assert_matches_type(GlidianGetSubmissionRequirementsResponse, glidian, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_submission_requirements(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            await async_client.v2.integrations.glidian.with_raw_response.get_submission_requirements(
                slug="",
                insurance_id=0,
                service_id=0,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_payers(self, async_client: AsyncSampleHealthcare) -> None:
        glidian = await async_client.v2.integrations.glidian.list_payers(
            slug="slug",
        )
        assert_matches_type(GlidianListPayersResponse, glidian, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_payers_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        glidian = await async_client.v2.integrations.glidian.list_payers(
            slug="slug",
            state="state",
        )
        assert_matches_type(GlidianListPayersResponse, glidian, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_payers(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.integrations.glidian.with_raw_response.list_payers(
            slug="slug",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        glidian = await response.parse()
        assert_matches_type(GlidianListPayersResponse, glidian, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_payers(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.integrations.glidian.with_streaming_response.list_payers(
            slug="slug",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            glidian = await response.parse()
            assert_matches_type(GlidianListPayersResponse, glidian, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_payers(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            await async_client.v2.integrations.glidian.with_raw_response.list_payers(
                slug="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_services(self, async_client: AsyncSampleHealthcare) -> None:
        glidian = await async_client.v2.integrations.glidian.list_services(
            slug="slug",
        )
        assert_matches_type(GlidianListServicesResponse, glidian, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_services_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        glidian = await async_client.v2.integrations.glidian.list_services(
            slug="slug",
            insurance_id=0,
        )
        assert_matches_type(GlidianListServicesResponse, glidian, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_services(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.integrations.glidian.with_raw_response.list_services(
            slug="slug",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        glidian = await response.parse()
        assert_matches_type(GlidianListServicesResponse, glidian, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_services(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.integrations.glidian.with_streaming_response.list_services(
            slug="slug",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            glidian = await response.parse()
            assert_matches_type(GlidianListServicesResponse, glidian, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_services(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            await async_client.v2.integrations.glidian.with_raw_response.list_services(
                slug="",
            )
