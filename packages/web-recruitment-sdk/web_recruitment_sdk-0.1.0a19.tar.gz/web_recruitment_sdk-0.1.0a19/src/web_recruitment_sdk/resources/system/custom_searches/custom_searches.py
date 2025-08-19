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
from .matching_jobs import (
    MatchingJobsResource,
    AsyncMatchingJobsResource,
    MatchingJobsResourceWithRawResponse,
    AsyncMatchingJobsResourceWithRawResponse,
    MatchingJobsResourceWithStreamingResponse,
    AsyncMatchingJobsResourceWithStreamingResponse,
)
from ...._base_client import make_request_options
from ....types.system.custom_search_list_response import CustomSearchListResponse
from ....types.system.custom_search_retrieve_criteria_response import CustomSearchRetrieveCriteriaResponse

__all__ = ["CustomSearchesResource", "AsyncCustomSearchesResource"]


class CustomSearchesResource(SyncAPIResource):
    @cached_property
    def matching_jobs(self) -> MatchingJobsResource:
        return MatchingJobsResource(self._client)

    @cached_property
    def with_raw_response(self) -> CustomSearchesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return CustomSearchesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CustomSearchesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return CustomSearchesResourceWithStreamingResponse(self)

    def list(
        self,
        tenant_db_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchListResponse:
        """
        Get all custom searches for a tenant

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._get(
            f"/system/{tenant_db_name}/custom-searches",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomSearchListResponse,
        )

    def refresh_patient_matches(
        self,
        tenant_db_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Refresh the materialized view of custom search patient matches.

        NOTE: This
        endpoint could take several minutes to complete for large datasets.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._post(
            f"/system/{tenant_db_name}/custom-searches/refresh-patient-matches",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def retrieve_criteria(
        self,
        custom_search_id: str,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchRetrieveCriteriaResponse:
        """
        Get Custom Search Criteria

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not custom_search_id:
            raise ValueError(f"Expected a non-empty value for `custom_search_id` but received {custom_search_id!r}")
        return self._get(
            f"/system/{tenant_db_name}/custom-searches/{custom_search_id}/criteria",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomSearchRetrieveCriteriaResponse,
        )


class AsyncCustomSearchesResource(AsyncAPIResource):
    @cached_property
    def matching_jobs(self) -> AsyncMatchingJobsResource:
        return AsyncMatchingJobsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncCustomSearchesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncCustomSearchesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCustomSearchesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncCustomSearchesResourceWithStreamingResponse(self)

    async def list(
        self,
        tenant_db_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchListResponse:
        """
        Get all custom searches for a tenant

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._get(
            f"/system/{tenant_db_name}/custom-searches",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomSearchListResponse,
        )

    async def refresh_patient_matches(
        self,
        tenant_db_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Refresh the materialized view of custom search patient matches.

        NOTE: This
        endpoint could take several minutes to complete for large datasets.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._post(
            f"/system/{tenant_db_name}/custom-searches/refresh-patient-matches",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def retrieve_criteria(
        self,
        custom_search_id: str,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchRetrieveCriteriaResponse:
        """
        Get Custom Search Criteria

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not custom_search_id:
            raise ValueError(f"Expected a non-empty value for `custom_search_id` but received {custom_search_id!r}")
        return await self._get(
            f"/system/{tenant_db_name}/custom-searches/{custom_search_id}/criteria",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomSearchRetrieveCriteriaResponse,
        )


class CustomSearchesResourceWithRawResponse:
    def __init__(self, custom_searches: CustomSearchesResource) -> None:
        self._custom_searches = custom_searches

        self.list = to_raw_response_wrapper(
            custom_searches.list,
        )
        self.refresh_patient_matches = to_raw_response_wrapper(
            custom_searches.refresh_patient_matches,
        )
        self.retrieve_criteria = to_raw_response_wrapper(
            custom_searches.retrieve_criteria,
        )

    @cached_property
    def matching_jobs(self) -> MatchingJobsResourceWithRawResponse:
        return MatchingJobsResourceWithRawResponse(self._custom_searches.matching_jobs)


class AsyncCustomSearchesResourceWithRawResponse:
    def __init__(self, custom_searches: AsyncCustomSearchesResource) -> None:
        self._custom_searches = custom_searches

        self.list = async_to_raw_response_wrapper(
            custom_searches.list,
        )
        self.refresh_patient_matches = async_to_raw_response_wrapper(
            custom_searches.refresh_patient_matches,
        )
        self.retrieve_criteria = async_to_raw_response_wrapper(
            custom_searches.retrieve_criteria,
        )

    @cached_property
    def matching_jobs(self) -> AsyncMatchingJobsResourceWithRawResponse:
        return AsyncMatchingJobsResourceWithRawResponse(self._custom_searches.matching_jobs)


class CustomSearchesResourceWithStreamingResponse:
    def __init__(self, custom_searches: CustomSearchesResource) -> None:
        self._custom_searches = custom_searches

        self.list = to_streamed_response_wrapper(
            custom_searches.list,
        )
        self.refresh_patient_matches = to_streamed_response_wrapper(
            custom_searches.refresh_patient_matches,
        )
        self.retrieve_criteria = to_streamed_response_wrapper(
            custom_searches.retrieve_criteria,
        )

    @cached_property
    def matching_jobs(self) -> MatchingJobsResourceWithStreamingResponse:
        return MatchingJobsResourceWithStreamingResponse(self._custom_searches.matching_jobs)


class AsyncCustomSearchesResourceWithStreamingResponse:
    def __init__(self, custom_searches: AsyncCustomSearchesResource) -> None:
        self._custom_searches = custom_searches

        self.list = async_to_streamed_response_wrapper(
            custom_searches.list,
        )
        self.refresh_patient_matches = async_to_streamed_response_wrapper(
            custom_searches.refresh_patient_matches,
        )
        self.retrieve_criteria = async_to_streamed_response_wrapper(
            custom_searches.retrieve_criteria,
        )

    @cached_property
    def matching_jobs(self) -> AsyncMatchingJobsResourceWithStreamingResponse:
        return AsyncMatchingJobsResourceWithStreamingResponse(self._custom_searches.matching_jobs)
