# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional

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
from .matching_jobs import (
    MatchingJobsResource,
    AsyncMatchingJobsResource,
    MatchingJobsResourceWithRawResponse,
    AsyncMatchingJobsResourceWithRawResponse,
    MatchingJobsResourceWithStreamingResponse,
    AsyncMatchingJobsResourceWithStreamingResponse,
)
from ...._base_client import make_request_options
from ....types.system import criterion_list_params
from ....types.system.criterion_list_response import CriterionListResponse
from ....types.system.criterion_get_patients_to_match_response import CriterionGetPatientsToMatchResponse

__all__ = ["CriteriaResource", "AsyncCriteriaResource"]


class CriteriaResource(SyncAPIResource):
    @cached_property
    def matching_jobs(self) -> MatchingJobsResource:
        return MatchingJobsResource(self._client)

    @cached_property
    def with_raw_response(self) -> CriteriaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return CriteriaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CriteriaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return CriteriaResourceWithStreamingResponse(self)

    def list(
        self,
        tenant_db_name: str,
        *,
        criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CriterionListResponse:
        """
        Get Criteria

        Args:
          criteria_ids: List of criteria IDs to match against

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._get(
            f"/system/{tenant_db_name}/criteria",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"criteria_ids": criteria_ids}, criterion_list_params.CriterionListParams),
            ),
            cast_to=CriterionListResponse,
        )

    def get_patients_to_match(
        self,
        criteria_id: str,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CriterionGetPatientsToMatchResponse:
        """
        Get Patients To Match

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not criteria_id:
            raise ValueError(f"Expected a non-empty value for `criteria_id` but received {criteria_id!r}")
        return self._get(
            f"/system/{tenant_db_name}/criteria/{criteria_id}/patients-to-match",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CriterionGetPatientsToMatchResponse,
        )


class AsyncCriteriaResource(AsyncAPIResource):
    @cached_property
    def matching_jobs(self) -> AsyncMatchingJobsResource:
        return AsyncMatchingJobsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncCriteriaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncCriteriaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCriteriaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncCriteriaResourceWithStreamingResponse(self)

    async def list(
        self,
        tenant_db_name: str,
        *,
        criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CriterionListResponse:
        """
        Get Criteria

        Args:
          criteria_ids: List of criteria IDs to match against

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._get(
            f"/system/{tenant_db_name}/criteria",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"criteria_ids": criteria_ids}, criterion_list_params.CriterionListParams
                ),
            ),
            cast_to=CriterionListResponse,
        )

    async def get_patients_to_match(
        self,
        criteria_id: str,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CriterionGetPatientsToMatchResponse:
        """
        Get Patients To Match

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not criteria_id:
            raise ValueError(f"Expected a non-empty value for `criteria_id` but received {criteria_id!r}")
        return await self._get(
            f"/system/{tenant_db_name}/criteria/{criteria_id}/patients-to-match",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CriterionGetPatientsToMatchResponse,
        )


class CriteriaResourceWithRawResponse:
    def __init__(self, criteria: CriteriaResource) -> None:
        self._criteria = criteria

        self.list = to_raw_response_wrapper(
            criteria.list,
        )
        self.get_patients_to_match = to_raw_response_wrapper(
            criteria.get_patients_to_match,
        )

    @cached_property
    def matching_jobs(self) -> MatchingJobsResourceWithRawResponse:
        return MatchingJobsResourceWithRawResponse(self._criteria.matching_jobs)


class AsyncCriteriaResourceWithRawResponse:
    def __init__(self, criteria: AsyncCriteriaResource) -> None:
        self._criteria = criteria

        self.list = async_to_raw_response_wrapper(
            criteria.list,
        )
        self.get_patients_to_match = async_to_raw_response_wrapper(
            criteria.get_patients_to_match,
        )

    @cached_property
    def matching_jobs(self) -> AsyncMatchingJobsResourceWithRawResponse:
        return AsyncMatchingJobsResourceWithRawResponse(self._criteria.matching_jobs)


class CriteriaResourceWithStreamingResponse:
    def __init__(self, criteria: CriteriaResource) -> None:
        self._criteria = criteria

        self.list = to_streamed_response_wrapper(
            criteria.list,
        )
        self.get_patients_to_match = to_streamed_response_wrapper(
            criteria.get_patients_to_match,
        )

    @cached_property
    def matching_jobs(self) -> MatchingJobsResourceWithStreamingResponse:
        return MatchingJobsResourceWithStreamingResponse(self._criteria.matching_jobs)


class AsyncCriteriaResourceWithStreamingResponse:
    def __init__(self, criteria: AsyncCriteriaResource) -> None:
        self._criteria = criteria

        self.list = async_to_streamed_response_wrapper(
            criteria.list,
        )
        self.get_patients_to_match = async_to_streamed_response_wrapper(
            criteria.get_patients_to_match,
        )

    @cached_property
    def matching_jobs(self) -> AsyncMatchingJobsResourceWithStreamingResponse:
        return AsyncMatchingJobsResourceWithStreamingResponse(self._criteria.matching_jobs)
