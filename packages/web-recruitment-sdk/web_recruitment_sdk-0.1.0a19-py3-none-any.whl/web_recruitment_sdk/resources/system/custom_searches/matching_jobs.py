# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.custom_search_read import CustomSearchRead

__all__ = ["MatchingJobsResource", "AsyncMatchingJobsResource"]


class MatchingJobsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MatchingJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return MatchingJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MatchingJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return MatchingJobsResourceWithStreamingResponse(self)

    def create(
        self,
        custom_search_id: int,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchRead:
        """
        Create matching jobs for all criteria and sites of a custom search

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._post(
            f"/system/{tenant_db_name}/custom-searches/{custom_search_id}/matching_jobs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomSearchRead,
        )

    def delete(
        self,
        custom_search_id: int,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Cancel all matching jobs for a custom search

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._delete(
            f"/system/{tenant_db_name}/custom-searches/{custom_search_id}/matching_jobs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncMatchingJobsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMatchingJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncMatchingJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMatchingJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncMatchingJobsResourceWithStreamingResponse(self)

    async def create(
        self,
        custom_search_id: int,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchRead:
        """
        Create matching jobs for all criteria and sites of a custom search

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._post(
            f"/system/{tenant_db_name}/custom-searches/{custom_search_id}/matching_jobs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomSearchRead,
        )

    async def delete(
        self,
        custom_search_id: int,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Cancel all matching jobs for a custom search

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._delete(
            f"/system/{tenant_db_name}/custom-searches/{custom_search_id}/matching_jobs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class MatchingJobsResourceWithRawResponse:
    def __init__(self, matching_jobs: MatchingJobsResource) -> None:
        self._matching_jobs = matching_jobs

        self.create = to_raw_response_wrapper(
            matching_jobs.create,
        )
        self.delete = to_raw_response_wrapper(
            matching_jobs.delete,
        )


class AsyncMatchingJobsResourceWithRawResponse:
    def __init__(self, matching_jobs: AsyncMatchingJobsResource) -> None:
        self._matching_jobs = matching_jobs

        self.create = async_to_raw_response_wrapper(
            matching_jobs.create,
        )
        self.delete = async_to_raw_response_wrapper(
            matching_jobs.delete,
        )


class MatchingJobsResourceWithStreamingResponse:
    def __init__(self, matching_jobs: MatchingJobsResource) -> None:
        self._matching_jobs = matching_jobs

        self.create = to_streamed_response_wrapper(
            matching_jobs.create,
        )
        self.delete = to_streamed_response_wrapper(
            matching_jobs.delete,
        )


class AsyncMatchingJobsResourceWithStreamingResponse:
    def __init__(self, matching_jobs: AsyncMatchingJobsResource) -> None:
        self._matching_jobs = matching_jobs

        self.create = async_to_streamed_response_wrapper(
            matching_jobs.create,
        )
        self.delete = async_to_streamed_response_wrapper(
            matching_jobs.delete,
        )
