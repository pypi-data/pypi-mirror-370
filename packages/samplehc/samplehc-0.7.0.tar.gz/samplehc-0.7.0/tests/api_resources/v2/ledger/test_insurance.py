# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.ledger import InsuranceListOutstandingAccountsResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestInsurance:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_outstanding_accounts(self, client: SampleHealthcare) -> None:
        insurance = client.v2.ledger.insurance.list_outstanding_accounts()
        assert_matches_type(InsuranceListOutstandingAccountsResponse, insurance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_outstanding_accounts(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.insurance.with_raw_response.list_outstanding_accounts()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        insurance = response.parse()
        assert_matches_type(InsuranceListOutstandingAccountsResponse, insurance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_outstanding_accounts(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.insurance.with_streaming_response.list_outstanding_accounts() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            insurance = response.parse()
            assert_matches_type(InsuranceListOutstandingAccountsResponse, insurance, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncInsurance:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_outstanding_accounts(self, async_client: AsyncSampleHealthcare) -> None:
        insurance = await async_client.v2.ledger.insurance.list_outstanding_accounts()
        assert_matches_type(InsuranceListOutstandingAccountsResponse, insurance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_outstanding_accounts(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.insurance.with_raw_response.list_outstanding_accounts()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        insurance = await response.parse()
        assert_matches_type(InsuranceListOutstandingAccountsResponse, insurance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_outstanding_accounts(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.insurance.with_streaming_response.list_outstanding_accounts() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            insurance = await response.parse()
            assert_matches_type(InsuranceListOutstandingAccountsResponse, insurance, path=["response"])

        assert cast(Any, response.is_closed) is True
