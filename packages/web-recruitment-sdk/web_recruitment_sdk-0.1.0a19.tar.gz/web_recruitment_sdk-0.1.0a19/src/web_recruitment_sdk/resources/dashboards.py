# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional

import httpx

from ..types import (
    dashboard_get_top_conditions_params,
    dashboard_get_top_procedures_params,
    dashboard_get_top_medications_params,
    dashboard_get_age_distribution_params,
    dashboard_get_race_distribution_params,
    dashboard_get_ethnic_distribution_params,
    dashboard_get_gender_distribution_params,
)
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
from ..types.chart_response import ChartResponse

__all__ = ["DashboardsResource", "AsyncDashboardsResource"]


class DashboardsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DashboardsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return DashboardsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DashboardsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return DashboardsResourceWithStreamingResponse(self)

    def get_age_distribution(
        self,
        *,
        custom_search_id: Optional[int] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        protocol_id: Optional[int] | NotGiven = NOT_GIVEN,
        step: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChartResponse:
        """
        Get age distribution across sites

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/dashboards/age-distribution",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "custom_search_id": custom_search_id,
                        "limit": limit,
                        "matching_criteria_ids": matching_criteria_ids,
                        "protocol_id": protocol_id,
                        "step": step,
                    },
                    dashboard_get_age_distribution_params.DashboardGetAgeDistributionParams,
                ),
            ),
            cast_to=ChartResponse,
        )

    def get_ethnic_distribution(
        self,
        *,
        custom_search_id: Optional[int] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        protocol_id: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChartResponse:
        """
        Get ethnic distribution across sites

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/dashboards/ethnic-distribution",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "custom_search_id": custom_search_id,
                        "limit": limit,
                        "matching_criteria_ids": matching_criteria_ids,
                        "protocol_id": protocol_id,
                    },
                    dashboard_get_ethnic_distribution_params.DashboardGetEthnicDistributionParams,
                ),
            ),
            cast_to=ChartResponse,
        )

    def get_gender_distribution(
        self,
        *,
        custom_search_id: Optional[int] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        protocol_id: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChartResponse:
        """
        Get gender distribution across sites

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/dashboards/gender-distribution",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "custom_search_id": custom_search_id,
                        "limit": limit,
                        "matching_criteria_ids": matching_criteria_ids,
                        "protocol_id": protocol_id,
                    },
                    dashboard_get_gender_distribution_params.DashboardGetGenderDistributionParams,
                ),
            ),
            cast_to=ChartResponse,
        )

    def get_race_distribution(
        self,
        *,
        custom_search_id: Optional[int] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        protocol_id: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChartResponse:
        """
        Get race distribution across sites

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/dashboards/race-distribution",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "custom_search_id": custom_search_id,
                        "limit": limit,
                        "matching_criteria_ids": matching_criteria_ids,
                        "protocol_id": protocol_id,
                    },
                    dashboard_get_race_distribution_params.DashboardGetRaceDistributionParams,
                ),
            ),
            cast_to=ChartResponse,
        )

    def get_top_conditions(
        self,
        *,
        custom_search_id: Optional[int] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        protocol_id: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChartResponse:
        """
        Get top conditions across sites

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/dashboards/conditions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "custom_search_id": custom_search_id,
                        "limit": limit,
                        "matching_criteria_ids": matching_criteria_ids,
                        "protocol_id": protocol_id,
                    },
                    dashboard_get_top_conditions_params.DashboardGetTopConditionsParams,
                ),
            ),
            cast_to=ChartResponse,
        )

    def get_top_medications(
        self,
        *,
        custom_search_id: Optional[int] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        protocol_id: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChartResponse:
        """
        Get top medications across sites

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/dashboards/medications",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "custom_search_id": custom_search_id,
                        "limit": limit,
                        "matching_criteria_ids": matching_criteria_ids,
                        "protocol_id": protocol_id,
                    },
                    dashboard_get_top_medications_params.DashboardGetTopMedicationsParams,
                ),
            ),
            cast_to=ChartResponse,
        )

    def get_top_procedures(
        self,
        *,
        custom_search_id: Optional[int] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        protocol_id: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChartResponse:
        """
        Get top procedures across sites

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/dashboards/procedures",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "custom_search_id": custom_search_id,
                        "limit": limit,
                        "matching_criteria_ids": matching_criteria_ids,
                        "protocol_id": protocol_id,
                    },
                    dashboard_get_top_procedures_params.DashboardGetTopProceduresParams,
                ),
            ),
            cast_to=ChartResponse,
        )


class AsyncDashboardsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDashboardsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncDashboardsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDashboardsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncDashboardsResourceWithStreamingResponse(self)

    async def get_age_distribution(
        self,
        *,
        custom_search_id: Optional[int] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        protocol_id: Optional[int] | NotGiven = NOT_GIVEN,
        step: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChartResponse:
        """
        Get age distribution across sites

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/dashboards/age-distribution",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "custom_search_id": custom_search_id,
                        "limit": limit,
                        "matching_criteria_ids": matching_criteria_ids,
                        "protocol_id": protocol_id,
                        "step": step,
                    },
                    dashboard_get_age_distribution_params.DashboardGetAgeDistributionParams,
                ),
            ),
            cast_to=ChartResponse,
        )

    async def get_ethnic_distribution(
        self,
        *,
        custom_search_id: Optional[int] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        protocol_id: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChartResponse:
        """
        Get ethnic distribution across sites

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/dashboards/ethnic-distribution",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "custom_search_id": custom_search_id,
                        "limit": limit,
                        "matching_criteria_ids": matching_criteria_ids,
                        "protocol_id": protocol_id,
                    },
                    dashboard_get_ethnic_distribution_params.DashboardGetEthnicDistributionParams,
                ),
            ),
            cast_to=ChartResponse,
        )

    async def get_gender_distribution(
        self,
        *,
        custom_search_id: Optional[int] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        protocol_id: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChartResponse:
        """
        Get gender distribution across sites

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/dashboards/gender-distribution",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "custom_search_id": custom_search_id,
                        "limit": limit,
                        "matching_criteria_ids": matching_criteria_ids,
                        "protocol_id": protocol_id,
                    },
                    dashboard_get_gender_distribution_params.DashboardGetGenderDistributionParams,
                ),
            ),
            cast_to=ChartResponse,
        )

    async def get_race_distribution(
        self,
        *,
        custom_search_id: Optional[int] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        protocol_id: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChartResponse:
        """
        Get race distribution across sites

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/dashboards/race-distribution",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "custom_search_id": custom_search_id,
                        "limit": limit,
                        "matching_criteria_ids": matching_criteria_ids,
                        "protocol_id": protocol_id,
                    },
                    dashboard_get_race_distribution_params.DashboardGetRaceDistributionParams,
                ),
            ),
            cast_to=ChartResponse,
        )

    async def get_top_conditions(
        self,
        *,
        custom_search_id: Optional[int] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        protocol_id: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChartResponse:
        """
        Get top conditions across sites

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/dashboards/conditions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "custom_search_id": custom_search_id,
                        "limit": limit,
                        "matching_criteria_ids": matching_criteria_ids,
                        "protocol_id": protocol_id,
                    },
                    dashboard_get_top_conditions_params.DashboardGetTopConditionsParams,
                ),
            ),
            cast_to=ChartResponse,
        )

    async def get_top_medications(
        self,
        *,
        custom_search_id: Optional[int] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        protocol_id: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChartResponse:
        """
        Get top medications across sites

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/dashboards/medications",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "custom_search_id": custom_search_id,
                        "limit": limit,
                        "matching_criteria_ids": matching_criteria_ids,
                        "protocol_id": protocol_id,
                    },
                    dashboard_get_top_medications_params.DashboardGetTopMedicationsParams,
                ),
            ),
            cast_to=ChartResponse,
        )

    async def get_top_procedures(
        self,
        *,
        custom_search_id: Optional[int] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        protocol_id: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChartResponse:
        """
        Get top procedures across sites

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/dashboards/procedures",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "custom_search_id": custom_search_id,
                        "limit": limit,
                        "matching_criteria_ids": matching_criteria_ids,
                        "protocol_id": protocol_id,
                    },
                    dashboard_get_top_procedures_params.DashboardGetTopProceduresParams,
                ),
            ),
            cast_to=ChartResponse,
        )


