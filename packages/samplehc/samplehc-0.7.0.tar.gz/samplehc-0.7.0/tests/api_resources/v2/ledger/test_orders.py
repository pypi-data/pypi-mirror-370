# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.ledger import (
    OrderRetrieveBalancesResponse,
    OrderRetrieveBatchBalancesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOrders:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_balances(self, client: SampleHealthcare) -> None:
        order = client.v2.ledger.orders.retrieve_balances(
            "orderId",
        )
        assert_matches_type(OrderRetrieveBalancesResponse, order, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_balances(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.orders.with_raw_response.retrieve_balances(
            "orderId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        order = response.parse()
        assert_matches_type(OrderRetrieveBalancesResponse, order, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_balances(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.orders.with_streaming_response.retrieve_balances(
            "orderId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            order = response.parse()
            assert_matches_type(OrderRetrieveBalancesResponse, order, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_balances(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `order_id` but received ''"):
            client.v2.ledger.orders.with_raw_response.retrieve_balances(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_batch_balances(self, client: SampleHealthcare) -> None:
        order = client.v2.ledger.orders.retrieve_batch_balances(
            order_ids=["string"],
        )
        assert_matches_type(OrderRetrieveBatchBalancesResponse, order, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_batch_balances(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.orders.with_raw_response.retrieve_batch_balances(
            order_ids=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        order = response.parse()
        assert_matches_type(OrderRetrieveBatchBalancesResponse, order, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_batch_balances(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.orders.with_streaming_response.retrieve_batch_balances(
            order_ids=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            order = response.parse()
            assert_matches_type(OrderRetrieveBatchBalancesResponse, order, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncOrders:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_balances(self, async_client: AsyncSampleHealthcare) -> None:
        order = await async_client.v2.ledger.orders.retrieve_balances(
            "orderId",
        )
        assert_matches_type(OrderRetrieveBalancesResponse, order, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_balances(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.orders.with_raw_response.retrieve_balances(
            "orderId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        order = await response.parse()
        assert_matches_type(OrderRetrieveBalancesResponse, order, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_balances(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.orders.with_streaming_response.retrieve_balances(
            "orderId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            order = await response.parse()
            assert_matches_type(OrderRetrieveBalancesResponse, order, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_balances(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `order_id` but received ''"):
            await async_client.v2.ledger.orders.with_raw_response.retrieve_balances(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_batch_balances(self, async_client: AsyncSampleHealthcare) -> None:
        order = await async_client.v2.ledger.orders.retrieve_batch_balances(
            order_ids=["string"],
        )
        assert_matches_type(OrderRetrieveBatchBalancesResponse, order, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_batch_balances(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.orders.with_raw_response.retrieve_batch_balances(
            order_ids=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        order = await response.parse()
        assert_matches_type(OrderRetrieveBatchBalancesResponse, order, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_batch_balances(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.orders.with_streaming_response.retrieve_batch_balances(
            order_ids=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            order = await response.parse()
            assert_matches_type(OrderRetrieveBatchBalancesResponse, order, path=["response"])

        assert cast(Any, response.is_closed) is True
