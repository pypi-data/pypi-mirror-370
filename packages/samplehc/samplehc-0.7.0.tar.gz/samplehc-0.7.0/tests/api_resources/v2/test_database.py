# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2 import DatabaseExecuteSqlResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDatabase:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_sql(self, client: SampleHealthcare) -> None:
        database = client.v2.database.execute_sql(
            query="query",
        )
        assert_matches_type(DatabaseExecuteSqlResponse, database, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_sql_with_all_params(self, client: SampleHealthcare) -> None:
        database = client.v2.database.execute_sql(
            query="query",
            params=["string"],
        )
        assert_matches_type(DatabaseExecuteSqlResponse, database, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_execute_sql(self, client: SampleHealthcare) -> None:
        response = client.v2.database.with_raw_response.execute_sql(
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database = response.parse()
        assert_matches_type(DatabaseExecuteSqlResponse, database, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_execute_sql(self, client: SampleHealthcare) -> None:
        with client.v2.database.with_streaming_response.execute_sql(
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database = response.parse()
            assert_matches_type(DatabaseExecuteSqlResponse, database, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDatabase:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_sql(self, async_client: AsyncSampleHealthcare) -> None:
        database = await async_client.v2.database.execute_sql(
            query="query",
        )
        assert_matches_type(DatabaseExecuteSqlResponse, database, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_sql_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        database = await async_client.v2.database.execute_sql(
            query="query",
            params=["string"],
        )
        assert_matches_type(DatabaseExecuteSqlResponse, database, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_execute_sql(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.database.with_raw_response.execute_sql(
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        database = await response.parse()
        assert_matches_type(DatabaseExecuteSqlResponse, database, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_execute_sql(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.database.with_streaming_response.execute_sql(
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            database = await response.parse()
            assert_matches_type(DatabaseExecuteSqlResponse, database, path=["response"])

        assert cast(Any, response.is_closed) is True