class DashboardsResourceWithRawResponse:
    def __init__(self, dashboards: DashboardsResource) -> None:
        self._dashboards = dashboards

        self.get_age_distribution = to_raw_response_wrapper(
            dashboards.get_age_distribution,
        )
        self.get_ethnic_distribution = to_raw_response_wrapper(
            dashboards.get_ethnic_distribution,
        )
        self.get_gender_distribution = to_raw_response_wrapper(
            dashboards.get_gender_distribution,
        )
        self.get_race_distribution = to_raw_response_wrapper(
            dashboards.get_race_distribution,
        )
        self.get_top_conditions = to_raw_response_wrapper(
            dashboards.get_top_conditions,
        )
        self.get_top_medications = to_raw_response_wrapper(
            dashboards.get_top_medications,
        )
        self.get_top_procedures = to_raw_response_wrapper(
            dashboards.get_top_procedures,
        )


class AsyncDashboardsResourceWithRawResponse:
    def __init__(self, dashboards: AsyncDashboardsResource) -> None:
        self._dashboards = dashboards

        self.get_age_distribution = async_to_raw_response_wrapper(
            dashboards.get_age_distribution,
        )
        self.get_ethnic_distribution = async_to_raw_response_wrapper(
            dashboards.get_ethnic_distribution,
        )
        self.get_gender_distribution = async_to_raw_response_wrapper(
            dashboards.get_gender_distribution,
        )
        self.get_race_distribution = async_to_raw_response_wrapper(
            dashboards.get_race_distribution,
        )
        self.get_top_conditions = async_to_raw_response_wrapper(
            dashboards.get_top_conditions,
        )
        self.get_top_medications = async_to_raw_response_wrapper(
            dashboards.get_top_medications,
        )
        self.get_top_procedures = async_to_raw_response_wrapper(
            dashboards.get_top_procedures,
        )


