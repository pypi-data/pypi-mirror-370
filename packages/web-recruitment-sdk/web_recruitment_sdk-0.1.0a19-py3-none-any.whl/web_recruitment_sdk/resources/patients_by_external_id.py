# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.patient_read import PatientRead

__all__ = ["PatientsByExternalIDResource", "AsyncPatientsByExternalIDResource"]


class PatientsByExternalIDResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PatientsByExternalIDResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return PatientsByExternalIDResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PatientsByExternalIDResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return PatientsByExternalIDResourceWithStreamingResponse(self)

    def retrieve(
        self,
        external_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientRead:
        """
        Get Patient By External Id

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not external_id:
            raise ValueError(f"Expected a non-empty value for `external_id` but received {external_id!r}")
        return self._get(
            f"/patients_by_external_id/{external_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientRead,
        )


class AsyncPatientsByExternalIDResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPatientsByExternalIDResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncPatientsByExternalIDResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPatientsByExternalIDResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncPatientsByExternalIDResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        external_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientRead:
        """
        Get Patient By External Id

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not external_id:
            raise ValueError(f"Expected a non-empty value for `external_id` but received {external_id!r}")
        return await self._get(
            f"/patients_by_external_id/{external_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientRead,
        )


class PatientsByExternalIDResourceWithRawResponse:
    def __init__(self, patients_by_external_id: PatientsByExternalIDResource) -> None:
        self._patients_by_external_id = patients_by_external_id

        self.retrieve = to_raw_response_wrapper(
            patients_by_external_id.retrieve,
        )


class AsyncPatientsByExternalIDResourceWithRawResponse:
    def __init__(self, patients_by_external_id: AsyncPatientsByExternalIDResource) -> None:
        self._patients_by_external_id = patients_by_external_id

        self.retrieve = async_to_raw_response_wrapper(
            patients_by_external_id.retrieve,
        )


class PatientsByExternalIDResourceWithStreamingResponse:
    def __init__(self, patients_by_external_id: PatientsByExternalIDResource) -> None:
        self._patients_by_external_id = patients_by_external_id

        self.retrieve = to_streamed_response_wrapper(
            patients_by_external_id.retrieve,
        )


class AsyncPatientsByExternalIDResourceWithStreamingResponse:
    def __init__(self, patients_by_external_id: AsyncPatientsByExternalIDResource) -> None:
        self._patients_by_external_id = patients_by_external_id

        self.retrieve = async_to_streamed_response_wrapper(
            patients_by_external_id.retrieve,
        )
