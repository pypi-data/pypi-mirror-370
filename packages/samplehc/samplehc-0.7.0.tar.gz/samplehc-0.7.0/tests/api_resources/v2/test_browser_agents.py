# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2 import BrowserAgentInvokeResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBrowserAgents:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_invoke(self, client: SampleHealthcare) -> None:
        browser_agent = client.v2.browser_agents.invoke(
            slug="slug",
        )
        assert_matches_type(BrowserAgentInvokeResponse, browser_agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_invoke_with_all_params(self, client: SampleHealthcare) -> None:
        browser_agent = client.v2.browser_agents.invoke(
            slug="slug",
            variables={"foo": "bar"},
        )
        assert_matches_type(BrowserAgentInvokeResponse, browser_agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_invoke(self, client: SampleHealthcare) -> None:
        response = client.v2.browser_agents.with_raw_response.invoke(
            slug="slug",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser_agent = response.parse()
        assert_matches_type(BrowserAgentInvokeResponse, browser_agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_invoke(self, client: SampleHealthcare) -> None:
        with client.v2.browser_agents.with_streaming_response.invoke(
            slug="slug",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser_agent = response.parse()
            assert_matches_type(BrowserAgentInvokeResponse, browser_agent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_invoke(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            client.v2.browser_agents.with_raw_response.invoke(
                slug="",
            )


class TestAsyncBrowserAgents:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_invoke(self, async_client: AsyncSampleHealthcare) -> None:
        browser_agent = await async_client.v2.browser_agents.invoke(
            slug="slug",
        )
        assert_matches_type(BrowserAgentInvokeResponse, browser_agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_invoke_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        browser_agent = await async_client.v2.browser_agents.invoke(
            slug="slug",
            variables={"foo": "bar"},
        )
        assert_matches_type(BrowserAgentInvokeResponse, browser_agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_invoke(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.browser_agents.with_raw_response.invoke(
            slug="slug",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser_agent = await response.parse()
        assert_matches_type(BrowserAgentInvokeResponse, browser_agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_invoke(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.browser_agents.with_streaming_response.invoke(
            slug="slug",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser_agent = await response.parse()
            assert_matches_type(BrowserAgentInvokeResponse, browser_agent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_invoke(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            await async_client.v2.browser_agents.with_raw_response.invoke(
                slug="",
            )
