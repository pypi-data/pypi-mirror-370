# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .messages import (
    MessagesResource,
    AsyncMessagesResource,
    MessagesResourceWithRawResponse,
    AsyncMessagesResourceWithRawResponse,
    MessagesResourceWithStreamingResponse,
    AsyncMessagesResourceWithStreamingResponse,
)
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["Kno2Resource", "AsyncKno2Resource"]


class Kno2Resource(SyncAPIResource):
    @cached_property
    def messages(self) -> MessagesResource:
        return MessagesResource(self._client)

    @cached_property
    def with_raw_response(self) -> Kno2ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return Kno2ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> Kno2ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return Kno2ResourceWithStreamingResponse(self)


class AsyncKno2Resource(AsyncAPIResource):
    @cached_property
    def messages(self) -> AsyncMessagesResource:
        return AsyncMessagesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncKno2ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncKno2ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncKno2ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncKno2ResourceWithStreamingResponse(self)


class Kno2ResourceWithRawResponse:
    def __init__(self, kno2: Kno2Resource) -> None:
        self._kno2 = kno2

    @cached_property
    def messages(self) -> MessagesResourceWithRawResponse:
        return MessagesResourceWithRawResponse(self._kno2.messages)


class AsyncKno2ResourceWithRawResponse:
    def __init__(self, kno2: AsyncKno2Resource) -> None:
        self._kno2 = kno2

    @cached_property
    def messages(self) -> AsyncMessagesResourceWithRawResponse:
        return AsyncMessagesResourceWithRawResponse(self._kno2.messages)


class Kno2ResourceWithStreamingResponse:
    def __init__(self, kno2: Kno2Resource) -> None:
        self._kno2 = kno2

    @cached_property
    def messages(self) -> MessagesResourceWithStreamingResponse:
        return MessagesResourceWithStreamingResponse(self._kno2.messages)


class AsyncKno2ResourceWithStreamingResponse:
    def __init__(self, kno2: AsyncKno2Resource) -> None:
        self._kno2 = kno2

    @cached_property
    def messages(self) -> AsyncMessagesResourceWithStreamingResponse:
        return AsyncMessagesResourceWithStreamingResponse(self._kno2.messages)
