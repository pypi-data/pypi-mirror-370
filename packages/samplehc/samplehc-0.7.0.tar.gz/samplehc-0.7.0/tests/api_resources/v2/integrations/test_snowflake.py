# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.integrations import SnowflakeQueryResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSnowflake:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_query(self, client: SampleHealthcare) -> None:
        snowflake = client.v2.integrations.snowflake.query(
            slug="slug",
            query="query",
        )
        assert_matches_type(SnowflakeQueryResponse, snowflake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_query(self, client: SampleHealthcare) -> None:
        response = client.v2.integrations.snowflake.with_raw_response.query(
            slug="slug",
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        snowflake = response.parse()
        assert_matches_type(SnowflakeQueryResponse, snowflake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_query(self, client: SampleHealthcare) -> None:
        with client.v2.integrations.snowflake.with_streaming_response.query(
            slug="slug",
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            snowflake = response.parse()
            assert_matches_type(SnowflakeQueryResponse, snowflake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_query(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            client.v2.integrations.snowflake.with_raw_response.query(
                slug="",
                query="query",
            )


class TestAsyncSnowflake:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_query(self, async_client: AsyncSampleHealthcare) -> None:
        snowflake = await async_client.v2.integrations.snowflake.query(
            slug="slug",
            query="query",
        )
        assert_matches_type(SnowflakeQueryResponse, snowflake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_query(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.integrations.snowflake.with_raw_response.query(
            slug="slug",
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        snowflake = await response.parse()
        assert_matches_type(SnowflakeQueryResponse, snowflake, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_query(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.integrations.snowflake.with_streaming_response.query(
            slug="slug",
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            snowflake = await response.parse()
            assert_matches_type(SnowflakeQueryResponse, snowflake, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_query(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            await async_client.v2.integrations.snowflake.with_raw_response.query(
                slug="",
                query="query",
            )
