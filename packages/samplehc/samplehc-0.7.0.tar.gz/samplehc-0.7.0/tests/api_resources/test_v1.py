# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types import (
    V1SqlExecuteResponse,
    V1QueryAuditLogsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestV1:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_query_audit_logs(self, client: SampleHealthcare) -> None:
        v1 = client.v1.query_audit_logs(
            query="query",
        )
        assert_matches_type(V1QueryAuditLogsResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_query_audit_logs(self, client: SampleHealthcare) -> None:
        response = client.v1.with_raw_response.query_audit_logs(
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert_matches_type(V1QueryAuditLogsResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_query_audit_logs(self, client: SampleHealthcare) -> None:
        with client.v1.with_streaming_response.query_audit_logs(
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert_matches_type(V1QueryAuditLogsResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_sql_execute(self, client: SampleHealthcare) -> None:
        v1 = client.v1.sql_execute(
            query="query",
        )
        assert_matches_type(V1SqlExecuteResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_sql_execute_with_all_params(self, client: SampleHealthcare) -> None:
        v1 = client.v1.sql_execute(
            query="query",
            array_mode=True,
            params=[{}],
        )
        assert_matches_type(V1SqlExecuteResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_sql_execute(self, client: SampleHealthcare) -> None:
        response = client.v1.with_raw_response.sql_execute(
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = response.parse()
        assert_matches_type(V1SqlExecuteResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_sql_execute(self, client: SampleHealthcare) -> None:
        with client.v1.with_streaming_response.sql_execute(
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = response.parse()
            assert_matches_type(V1SqlExecuteResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncV1:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_query_audit_logs(self, async_client: AsyncSampleHealthcare) -> None:
        v1 = await async_client.v1.query_audit_logs(
            query="query",
        )
        assert_matches_type(V1QueryAuditLogsResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_query_audit_logs(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v1.with_raw_response.query_audit_logs(
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert_matches_type(V1QueryAuditLogsResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_query_audit_logs(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v1.with_streaming_response.query_audit_logs(
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert_matches_type(V1QueryAuditLogsResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_sql_execute(self, async_client: AsyncSampleHealthcare) -> None:
        v1 = await async_client.v1.sql_execute(
            query="query",
        )
        assert_matches_type(V1SqlExecuteResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_sql_execute_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        v1 = await async_client.v1.sql_execute(
            query="query",
            array_mode=True,
            params=[{}],
        )
        assert_matches_type(V1SqlExecuteResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_sql_execute(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v1.with_raw_response.sql_execute(
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        v1 = await response.parse()
        assert_matches_type(V1SqlExecuteResponse, v1, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_sql_execute(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v1.with_streaming_response.sql_execute(
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            v1 = await response.parse()
            assert_matches_type(V1SqlExecuteResponse, v1, path=["response"])

        assert cast(Any, response.is_closed) is True
