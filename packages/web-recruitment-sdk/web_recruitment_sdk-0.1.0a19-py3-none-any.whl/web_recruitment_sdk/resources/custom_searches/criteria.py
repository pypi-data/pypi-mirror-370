# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ...types import CriteriaType
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
from ...types.criteria_type import CriteriaType
from ...types.custom_searches import (
    CriteriaStatus,
    criterion_create_params,
    criterion_update_params,
    criterion_get_matching_progress_params,
)
from ...types.custom_searches.criteria_read import CriteriaRead
from ...types.custom_searches.criteria_status import CriteriaStatus
from ...types.custom_searches.criterion_retrieve_response import CriterionRetrieveResponse
from ...types.custom_searches.criterion_get_matching_progress_response import CriterionGetMatchingProgressResponse

__all__ = ["CriteriaResource", "AsyncCriteriaResource"]


class CriteriaResource(SyncAPIResource):
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

    def create(
        self,
        path_custom_search_id: int,
        *,
        summary: str,
        type: CriteriaType,
        body_custom_search_id: Optional[int] | NotGiven = NOT_GIVEN,
        description: Optional[str] | NotGiven = NOT_GIVEN,
        protocol_id: Optional[int] | NotGiven = NOT_GIVEN,
        status: CriteriaStatus | NotGiven = NOT_GIVEN,
        user_raw_input: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CriteriaRead:
        """
        Create Custom Search Criterion

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            f"/custom-searches/{path_custom_search_id}/criteria",
            body=maybe_transform(
                {
                    "summary": summary,
                    "type": type,
                    "body_custom_search_id": body_custom_search_id,
                    "description": description,
                    "protocol_id": protocol_id,
                    "status": status,
                    "user_raw_input": user_raw_input,
                },
                criterion_create_params.CriterionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CriteriaRead,
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
    ) -> CriterionRetrieveResponse:
        """
        Get Custom Search Criteria

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/custom-searches/{custom_search_id}/criteria",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CriterionRetrieveResponse,
        )

    def update(
        self,
        criterion_id: int,
        *,
        path_custom_search_id: int,
        summary: str,
        type: CriteriaType,
        body_custom_search_id: Optional[int] | NotGiven = NOT_GIVEN,
        description: Optional[str] | NotGiven = NOT_GIVEN,
        protocol_id: Optional[int] | NotGiven = NOT_GIVEN,
        status: CriteriaStatus | NotGiven = NOT_GIVEN,
        user_raw_input: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CriteriaRead:
        """
        Update Custom Search Criterion

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._put(
            f"/custom-searches/{path_custom_search_id}/criteria/{criterion_id}",
            body=maybe_transform(
                {
                    "summary": summary,
                    "type": type,
                    "body_custom_search_id": body_custom_search_id,
                    "description": description,
                    "protocol_id": protocol_id,
                    "status": status,
                    "user_raw_input": user_raw_input,
                },
                criterion_update_params.CriterionUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CriteriaRead,
        )

    def delete(
        self,
        criterion_id: int,
        *,
        custom_search_id: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete Custom Search Criterion

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/custom-searches/{custom_search_id}/criteria/{criterion_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get_matching_progress(
        self,
        custom_search_id: int,
        *,
        enable_sites_breakdown: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CriterionGetMatchingProgressResponse:
        """
        Get matching progress information for a custom search's criteria.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/custom-searches/{custom_search_id}/criteria/matching-progress",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"enable_sites_breakdown": enable_sites_breakdown},
                    criterion_get_matching_progress_params.CriterionGetMatchingProgressParams,
                ),
            ),
            cast_to=CriterionGetMatchingProgressResponse,
        )


