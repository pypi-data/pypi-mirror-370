# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .adt import (
    AdtResource,
    AsyncAdtResource,
    AdtResourceWithRawResponse,
    AsyncAdtResourceWithRawResponse,
    AdtResourceWithStreamingResponse,
    AsyncAdtResourceWithStreamingResponse,
)
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["HieResource", "AsyncHieResource"]


class HieResource(SyncAPIResource):
    @cached_property
    def adt(self) -> AdtResource:
        return AdtResource(self._client)

    @cached_property
    def with_raw_response(self) -> HieResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return HieResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> HieResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return HieResourceWithStreamingResponse(self)


class AsyncHieResource(AsyncAPIResource):
    @cached_property
    def adt(self) -> AsyncAdtResource:
        return AsyncAdtResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncHieResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncHieResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncHieResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncHieResourceWithStreamingResponse(self)


class HieResourceWithRawResponse:
    def __init__(self, hie: HieResource) -> None:
        self._hie = hie

    @cached_property
    def adt(self) -> AdtResourceWithRawResponse:
        return AdtResourceWithRawResponse(self._hie.adt)


class AsyncHieResourceWithRawResponse:
    def __init__(self, hie: AsyncHieResource) -> None:
        self._hie = hie

    @cached_property
    def adt(self) -> AsyncAdtResourceWithRawResponse:
        return AsyncAdtResourceWithRawResponse(self._hie.adt)


class HieResourceWithStreamingResponse:
    def __init__(self, hie: HieResource) -> None:
        self._hie = hie

    @cached_property
    def adt(self) -> AdtResourceWithStreamingResponse:
        return AdtResourceWithStreamingResponse(self._hie.adt)


class AsyncHieResourceWithStreamingResponse:
    def __init__(self, hie: AsyncHieResource) -> None:
        self._hie = hie

    @cached_property
    def adt(self) -> AsyncAdtResourceWithStreamingResponse:
        return AsyncAdtResourceWithStreamingResponse(self._hie.adt)
