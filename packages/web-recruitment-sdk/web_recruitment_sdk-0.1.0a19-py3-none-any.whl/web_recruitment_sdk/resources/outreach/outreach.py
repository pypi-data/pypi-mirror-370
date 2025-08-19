# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ...types import outreach_trigger_call_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
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
from .campaigns.campaigns import (
    CampaignsResource,
    AsyncCampaignsResource,
    CampaignsResourceWithRawResponse,
    AsyncCampaignsResourceWithRawResponse,
    CampaignsResourceWithStreamingResponse,
    AsyncCampaignsResourceWithStreamingResponse,
)
from ...types.outreach_trigger_call_response import OutreachTriggerCallResponse

__all__ = ["OutreachResource", "AsyncOutreachResource"]


class OutreachResource(SyncAPIResource):
    @cached_property
    def campaigns(self) -> CampaignsResource:
        return CampaignsResource(self._client)

    @cached_property
    def with_raw_response(self) -> OutreachResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return OutreachResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OutreachResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return OutreachResourceWithStreamingResponse(self)

    def trigger_call(
        self,
        *,
        call_data: outreach_trigger_call_params.CallData,
        conversation_flow: Literal["study_qualification", "lead_warmer"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OutreachTriggerCallResponse:
        """
        Trigger a phone call to a patient using LiveKit

        Args:
          call_data: Class to store user data and agents during a call.

          conversation_flow: Represents the flow of a conversation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/outreach/make-call",
            body=maybe_transform(
                {
                    "call_data": call_data,
                    "conversation_flow": conversation_flow,
                },
                outreach_trigger_call_params.OutreachTriggerCallParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OutreachTriggerCallResponse,
        )


class AsyncOutreachResource(AsyncAPIResource):
    @cached_property
    def campaigns(self) -> AsyncCampaignsResource:
        return AsyncCampaignsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncOutreachResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncOutreachResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOutreachResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncOutreachResourceWithStreamingResponse(self)

    async def trigger_call(
        self,
        *,
        call_data: outreach_trigger_call_params.CallData,
        conversation_flow: Literal["study_qualification", "lead_warmer"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OutreachTriggerCallResponse:
        """
        Trigger a phone call to a patient using LiveKit

        Args:
          call_data: Class to store user data and agents during a call.

          conversation_flow: Represents the flow of a conversation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/outreach/make-call",
            body=await async_maybe_transform(
                {
                    "call_data": call_data,
                    "conversation_flow": conversation_flow,
                },
                outreach_trigger_call_params.OutreachTriggerCallParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OutreachTriggerCallResponse,
        )


class OutreachResourceWithRawResponse:
    def __init__(self, outreach: OutreachResource) -> None:
        self._outreach = outreach

        self.trigger_call = to_raw_response_wrapper(
            outreach.trigger_call,
        )

    @cached_property
    def campaigns(self) -> CampaignsResourceWithRawResponse:
        return CampaignsResourceWithRawResponse(self._outreach.campaigns)


class AsyncOutreachResourceWithRawResponse:
    def __init__(self, outreach: AsyncOutreachResource) -> None:
        self._outreach = outreach

        self.trigger_call = async_to_raw_response_wrapper(
            outreach.trigger_call,
        )

    @cached_property
    def campaigns(self) -> AsyncCampaignsResourceWithRawResponse:
        return AsyncCampaignsResourceWithRawResponse(self._outreach.campaigns)


class OutreachResourceWithStreamingResponse:
    def __init__(self, outreach: OutreachResource) -> None:
        self._outreach = outreach

        self.trigger_call = to_streamed_response_wrapper(
            outreach.trigger_call,
        )

    @cached_property
    def campaigns(self) -> CampaignsResourceWithStreamingResponse:
        return CampaignsResourceWithStreamingResponse(self._outreach.campaigns)


class AsyncOutreachResourceWithStreamingResponse:
    def __init__(self, outreach: AsyncOutreachResource) -> None:
        self._outreach = outreach

        self.trigger_call = async_to_streamed_response_wrapper(
            outreach.trigger_call,
        )

    @cached_property
    def campaigns(self) -> AsyncCampaignsResourceWithStreamingResponse:
        return AsyncCampaignsResourceWithStreamingResponse(self._outreach.campaigns)
