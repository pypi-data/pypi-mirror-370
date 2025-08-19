# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from datetime import date
from typing_extensions import Literal

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.outreach import campaign_create_params
from .patients.patients import (
    PatientsResource,
    AsyncPatientsResource,
    PatientsResourceWithRawResponse,
    AsyncPatientsResourceWithRawResponse,
    PatientsResourceWithStreamingResponse,
    AsyncPatientsResourceWithStreamingResponse,
)
from ....types.outreach.campaign_list_response import CampaignListResponse
from ....types.outreach.campaign_pause_response import CampaignPauseResponse
from ....types.outreach.campaign_start_response import CampaignStartResponse
from ....types.outreach.campaign_create_response import CampaignCreateResponse

__all__ = ["CampaignsResource", "AsyncCampaignsResource"]


class CampaignsResource(SyncAPIResource):
    @cached_property
    def patients(self) -> PatientsResource:
        return PatientsResource(self._client)

    @cached_property
    def with_raw_response(self) -> CampaignsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return CampaignsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CampaignsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return CampaignsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        action_type: Literal["PHONE_CALL", "SMS"],
        booking_url: str,
        end_date: Union[str, date],
        from_phone_number: str,
        hours_between_attempts: int,
        max_attempts_per_patient: int,
        name: str,
        outreach_hours_end: int,
        outreach_hours_start: int,
        patient_ids: List[str],
        start_date: Union[str, date],
        principal_investigator: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CampaignCreateResponse:
        """
        Create a new outreach campaign with patient validation.

        Campaign dates (start_date, end_date) specify day boundaries - the first and
        last days when outreach can occur. Actual outreach times are determined by
        outreach_hours_start/end in each patient's local timezone.

        Args:
          action_type: Type of outreach action to perform

          end_date: Last day of the campaign (YYYY-MM-DD)

          from_phone_number: Phone number to use as the 'from' number for calls

          hours_between_attempts: Minimum hours between outreach attempts

          max_attempts_per_patient: Maximum number of outreach attempts per patient

          outreach_hours_end: End hour for outreach in patient's local timezone (0-23)

          outreach_hours_start: Start hour for outreach in patient's local timezone (0-23)

          patient_ids: List of patient IDs to include in campaign

          start_date: First day of the campaign (YYYY-MM-DD)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/outreach/campaigns",
            body=maybe_transform(
                {
                    "action_type": action_type,
                    "booking_url": booking_url,
                    "end_date": end_date,
                    "from_phone_number": from_phone_number,
                    "hours_between_attempts": hours_between_attempts,
                    "max_attempts_per_patient": max_attempts_per_patient,
                    "name": name,
                    "outreach_hours_end": outreach_hours_end,
                    "outreach_hours_start": outreach_hours_start,
                    "patient_ids": patient_ids,
                    "start_date": start_date,
                    "principal_investigator": principal_investigator,
                },
                campaign_create_params.CampaignCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CampaignCreateResponse,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CampaignListResponse:
        """Get all outreach campaigns"""
        return self._get(
            "/outreach/campaigns",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CampaignListResponse,
        )

    def pause(
        self,
        campaign_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CampaignPauseResponse:
        """
        Pause an outreach campaign

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            f"/outreach/campaigns/{campaign_id}/pause",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CampaignPauseResponse,
        )

    def start(
        self,
        campaign_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CampaignStartResponse:
        """
        Start or resume an outreach campaign (NOT_STARTED or PAUSED)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            f"/outreach/campaigns/{campaign_id}/start",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CampaignStartResponse,
        )


class AsyncCampaignsResource(AsyncAPIResource):
    @cached_property
    def patients(self) -> AsyncPatientsResource:
        return AsyncPatientsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncCampaignsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncCampaignsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCampaignsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncCampaignsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        action_type: Literal["PHONE_CALL", "SMS"],
        booking_url: str,
        end_date: Union[str, date],
        from_phone_number: str,
        hours_between_attempts: int,
        max_attempts_per_patient: int,
        name: str,
        outreach_hours_end: int,
        outreach_hours_start: int,
        patient_ids: List[str],
        start_date: Union[str, date],
        principal_investigator: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CampaignCreateResponse:
        """
        Create a new outreach campaign with patient validation.

        Campaign dates (start_date, end_date) specify day boundaries - the first and
        last days when outreach can occur. Actual outreach times are determined by
        outreach_hours_start/end in each patient's local timezone.

        Args:
          action_type: Type of outreach action to perform

          end_date: Last day of the campaign (YYYY-MM-DD)

          from_phone_number: Phone number to use as the 'from' number for calls

          hours_between_attempts: Minimum hours between outreach attempts

          max_attempts_per_patient: Maximum number of outreach attempts per patient

          outreach_hours_end: End hour for outreach in patient's local timezone (0-23)

          outreach_hours_start: Start hour for outreach in patient's local timezone (0-23)

          patient_ids: List of patient IDs to include in campaign

          start_date: First day of the campaign (YYYY-MM-DD)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/outreach/campaigns",
            body=await async_maybe_transform(
                {
                    "action_type": action_type,
                    "booking_url": booking_url,
                    "end_date": end_date,
                    "from_phone_number": from_phone_number,
                    "hours_between_attempts": hours_between_attempts,
                    "max_attempts_per_patient": max_attempts_per_patient,
                    "name": name,
                    "outreach_hours_end": outreach_hours_end,
                    "outreach_hours_start": outreach_hours_start,
                    "patient_ids": patient_ids,
                    "start_date": start_date,
                    "principal_investigator": principal_investigator,
                },
                campaign_create_params.CampaignCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CampaignCreateResponse,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CampaignListResponse:
        """Get all outreach campaigns"""
        return await self._get(
            "/outreach/campaigns",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CampaignListResponse,
        )

    async def pause(
        self,
        campaign_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CampaignPauseResponse:
        """
        Pause an outreach campaign

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            f"/outreach/campaigns/{campaign_id}/pause",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CampaignPauseResponse,
        )

    async def start(
        self,
        campaign_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CampaignStartResponse:
        """
        Start or resume an outreach campaign (NOT_STARTED or PAUSED)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            f"/outreach/campaigns/{campaign_id}/start",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CampaignStartResponse,
        )


class CampaignsResourceWithRawResponse:
    def __init__(self, campaigns: CampaignsResource) -> None:
        self._campaigns = campaigns

        self.create = to_raw_response_wrapper(
            campaigns.create,
        )
        self.list = to_raw_response_wrapper(
            campaigns.list,
        )
        self.pause = to_raw_response_wrapper(
            campaigns.pause,
        )
        self.start = to_raw_response_wrapper(
            campaigns.start,
        )

    @cached_property
    def patients(self) -> PatientsResourceWithRawResponse:
        return PatientsResourceWithRawResponse(self._campaigns.patients)


class AsyncCampaignsResourceWithRawResponse:
    def __init__(self, campaigns: AsyncCampaignsResource) -> None:
        self._campaigns = campaigns

        self.create = async_to_raw_response_wrapper(
            campaigns.create,
        )
        self.list = async_to_raw_response_wrapper(
            campaigns.list,
        )
        self.pause = async_to_raw_response_wrapper(
            campaigns.pause,
        )
        self.start = async_to_raw_response_wrapper(
            campaigns.start,
        )

    @cached_property
    def patients(self) -> AsyncPatientsResourceWithRawResponse:
        return AsyncPatientsResourceWithRawResponse(self._campaigns.patients)


class CampaignsResourceWithStreamingResponse:
    def __init__(self, campaigns: CampaignsResource) -> None:
        self._campaigns = campaigns

        self.create = to_streamed_response_wrapper(
            campaigns.create,
        )
        self.list = to_streamed_response_wrapper(
            campaigns.list,
        )
        self.pause = to_streamed_response_wrapper(
            campaigns.pause,
        )
        self.start = to_streamed_response_wrapper(
            campaigns.start,
        )

    @cached_property
    def patients(self) -> PatientsResourceWithStreamingResponse:
        return PatientsResourceWithStreamingResponse(self._campaigns.patients)


class AsyncCampaignsResourceWithStreamingResponse:
    def __init__(self, campaigns: AsyncCampaignsResource) -> None:
        self._campaigns = campaigns

        self.create = async_to_streamed_response_wrapper(
            campaigns.create,
        )
        self.list = async_to_streamed_response_wrapper(
            campaigns.list,
        )
        self.pause = async_to_streamed_response_wrapper(
            campaigns.pause,
        )
        self.start = async_to_streamed_response_wrapper(
            campaigns.start,
        )

    @cached_property
    def patients(self) -> AsyncPatientsResourceWithStreamingResponse:
        return AsyncPatientsResourceWithStreamingResponse(self._campaigns.patients)
