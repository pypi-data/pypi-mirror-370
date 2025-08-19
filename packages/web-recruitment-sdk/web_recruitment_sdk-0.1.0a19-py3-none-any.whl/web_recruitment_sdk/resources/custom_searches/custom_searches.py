# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional

import httpx

from ...types import (
    custom_search_patch_params,
    custom_search_create_params,
    custom_search_update_params,
    custom_search_retrieve_funnel_params,
    custom_search_retrieve_matches_params,
    custom_search_get_criteria_instances_params,
)
from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from .criteria import (
    CriteriaResource,
    AsyncCriteriaResource,
    CriteriaResourceWithRawResponse,
    AsyncCriteriaResourceWithRawResponse,
    CriteriaResourceWithStreamingResponse,
    AsyncCriteriaResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .user_criteria import (
    UserCriteriaResource,
    AsyncUserCriteriaResource,
    UserCriteriaResourceWithRawResponse,
    AsyncUserCriteriaResourceWithRawResponse,
    UserCriteriaResourceWithStreamingResponse,
    AsyncUserCriteriaResourceWithStreamingResponse,
)
from ..._base_client import make_request_options
from ...types.funnel_stats import FunnelStats
from ...types.custom_search_read import CustomSearchRead
from ...types.custom_search_list_response import CustomSearchListResponse
from ...types.custom_search_retrieve_sites_response import CustomSearchRetrieveSitesResponse
from ...types.custom_search_retrieve_matches_response import CustomSearchRetrieveMatchesResponse
from ...types.custom_search_get_criteria_instances_response import CustomSearchGetCriteriaInstancesResponse

__all__ = ["CustomSearchesResource", "AsyncCustomSearchesResource"]


class CustomSearchesResource(SyncAPIResource):
    @cached_property
    def criteria(self) -> CriteriaResource:
        return CriteriaResource(self._client)

    @cached_property
    def user_criteria(self) -> UserCriteriaResource:
        return UserCriteriaResource(self._client)

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

    def create(
        self,
        *,
        title: str,
        site_ids: Iterable[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchRead:
        """
        Create Custom Search

        Args:
          site_ids: The site IDs to associate with the custom search

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/custom-searches",
            body=maybe_transform(
                {
                    "title": title,
                    "site_ids": site_ids,
                },
                custom_search_create_params.CustomSearchCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomSearchRead,
        )

    def retrieve(
        self,
        custom_search_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchRead:
        """
        Get Custom Search

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/custom-searches/{custom_search_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomSearchRead,
        )

    def update(
        self,
        custom_search_id: int,
        *,
        sites: Optional[Iterable[custom_search_update_params.Site]] | NotGiven = NOT_GIVEN,
        title: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchRead:
        """
        Patch Custom Search

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._patch(
            f"/custom-searches/{custom_search_id}",
            body=maybe_transform(
                {
                    "sites": sites,
                    "title": title,
                },
                custom_search_update_params.CustomSearchUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomSearchRead,
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
    ) -> CustomSearchListResponse:
        """Get Custom Searches"""
        return self._get(
            "/custom-searches",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomSearchListResponse,
        )

    def delete(
        self,
        custom_search_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete Custom Search

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/custom-searches/{custom_search_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get_criteria_instances(
        self,
        custom_search_id: int,
        *,
        trially_patient_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchGetCriteriaInstancesResponse:
        """
        Get Custom Search Criteria Instances

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/custom-searches/{custom_search_id}/criteria_instances",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"trially_patient_id": trially_patient_id},
                    custom_search_get_criteria_instances_params.CustomSearchGetCriteriaInstancesParams,
                ),
            ),
            cast_to=CustomSearchGetCriteriaInstancesResponse,
        )

    def patch(
        self,
        custom_search_id: int,
        *,
        sites: Optional[Iterable[custom_search_patch_params.Site]] | NotGiven = NOT_GIVEN,
        title: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchRead:
        """
        Patch Custom Search V2

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._patch(
            f"/v2/custom-searches/{custom_search_id}",
            body=maybe_transform(
                {
                    "sites": sites,
                    "title": title,
                },
                custom_search_patch_params.CustomSearchPatchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomSearchRead,
        )

    def retrieve_funnel(
        self,
        custom_search_id: int,
        *,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        site_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FunnelStats:
        """
        Get Custom Search Funnel

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/custom-searches/{custom_search_id}/funnel",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "matching_criteria_ids": matching_criteria_ids,
                        "site_ids": site_ids,
                    },
                    custom_search_retrieve_funnel_params.CustomSearchRetrieveFunnelParams,
                ),
            ),
            cast_to=FunnelStats,
        )

    def retrieve_matches(
        self,
        custom_search_id: int,
        *,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchRetrieveMatchesResponse:
        """
        Get Custom Search Matches

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/custom-searches/{custom_search_id}/matches",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"matching_criteria_ids": matching_criteria_ids},
                    custom_search_retrieve_matches_params.CustomSearchRetrieveMatchesParams,
                ),
            ),
            cast_to=CustomSearchRetrieveMatchesResponse,
        )

    def retrieve_sites(
        self,
        custom_search_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchRetrieveSitesResponse:
        """
        Get Custom Search Sites

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/custom-searches/{custom_search_id}/sites",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomSearchRetrieveSitesResponse,
        )


