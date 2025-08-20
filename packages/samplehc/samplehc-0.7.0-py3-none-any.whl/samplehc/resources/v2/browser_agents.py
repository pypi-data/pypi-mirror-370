# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ...types.v2 import browser_agent_invoke_params
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.v2.browser_agent_invoke_response import BrowserAgentInvokeResponse

__all__ = ["BrowserAgentsResource", "AsyncBrowserAgentsResource"]


class BrowserAgentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BrowserAgentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return BrowserAgentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BrowserAgentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return BrowserAgentsResourceWithStreamingResponse(self)

    def invoke(
        self,
        slug: str,
        *,
        variables: Dict[str, object] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserAgentInvokeResponse:
        """
        Start execution of a browser agent with optional variables.

        Args:
          variables: Variables to pass to the browser agent

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return self._post(
            f"/api/v2/browser-agents/{slug}/invoke",
            body=maybe_transform({"variables": variables}, browser_agent_invoke_params.BrowserAgentInvokeParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserAgentInvokeResponse,
        )


class AsyncBrowserAgentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBrowserAgentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncBrowserAgentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBrowserAgentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncBrowserAgentsResourceWithStreamingResponse(self)

    async def invoke(
        self,
        slug: str,
        *,
        variables: Dict[str, object] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserAgentInvokeResponse:
        """
        Start execution of a browser agent with optional variables.

        Args:
          variables: Variables to pass to the browser agent

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return await self._post(
            f"/api/v2/browser-agents/{slug}/invoke",
            body=await async_maybe_transform(
                {"variables": variables}, browser_agent_invoke_params.BrowserAgentInvokeParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserAgentInvokeResponse,
        )


class BrowserAgentsResourceWithRawResponse:
    def __init__(self, browser_agents: BrowserAgentsResource) -> None:
        self._browser_agents = browser_agents

        self.invoke = to_raw_response_wrapper(
            browser_agents.invoke,
        )


class AsyncBrowserAgentsResourceWithRawResponse:
    def __init__(self, browser_agents: AsyncBrowserAgentsResource) -> None:
        self._browser_agents = browser_agents

        self.invoke = async_to_raw_response_wrapper(
            browser_agents.invoke,
        )


class BrowserAgentsResourceWithStreamingResponse:
    def __init__(self, browser_agents: BrowserAgentsResource) -> None:
        self._browser_agents = browser_agents

        self.invoke = to_streamed_response_wrapper(
            browser_agents.invoke,
        )


class AsyncBrowserAgentsResourceWithStreamingResponse:
    def __init__(self, browser_agents: AsyncBrowserAgentsResource) -> None:
        self._browser_agents = browser_agents

        self.invoke = async_to_streamed_response_wrapper(
            browser_agents.invoke,
        )
