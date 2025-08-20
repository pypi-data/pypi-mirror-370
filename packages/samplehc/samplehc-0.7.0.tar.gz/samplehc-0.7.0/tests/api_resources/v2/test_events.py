# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2 import EventEmitResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEvents:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_emit(self, client: SampleHealthcare) -> None:
        event = client.v2.events.emit(
            name="name",
        )
        assert_matches_type(EventEmitResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_emit_with_all_params(self, client: SampleHealthcare) -> None:
        event = client.v2.events.emit(
            name="name",
            payload={},
            idempotency_key="idempotency-key",
        )
        assert_matches_type(EventEmitResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_emit(self, client: SampleHealthcare) -> None:
        response = client.v2.events.with_raw_response.emit(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = response.parse()
        assert_matches_type(EventEmitResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_emit(self, client: SampleHealthcare) -> None:
        with client.v2.events.with_streaming_response.emit(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = response.parse()
            assert_matches_type(EventEmitResponse, event, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncEvents:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_emit(self, async_client: AsyncSampleHealthcare) -> None:
        event = await async_client.v2.events.emit(
            name="name",
        )
        assert_matches_type(EventEmitResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_emit_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        event = await async_client.v2.events.emit(
            name="name",
            payload={},
            idempotency_key="idempotency-key",
        )
        assert_matches_type(EventEmitResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_emit(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.events.with_raw_response.emit(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = await response.parse()
        assert_matches_type(EventEmitResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_emit(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.events.with_streaming_response.emit(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = await response.parse()
            assert_matches_type(EventEmitResponse, event, path=["response"])

        assert cast(Any, response.is_closed) is True
