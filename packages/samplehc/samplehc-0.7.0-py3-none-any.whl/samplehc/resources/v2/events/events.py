# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .hie.hie import (
    HieResource,
    AsyncHieResource,
    HieResourceWithRawResponse,
    AsyncHieResourceWithRawResponse,
    HieResourceWithStreamingResponse,
    AsyncHieResourceWithStreamingResponse,
)
from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, strip_not_given, async_maybe_transform
from ...._compat import cached_property
from ....types.v2 import event_emit_params
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v2.event_emit_response import EventEmitResponse

__all__ = ["EventsResource", "AsyncEventsResource"]


class EventsResource(SyncAPIResource):
    @cached_property
    def hie(self) -> HieResource:
        return HieResource(self._client)

    @cached_property
    def with_raw_response(self) -> EventsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return EventsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EventsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return EventsResourceWithStreamingResponse(self)

    def emit(
        self,
        *,
        name: str,
        payload: object | NotGiven = NOT_GIVEN,
        idempotency_key: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EventEmitResponse:
        """
        Create event

        Args:
          name: The name of the event to create.

          payload: The payload data for the event.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"idempotency-key": idempotency_key}), **(extra_headers or {})}
        return self._post(
            "/api/v2/events/",
            body=maybe_transform(
                {
                    "name": name,
                    "payload": payload,
                },
                event_emit_params.EventEmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EventEmitResponse,
        )


class AsyncEventsResource(AsyncAPIResource):
    @cached_property
    def hie(self) -> AsyncHieResource:
        return AsyncHieResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncEventsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncEventsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEventsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncEventsResourceWithStreamingResponse(self)

    async def emit(
        self,
        *,
        name: str,
        payload: object | NotGiven = NOT_GIVEN,
        idempotency_key: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EventEmitResponse:
        """
        Create event

        Args:
          name: The name of the event to create.

          payload: The payload data for the event.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"idempotency-key": idempotency_key}), **(extra_headers or {})}
        return await self._post(
            "/api/v2/events/",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "payload": payload,
                },
                event_emit_params.EventEmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EventEmitResponse,
        )


class EventsResourceWithRawResponse:
    def __init__(self, events: EventsResource) -> None:
        self._events = events

        self.emit = to_raw_response_wrapper(
            events.emit,
        )

    @cached_property
    def hie(self) -> HieResourceWithRawResponse:
        return HieResourceWithRawResponse(self._events.hie)


class AsyncEventsResourceWithRawResponse:
    def __init__(self, events: AsyncEventsResource) -> None:
        self._events = events

        self.emit = async_to_raw_response_wrapper(
            events.emit,
        )

    @cached_property
    def hie(self) -> AsyncHieResourceWithRawResponse:
        return AsyncHieResourceWithRawResponse(self._events.hie)


class EventsResourceWithStreamingResponse:
    def __init__(self, events: EventsResource) -> None:
        self._events = events

        self.emit = to_streamed_response_wrapper(
            events.emit,
        )

    @cached_property
    def hie(self) -> HieResourceWithStreamingResponse:
        return HieResourceWithStreamingResponse(self._events.hie)


class AsyncEventsResourceWithStreamingResponse:
    def __init__(self, events: AsyncEventsResource) -> None:
        self._events = events

        self.emit = async_to_streamed_response_wrapper(
            events.emit,
        )

    @cached_property
    def hie(self) -> AsyncHieResourceWithStreamingResponse:
        return AsyncHieResourceWithStreamingResponse(self._events.hie)
