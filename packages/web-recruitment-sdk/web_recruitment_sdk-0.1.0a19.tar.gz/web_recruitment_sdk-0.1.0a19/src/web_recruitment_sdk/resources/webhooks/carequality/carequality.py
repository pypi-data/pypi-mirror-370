# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .documents import (
    DocumentsResource,
    AsyncDocumentsResource,
    DocumentsResourceWithRawResponse,
    AsyncDocumentsResourceWithRawResponse,
    DocumentsResourceWithStreamingResponse,
    AsyncDocumentsResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["CarequalityResource", "AsyncCarequalityResource"]


class CarequalityResource(SyncAPIResource):
    @cached_property
    def documents(self) -> DocumentsResource:
        return DocumentsResource(self._client)

    @cached_property
    def with_raw_response(self) -> CarequalityResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return CarequalityResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CarequalityResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return CarequalityResourceWithStreamingResponse(self)


class AsyncCarequalityResource(AsyncAPIResource):
    @cached_property
    def documents(self) -> AsyncDocumentsResource:
        return AsyncDocumentsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncCarequalityResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncCarequalityResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCarequalityResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncCarequalityResourceWithStreamingResponse(self)


class CarequalityResourceWithRawResponse:
    def __init__(self, carequality: CarequalityResource) -> None:
        self._carequality = carequality

    @cached_property
    def documents(self) -> DocumentsResourceWithRawResponse:
        return DocumentsResourceWithRawResponse(self._carequality.documents)


class AsyncCarequalityResourceWithRawResponse:
    def __init__(self, carequality: AsyncCarequalityResource) -> None:
        self._carequality = carequality

    @cached_property
    def documents(self) -> AsyncDocumentsResourceWithRawResponse:
        return AsyncDocumentsResourceWithRawResponse(self._carequality.documents)


class CarequalityResourceWithStreamingResponse:
    def __init__(self, carequality: CarequalityResource) -> None:
        self._carequality = carequality

    @cached_property
    def documents(self) -> DocumentsResourceWithStreamingResponse:
        return DocumentsResourceWithStreamingResponse(self._carequality.documents)


class AsyncCarequalityResourceWithStreamingResponse:
    def __init__(self, carequality: AsyncCarequalityResource) -> None:
        self._carequality = carequality

    @cached_property
    def documents(self) -> AsyncDocumentsResourceWithStreamingResponse:
        return AsyncDocumentsResourceWithStreamingResponse(self._carequality.documents)
