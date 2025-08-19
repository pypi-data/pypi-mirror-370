# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .actions import (
    ActionsResource,
    AsyncActionsResource,
    ActionsResourceWithRawResponse,
    AsyncActionsResourceWithRawResponse,
    ActionsResourceWithStreamingResponse,
    AsyncActionsResourceWithStreamingResponse,
)
from ....._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.outreach.campaigns.patient_list_response import PatientListResponse

__all__ = ["PatientsResource", "AsyncPatientsResource"]


class PatientsResource(SyncAPIResource):
    @cached_property
    def actions(self) -> ActionsResource:
        return ActionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> PatientsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return PatientsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PatientsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return PatientsResourceWithStreamingResponse(self)

    def list(
        self,
        campaign_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientListResponse:
        """
        Get all patient campaigns for a campaign with patient info and outreach actions

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/outreach/campaigns/{campaign_id}/patients",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientListResponse,
        )


class AsyncPatientsResource(AsyncAPIResource):
    @cached_property
    def actions(self) -> AsyncActionsResource:
        return AsyncActionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncPatientsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncPatientsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPatientsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncPatientsResourceWithStreamingResponse(self)

    async def list(
        self,
        campaign_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientListResponse:
        """
        Get all patient campaigns for a campaign with patient info and outreach actions

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/outreach/campaigns/{campaign_id}/patients",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientListResponse,
        )


class PatientsResourceWithRawResponse:
    def __init__(self, patients: PatientsResource) -> None:
        self._patients = patients

        self.list = to_raw_response_wrapper(
            patients.list,
        )

    @cached_property
    def actions(self) -> ActionsResourceWithRawResponse:
        return ActionsResourceWithRawResponse(self._patients.actions)


class AsyncPatientsResourceWithRawResponse:
    def __init__(self, patients: AsyncPatientsResource) -> None:
        self._patients = patients

        self.list = async_to_raw_response_wrapper(
            patients.list,
        )

    @cached_property
    def actions(self) -> AsyncActionsResourceWithRawResponse:
        return AsyncActionsResourceWithRawResponse(self._patients.actions)


class PatientsResourceWithStreamingResponse:
    def __init__(self, patients: PatientsResource) -> None:
        self._patients = patients

        self.list = to_streamed_response_wrapper(
            patients.list,
        )

    @cached_property
    def actions(self) -> ActionsResourceWithStreamingResponse:
        return ActionsResourceWithStreamingResponse(self._patients.actions)


class AsyncPatientsResourceWithStreamingResponse:
    def __init__(self, patients: AsyncPatientsResource) -> None:
        self._patients = patients

        self.list = async_to_streamed_response_wrapper(
            patients.list,
        )

    @cached_property
    def actions(self) -> AsyncActionsResourceWithStreamingResponse:
        return AsyncActionsResourceWithStreamingResponse(self._patients.actions)
