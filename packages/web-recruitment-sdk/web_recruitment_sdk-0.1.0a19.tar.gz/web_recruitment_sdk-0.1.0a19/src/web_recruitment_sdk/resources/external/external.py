# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from .carequality.carequality import (
    CarequalityResource,
    AsyncCarequalityResource,
    CarequalityResourceWithRawResponse,
    AsyncCarequalityResourceWithRawResponse,
    CarequalityResourceWithStreamingResponse,
    AsyncCarequalityResourceWithStreamingResponse,
)

__all__ = ["ExternalResource", "AsyncExternalResource"]


class ExternalResource(SyncAPIResource):
    @cached_property
    def carequality(self) -> CarequalityResource:
        return CarequalityResource(self._client)

    @cached_property
    def with_raw_response(self) -> ExternalResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return ExternalResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ExternalResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return ExternalResourceWithStreamingResponse(self)


class AsyncExternalResource(AsyncAPIResource):
    @cached_property
    def carequality(self) -> AsyncCarequalityResource:
        return AsyncCarequalityResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncExternalResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncExternalResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncExternalResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncExternalResourceWithStreamingResponse(self)


class ExternalResourceWithRawResponse:
    def __init__(self, external: ExternalResource) -> None:
        self._external = external

    @cached_property
    def carequality(self) -> CarequalityResourceWithRawResponse:
        return CarequalityResourceWithRawResponse(self._external.carequality)


class AsyncExternalResourceWithRawResponse:
    def __init__(self, external: AsyncExternalResource) -> None:
        self._external = external

    @cached_property
    def carequality(self) -> AsyncCarequalityResourceWithRawResponse:
        return AsyncCarequalityResourceWithRawResponse(self._external.carequality)


class ExternalResourceWithStreamingResponse:
    def __init__(self, external: ExternalResource) -> None:
        self._external = external

    @cached_property
    def carequality(self) -> CarequalityResourceWithStreamingResponse:
        return CarequalityResourceWithStreamingResponse(self._external.carequality)


class AsyncExternalResourceWithStreamingResponse:
    def __init__(self, external: AsyncExternalResource) -> None:
        self._external = external

    @cached_property
    def carequality(self) -> AsyncCarequalityResourceWithStreamingResponse:
        return AsyncCarequalityResourceWithStreamingResponse(self._external.carequality)