class AsyncCustomSearchesResource(AsyncAPIResource):
    @cached_property
    def criteria(self) -> AsyncCriteriaResource:
        return AsyncCriteriaResource(self._client)

    @cached_property
    def user_criteria(self) -> AsyncUserCriteriaResource:
        return AsyncUserCriteriaResource(self._client)

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

    async def create(
        self,
        *,
        title: str,
        site_ids: Iterable[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchRead:
        """
        Create Custom Search

        Args:
          site_ids: The site IDs to associate with the custom search

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/custom-searches",
            body=await async_maybe_transform(
                {
                    "title": title,
                    "site_ids": site_ids,
                },
                custom_search_create_params.CustomSearchCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomSearchRead,
        )

    async def retrieve(
        self,
        custom_search_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchRead:
        """
        Get Custom Search

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/custom-searches/{custom_search_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomSearchRead,
        )

    async def update(
        self,
        custom_search_id: int,
        *,
        sites: Optional[Iterable[custom_search_update_params.Site]] | NotGiven = NOT_GIVEN,
        title: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchRead:
        """
        Patch Custom Search

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._patch(
            f"/custom-searches/{custom_search_id}",
            body=await async_maybe_transform(
                {
                    "sites": sites,
                    "title": title,
                },
                custom_search_update_params.CustomSearchUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomSearchRead,
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
    ) -> CustomSearchListResponse:
        """Get Custom Searches"""
        return await self._get(
            "/custom-searches",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomSearchListResponse,
        )

    async def delete(
        self,
        custom_search_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete Custom Search

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/custom-searches/{custom_search_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get_criteria_instances(
        self,
        custom_search_id: int,
        *,
        trially_patient_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchGetCriteriaInstancesResponse:
        """
        Get Custom Search Criteria Instances

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/custom-searches/{custom_search_id}/criteria_instances",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"trially_patient_id": trially_patient_id},
                    custom_search_get_criteria_instances_params.CustomSearchGetCriteriaInstancesParams,
                ),
            ),
            cast_to=CustomSearchGetCriteriaInstancesResponse,
        )

    async def patch(
        self,
        custom_search_id: int,
        *,
        sites: Optional[Iterable[custom_search_patch_params.Site]] | NotGiven = NOT_GIVEN,
        title: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchRead:
        """
        Patch Custom Search V2

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._patch(
            f"/v2/custom-searches/{custom_search_id}",
            body=await async_maybe_transform(
                {
                    "sites": sites,
                    "title": title,
                },
                custom_search_patch_params.CustomSearchPatchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomSearchRead,
        )

    async def retrieve_funnel(
        self,
        custom_search_id: int,
        *,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        site_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FunnelStats:
        """
        Get Custom Search Funnel

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/custom-searches/{custom_search_id}/funnel",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "matching_criteria_ids": matching_criteria_ids,
                        "site_ids": site_ids,
                    },
                    custom_search_retrieve_funnel_params.CustomSearchRetrieveFunnelParams,
                ),
            ),
            cast_to=FunnelStats,
        )

    async def retrieve_matches(
        self,
        custom_search_id: int,
        *,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchRetrieveMatchesResponse:
        """
        Get Custom Search Matches

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/custom-searches/{custom_search_id}/matches",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"matching_criteria_ids": matching_criteria_ids},
                    custom_search_retrieve_matches_params.CustomSearchRetrieveMatchesParams,
                ),
            ),
            cast_to=CustomSearchRetrieveMatchesResponse,
        )

    async def retrieve_sites(
        self,
        custom_search_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomSearchRetrieveSitesResponse:
        """
        Get Custom Search Sites

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/custom-searches/{custom_search_id}/sites",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomSearchRetrieveSitesResponse,
        )


class CustomSearchesResourceWithRawResponse:
    def __init__(self, custom_searches: CustomSearchesResource) -> None:
        self._custom_searches = custom_searches

        self.create = to_raw_response_wrapper(
            custom_searches.create,
        )
        self.retrieve = to_raw_response_wrapper(
            custom_searches.retrieve,
        )
        self.update = to_raw_response_wrapper(
            custom_searches.update,
        )
        self.list = to_raw_response_wrapper(
            custom_searches.list,
        )
        self.delete = to_raw_response_wrapper(
            custom_searches.delete,
        )
        self.get_criteria_instances = to_raw_response_wrapper(
            custom_searches.get_criteria_instances,
        )
        self.patch = to_raw_response_wrapper(
            custom_searches.patch,
        )
        self.retrieve_funnel = to_raw_response_wrapper(
            custom_searches.retrieve_funnel,
        )
        self.retrieve_matches = to_raw_response_wrapper(
            custom_searches.retrieve_matches,
        )
        self.retrieve_sites = to_raw_response_wrapper(
            custom_searches.retrieve_sites,
        )

    @cached_property
    def criteria(self) -> CriteriaResourceWithRawResponse:
        return CriteriaResourceWithRawResponse(self._custom_searches.criteria)

    @cached_property
    def user_criteria(self) -> UserCriteriaResourceWithRawResponse:
        return UserCriteriaResourceWithRawResponse(self._custom_searches.user_criteria)


