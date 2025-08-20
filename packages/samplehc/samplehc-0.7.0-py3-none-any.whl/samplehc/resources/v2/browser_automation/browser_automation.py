# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .availity import (
    AvailityResource,
    AsyncAvailityResource,
    AvailityResourceWithRawResponse,
    AsyncAvailityResourceWithRawResponse,
    AvailityResourceWithStreamingResponse,
    AsyncAvailityResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["BrowserAutomationResource", "AsyncBrowserAutomationResource"]


class BrowserAutomationResource(SyncAPIResource):
    @cached_property
    def availity(self) -> AvailityResource:
        return AvailityResource(self._client)

    @cached_property
    def with_raw_response(self) -> BrowserAutomationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return BrowserAutomationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BrowserAutomationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return BrowserAutomationResourceWithStreamingResponse(self)


class AsyncBrowserAutomationResource(AsyncAPIResource):
    @cached_property
    def availity(self) -> AsyncAvailityResource:
        return AsyncAvailityResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncBrowserAutomationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncBrowserAutomationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBrowserAutomationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncBrowserAutomationResourceWithStreamingResponse(self)


class BrowserAutomationResourceWithRawResponse:
    def __init__(self, browser_automation: BrowserAutomationResource) -> None:
        self._browser_automation = browser_automation

    @cached_property
    def availity(self) -> AvailityResourceWithRawResponse:
        return AvailityResourceWithRawResponse(self._browser_automation.availity)


class AsyncBrowserAutomationResourceWithRawResponse:
    def __init__(self, browser_automation: AsyncBrowserAutomationResource) -> None:
        self._browser_automation = browser_automation

    @cached_property
    def availity(self) -> AsyncAvailityResourceWithRawResponse:
        return AsyncAvailityResourceWithRawResponse(self._browser_automation.availity)


class BrowserAutomationResourceWithStreamingResponse:
    def __init__(self, browser_automation: BrowserAutomationResource) -> None:
        self._browser_automation = browser_automation

    @cached_property
    def availity(self) -> AvailityResourceWithStreamingResponse:
        return AvailityResourceWithStreamingResponse(self._browser_automation.availity)


class AsyncBrowserAutomationResourceWithStreamingResponse:
    def __init__(self, browser_automation: AsyncBrowserAutomationResource) -> None:
        self._browser_automation = browser_automation

    @cached_property
    def availity(self) -> AsyncAvailityResourceWithStreamingResponse:
        return AsyncAvailityResourceWithStreamingResponse(self._browser_automation.availity)
