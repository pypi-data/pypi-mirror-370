# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.system import appointment_list_params
from ...types.system.appointment_list_response import AppointmentListResponse

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

    def list(
        self,
        tenant_db_name: str,
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
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._get(
            f"/system/{tenant_db_name}/appointments",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"limit": limit}, appointment_list_params.AppointmentListParams),
            ),
            cast_to=AppointmentListResponse,
        )

    def delete(
        self,
        trially_appointment_id: str,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete Appointment

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not trially_appointment_id:
            raise ValueError(
                f"Expected a non-empty value for `trially_appointment_id` but received {trially_appointment_id!r}"
            )
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/system/{tenant_db_name}/appointments/{trially_appointment_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
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

    async def list(
        self,
        tenant_db_name: str,
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
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._get(
            f"/system/{tenant_db_name}/appointments",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"limit": limit}, appointment_list_params.AppointmentListParams),
            ),
            cast_to=AppointmentListResponse,
        )

    async def delete(
        self,
        trially_appointment_id: str,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete Appointment

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not trially_appointment_id:
            raise ValueError(
                f"Expected a non-empty value for `trially_appointment_id` but received {trially_appointment_id!r}"
            )
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/system/{tenant_db_name}/appointments/{trially_appointment_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AppointmentsResourceWithRawResponse:
    def __init__(self, appointments: AppointmentsResource) -> None:
        self._appointments = appointments

        self.list = to_raw_response_wrapper(
            appointments.list,
        )
        self.delete = to_raw_response_wrapper(
            appointments.delete,
        )


class AsyncAppointmentsResourceWithRawResponse:
    def __init__(self, appointments: AsyncAppointmentsResource) -> None:
        self._appointments = appointments

        self.list = async_to_raw_response_wrapper(
            appointments.list,
        )
        self.delete = async_to_raw_response_wrapper(
            appointments.delete,
        )


class AppointmentsResourceWithStreamingResponse:
    def __init__(self, appointments: AppointmentsResource) -> None:
        self._appointments = appointments

        self.list = to_streamed_response_wrapper(
            appointments.list,
        )
        self.delete = to_streamed_response_wrapper(
            appointments.delete,
        )


class AsyncAppointmentsResourceWithStreamingResponse:
    def __init__(self, appointments: AsyncAppointmentsResource) -> None:
        self._appointments = appointments

        self.list = async_to_streamed_response_wrapper(
            appointments.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            appointments.delete,
        )