class AsyncCriteriaResource(AsyncAPIResource):
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

    async def create(
        self,
        path_custom_search_id: int,
        *,
        summary: str,
        type: CriteriaType,
        body_custom_search_id: Optional[int] | NotGiven = NOT_GIVEN,
        description: Optional[str] | NotGiven = NOT_GIVEN,
        protocol_id: Optional[int] | NotGiven = NOT_GIVEN,
        status: CriteriaStatus | NotGiven = NOT_GIVEN,
        user_raw_input: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CriteriaRead:
        """
        Create Custom Search Criterion

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            f"/custom-searches/{path_custom_search_id}/criteria",
            body=await async_maybe_transform(
                {
                    "summary": summary,
                    "type": type,
                    "body_custom_search_id": body_custom_search_id,
                    "description": description,
                    "protocol_id": protocol_id,
                    "status": status,
                    "user_raw_input": user_raw_input,
                },
                criterion_create_params.CriterionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CriteriaRead,
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
    ) -> CriterionRetrieveResponse:
        """
        Get Custom Search Criteria

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/custom-searches/{custom_search_id}/criteria",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CriterionRetrieveResponse,
        )

    async def update(
        self,
        criterion_id: int,
        *,
        path_custom_search_id: int,
        summary: str,
        type: CriteriaType,
        body_custom_search_id: Optional[int] | NotGiven = NOT_GIVEN,
        description: Optional[str] | NotGiven = NOT_GIVEN,
        protocol_id: Optional[int] | NotGiven = NOT_GIVEN,
        status: CriteriaStatus | NotGiven = NOT_GIVEN,
        user_raw_input: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CriteriaRead:
        """
        Update Custom Search Criterion

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._put(
            f"/custom-searches/{path_custom_search_id}/criteria/{criterion_id}",
            body=await async_maybe_transform(
                {
                    "summary": summary,
                    "type": type,
                    "body_custom_search_id": body_custom_search_id,
                    "description": description,
                    "protocol_id": protocol_id,
                    "status": status,
                    "user_raw_input": user_raw_input,
                },
                criterion_update_params.CriterionUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CriteriaRead,
        )

    async def delete(
        self,
        criterion_id: int,
        *,
        custom_search_id: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete Custom Search Criterion

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/custom-searches/{custom_search_id}/criteria/{criterion_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get_matching_progress(
        self,
        custom_search_id: int,
        *,
        enable_sites_breakdown: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CriterionGetMatchingProgressResponse:
        """
        Get matching progress information for a custom search's criteria.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/custom-searches/{custom_search_id}/criteria/matching-progress",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"enable_sites_breakdown": enable_sites_breakdown},
                    criterion_get_matching_progress_params.CriterionGetMatchingProgressParams,
                ),
            ),
            cast_to=CriterionGetMatchingProgressResponse,
        )


class CriteriaResourceWithRawResponse:
    def __init__(self, criteria: CriteriaResource) -> None:
        self._criteria = criteria

        self.create = to_raw_response_wrapper(
            criteria.create,
        )
        self.retrieve = to_raw_response_wrapper(
            criteria.retrieve,
        )
        self.update = to_raw_response_wrapper(
            criteria.update,
        )
        self.delete = to_raw_response_wrapper(
            criteria.delete,
        )
        self.get_matching_progress = to_raw_response_wrapper(
            criteria.get_matching_progress,
        )


class AsyncCriteriaResourceWithRawResponse:
    def __init__(self, criteria: AsyncCriteriaResource) -> None:
        self._criteria = criteria

        self.create = async_to_raw_response_wrapper(
            criteria.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            criteria.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            criteria.update,
        )
        self.delete = async_to_raw_response_wrapper(
            criteria.delete,
        )
        self.get_matching_progress = async_to_raw_response_wrapper(
            criteria.get_matching_progress,
        )


class CriteriaResourceWithStreamingResponse:
    def __init__(self, criteria: CriteriaResource) -> None:
        self._criteria = criteria

        self.create = to_streamed_response_wrapper(
            criteria.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            criteria.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            criteria.update,
        )
        self.delete = to_streamed_response_wrapper(
            criteria.delete,
        )
        self.get_matching_progress = to_streamed_response_wrapper(
            criteria.get_matching_progress,
        )


class AsyncCriteriaResourceWithStreamingResponse:
    def __init__(self, criteria: AsyncCriteriaResource) -> None:
        self._criteria = criteria

        self.create = async_to_streamed_response_wrapper(
            criteria.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            criteria.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            criteria.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            criteria.delete,
        )
        self.get_matching_progress = async_to_streamed_response_wrapper(
            criteria.get_matching_progress,
        )