class DashboardsResourceWithStreamingResponse:
    def __init__(self, dashboards: DashboardsResource) -> None:
        self._dashboards = dashboards

        self.get_age_distribution = to_streamed_response_wrapper(
            dashboards.get_age_distribution,
        )
        self.get_ethnic_distribution = to_streamed_response_wrapper(
            dashboards.get_ethnic_distribution,
        )
        self.get_gender_distribution = to_streamed_response_wrapper(
            dashboards.get_gender_distribution,
        )
        self.get_race_distribution = to_streamed_response_wrapper(
            dashboards.get_race_distribution,
        )
        self.get_top_conditions = to_streamed_response_wrapper(
            dashboards.get_top_conditions,
        )
        self.get_top_medications = to_streamed_response_wrapper(
            dashboards.get_top_medications,
        )
        self.get_top_procedures = to_streamed_response_wrapper(
            dashboards.get_top_procedures,
        )


class AsyncDashboardsResourceWithStreamingResponse:
    def __init__(self, dashboards: AsyncDashboardsResource) -> None:
        self._dashboards = dashboards

        self.get_age_distribution = async_to_streamed_response_wrapper(
            dashboards.get_age_distribution,
        )
        self.get_ethnic_distribution = async_to_streamed_response_wrapper(
            dashboards.get_ethnic_distribution,
        )
        self.get_gender_distribution = async_to_streamed_response_wrapper(
            dashboards.get_gender_distribution,
        )
        self.get_race_distribution = async_to_streamed_response_wrapper(
            dashboards.get_race_distribution,
        )
        self.get_top_conditions = async_to_streamed_response_wrapper(
            dashboards.get_top_conditions,
        )
        self.get_top_medications = async_to_streamed_response_wrapper(
            dashboards.get_top_medications,
        )
        self.get_top_procedures = async_to_streamed_response_wrapper(
            dashboards.get_top_procedures,
        )
