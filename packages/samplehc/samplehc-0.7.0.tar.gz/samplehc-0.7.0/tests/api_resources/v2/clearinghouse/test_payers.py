# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.clearinghouse import PayerListResponse, PayerRetrieveSearchResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPayers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: SampleHealthcare) -> None:
        payer = client.v2.clearinghouse.payers.list()
        assert_matches_type(PayerListResponse, payer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: SampleHealthcare) -> None:
        response = client.v2.clearinghouse.payers.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        payer = response.parse()
        assert_matches_type(PayerListResponse, payer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: SampleHealthcare) -> None:
        with client.v2.clearinghouse.payers.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            payer = response.parse()
            assert_matches_type(PayerListResponse, payer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_search(self, client: SampleHealthcare) -> None:
        payer = client.v2.clearinghouse.payers.retrieve_search(
            query="query",
        )
        assert_matches_type(PayerRetrieveSearchResponse, payer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_search(self, client: SampleHealthcare) -> None:
        response = client.v2.clearinghouse.payers.with_raw_response.retrieve_search(
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        payer = response.parse()
        assert_matches_type(PayerRetrieveSearchResponse, payer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_search(self, client: SampleHealthcare) -> None:
        with client.v2.clearinghouse.payers.with_streaming_response.retrieve_search(
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            payer = response.parse()
            assert_matches_type(PayerRetrieveSearchResponse, payer, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPayers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncSampleHealthcare) -> None:
        payer = await async_client.v2.clearinghouse.payers.list()
        assert_matches_type(PayerListResponse, payer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.clearinghouse.payers.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        payer = await response.parse()
        assert_matches_type(PayerListResponse, payer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.clearinghouse.payers.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            payer = await response.parse()
            assert_matches_type(PayerListResponse, payer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_search(self, async_client: AsyncSampleHealthcare) -> None:
        payer = await async_client.v2.clearinghouse.payers.retrieve_search(
            query="query",
        )
        assert_matches_type(PayerRetrieveSearchResponse, payer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_search(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.clearinghouse.payers.with_raw_response.retrieve_search(
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        payer = await response.parse()
        assert_matches_type(PayerRetrieveSearchResponse, payer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_search(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.clearinghouse.payers.with_streaming_response.retrieve_search(
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            payer = await response.parse()
            assert_matches_type(PayerRetrieveSearchResponse, payer, path=["response"])

        assert cast(Any, response.is_closed) is True
