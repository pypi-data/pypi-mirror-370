# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .patients import (
    PatientsResource,
    AsyncPatientsResource,
    PatientsResourceWithRawResponse,
    AsyncPatientsResourceWithRawResponse,
    PatientsResourceWithStreamingResponse,
    AsyncPatientsResourceWithStreamingResponse,
)
from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
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
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.external.carequality_health_check_response import CarequalityHealthCheckResponse

__all__ = ["CarequalityResource", "AsyncCarequalityResource"]


class CarequalityResource(SyncAPIResource):
    @cached_property
    def patients(self) -> PatientsResource:
        return PatientsResource(self._client)

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

    def health_check(
        self,
        *,
        x_api_key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CarequalityHealthCheckResponse:
        """
        Health check endpoint for CareQuality integration.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"X-API-Key": x_api_key, **(extra_headers or {})}
        return self._get(
            "/external/carequality/health",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CarequalityHealthCheckResponse,
        )


class AsyncCarequalityResource(AsyncAPIResource):
    @cached_property
    def patients(self) -> AsyncPatientsResource:
        return AsyncPatientsResource(self._client)

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

    async def health_check(
        self,
        *,
        x_api_key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CarequalityHealthCheckResponse:
        """
        Health check endpoint for CareQuality integration.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"X-API-Key": x_api_key, **(extra_headers or {})}
        return await self._get(
            "/external/carequality/health",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CarequalityHealthCheckResponse,
        )


class CarequalityResourceWithRawResponse:
    def __init__(self, carequality: CarequalityResource) -> None:
        self._carequality = carequality

        self.health_check = to_raw_response_wrapper(
            carequality.health_check,
        )

    @cached_property
    def patients(self) -> PatientsResourceWithRawResponse:
        return PatientsResourceWithRawResponse(self._carequality.patients)

    @cached_property
    def documents(self) -> DocumentsResourceWithRawResponse:
        return DocumentsResourceWithRawResponse(self._carequality.documents)


class AsyncCarequalityResourceWithRawResponse:
    def __init__(self, carequality: AsyncCarequalityResource) -> None:
        self._carequality = carequality

        self.health_check = async_to_raw_response_wrapper(
            carequality.health_check,
        )

    @cached_property
    def patients(self) -> AsyncPatientsResourceWithRawResponse:
        return AsyncPatientsResourceWithRawResponse(self._carequality.patients)

    @cached_property
    def documents(self) -> AsyncDocumentsResourceWithRawResponse:
        return AsyncDocumentsResourceWithRawResponse(self._carequality.documents)


class CarequalityResourceWithStreamingResponse:
    def __init__(self, carequality: CarequalityResource) -> None:
        self._carequality = carequality

        self.health_check = to_streamed_response_wrapper(
            carequality.health_check,
        )

    @cached_property
    def patients(self) -> PatientsResourceWithStreamingResponse:
        return PatientsResourceWithStreamingResponse(self._carequality.patients)

    @cached_property
    def documents(self) -> DocumentsResourceWithStreamingResponse:
        return DocumentsResourceWithStreamingResponse(self._carequality.documents)


class AsyncCarequalityResourceWithStreamingResponse:
    def __init__(self, carequality: AsyncCarequalityResource) -> None:
        self._carequality = carequality

        self.health_check = async_to_streamed_response_wrapper(
            carequality.health_check,
        )

    @cached_property
    def patients(self) -> AsyncPatientsResourceWithStreamingResponse:
        return AsyncPatientsResourceWithStreamingResponse(self._carequality.patients)

    @cached_property
    def documents(self) -> AsyncDocumentsResourceWithStreamingResponse:
        return AsyncDocumentsResourceWithStreamingResponse(self._carequality.documents)
