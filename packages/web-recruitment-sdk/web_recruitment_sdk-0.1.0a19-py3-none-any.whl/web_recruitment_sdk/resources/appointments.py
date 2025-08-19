# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import appointment_list_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.appointment import Appointment
from ..types.appointment_list_response import AppointmentListResponse

__all__ = ["AppointmentsResource", "AsyncAppointmentsResource"]


class AppointmentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AppointmentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AppointmentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AppointmentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AppointmentsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        trially_appointment_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Appointment:
        """
        Get Appointment

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not trially_appointment_id:
            raise ValueError(
                f"Expected a non-empty value for `trially_appointment_id` but received {trially_appointment_id!r}"
            )
        return self._get(
            f"/appointments/{trially_appointment_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Appointment,
        )

    def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AppointmentListResponse:
        """
        Get Appointments

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/appointments",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"limit": limit}, appointment_list_params.AppointmentListParams),
            ),
            cast_to=AppointmentListResponse,
        )


class AsyncAppointmentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAppointmentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncAppointmentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAppointmentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncAppointmentsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        trially_appointment_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Appointment:
        """
        Get Appointment

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not trially_appointment_id:
            raise ValueError(
                f"Expected a non-empty value for `trially_appointment_id` but received {trially_appointment_id!r}"
            )
        return await self._get(
            f"/appointments/{trially_appointment_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Appointment,
        )

    async def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AppointmentListResponse:
        """
        Get Appointments

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/appointments",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"limit": limit}, appointment_list_params.AppointmentListParams),
            ),
            cast_to=AppointmentListResponse,
        )


class AppointmentsResourceWithRawResponse:
    def __init__(self, appointments: AppointmentsResource) -> None:
        self._appointments = appointments

        self.retrieve = to_raw_response_wrapper(
            appointments.retrieve,
        )
        self.list = to_raw_response_wrapper(
            appointments.list,
        )


class AsyncAppointmentsResourceWithRawResponse:
    def __init__(self, appointments: AsyncAppointmentsResource) -> None:
        self._appointments = appointments

        self.retrieve = async_to_raw_response_wrapper(
            appointments.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            appointments.list,
        )


class AppointmentsResourceWithStreamingResponse:
    def __init__(self, appointments: AppointmentsResource) -> None:
        self._appointments = appointments

        self.retrieve = to_streamed_response_wrapper(
            appointments.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            appointments.list,
        )


class AsyncAppointmentsResourceWithStreamingResponse:
    def __init__(self, appointments: AsyncAppointmentsResource) -> None:
        self._appointments = appointments

        self.retrieve = async_to_streamed_response_wrapper(
            appointments.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            appointments.list,
        )