class AsyncCustomSearchesResourceWithRawResponse:
    def __init__(self, custom_searches: AsyncCustomSearchesResource) -> None:
        self._custom_searches = custom_searches

        self.create = async_to_raw_response_wrapper(
            custom_searches.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            custom_searches.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            custom_searches.update,
        )
        self.list = async_to_raw_response_wrapper(
            custom_searches.list,
        )
        self.delete = async_to_raw_response_wrapper(
            custom_searches.delete,
        )
        self.get_criteria_instances = async_to_raw_response_wrapper(
            custom_searches.get_criteria_instances,
        )
        self.patch = async_to_raw_response_wrapper(
            custom_searches.patch,
        )
        self.retrieve_funnel = async_to_raw_response_wrapper(
            custom_searches.retrieve_funnel,
        )
        self.retrieve_matches = async_to_raw_response_wrapper(
            custom_searches.retrieve_matches,
        )
        self.retrieve_sites = async_to_raw_response_wrapper(
            custom_searches.retrieve_sites,
        )

    @cached_property
    def criteria(self) -> AsyncCriteriaResourceWithRawResponse:
        return AsyncCriteriaResourceWithRawResponse(self._custom_searches.criteria)

    @cached_property
    def user_criteria(self) -> AsyncUserCriteriaResourceWithRawResponse:
        return AsyncUserCriteriaResourceWithRawResponse(self._custom_searches.user_criteria)


class CustomSearchesResourceWithStreamingResponse:
    def __init__(self, custom_searches: CustomSearchesResource) -> None:
        self._custom_searches = custom_searches

        self.create = to_streamed_response_wrapper(
            custom_searches.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            custom_searches.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            custom_searches.update,
        )
        self.list = to_streamed_response_wrapper(
            custom_searches.list,
        )
        self.delete = to_streamed_response_wrapper(
            custom_searches.delete,
        )
        self.get_criteria_instances = to_streamed_response_wrapper(
            custom_searches.get_criteria_instances,
        )
        self.patch = to_streamed_response_wrapper(
            custom_searches.patch,
        )
        self.retrieve_funnel = to_streamed_response_wrapper(
            custom_searches.retrieve_funnel,
        )
        self.retrieve_matches = to_streamed_response_wrapper(
            custom_searches.retrieve_matches,
        )
        self.retrieve_sites = to_streamed_response_wrapper(
            custom_searches.retrieve_sites,
        )

    @cached_property
    def criteria(self) -> CriteriaResourceWithStreamingResponse:
        return CriteriaResourceWithStreamingResponse(self._custom_searches.criteria)

    @cached_property
    def user_criteria(self) -> UserCriteriaResourceWithStreamingResponse:
        return UserCriteriaResourceWithStreamingResponse(self._custom_searches.user_criteria)


class AsyncCustomSearchesResourceWithStreamingResponse:
    def __init__(self, custom_searches: AsyncCustomSearchesResource) -> None:
        self._custom_searches = custom_searches

        self.create = async_to_streamed_response_wrapper(
            custom_searches.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            custom_searches.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            custom_searches.update,
        )
        self.list = async_to_streamed_response_wrapper(
            custom_searches.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            custom_searches.delete,
        )
        self.get_criteria_instances = async_to_streamed_response_wrapper(
            custom_searches.get_criteria_instances,
        )
        self.patch = async_to_streamed_response_wrapper(
            custom_searches.patch,
        )
        self.retrieve_funnel = async_to_streamed_response_wrapper(
            custom_searches.retrieve_funnel,
        )
        self.retrieve_matches = async_to_streamed_response_wrapper(
            custom_searches.retrieve_matches,
        )
        self.retrieve_sites = async_to_streamed_response_wrapper(
            custom_searches.retrieve_sites,
        )

    @cached_property
    def criteria(self) -> AsyncCriteriaResourceWithStreamingResponse:
        return AsyncCriteriaResourceWithStreamingResponse(self._custom_searches.criteria)

    @cached_property
    def user_criteria(self) -> AsyncUserCriteriaResourceWithStreamingResponse:
        return AsyncUserCriteriaResourceWithStreamingResponse(self._custom_searches.user_criteria)
