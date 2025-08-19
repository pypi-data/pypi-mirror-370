# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

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
from ...types.custom_searches import user_criterion_update_params, user_criterion_retrieve_params
from ...types.custom_searches.user_criterion_update_response import UserCriterionUpdateResponse
from ...types.custom_searches.user_criterion_retrieve_response import UserCriterionRetrieveResponse

__all__ = ["UserCriteriaResource", "AsyncUserCriteriaResource"]


class UserCriteriaResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UserCriteriaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return UserCriteriaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UserCriteriaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return UserCriteriaResourceWithStreamingResponse(self)

    def retrieve(
        self,
        custom_search_id: int,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        skip: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserCriterionRetrieveResponse:
        """
        Get Custom Search Criteria For User

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/custom-searches/{custom_search_id}/user-criteria",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "skip": skip,
                    },
                    user_criterion_retrieve_params.UserCriterionRetrieveParams,
                ),
            ),
            cast_to=UserCriterionRetrieveResponse,
        )

    def update(
        self,
        custom_search_id: int,
        *,
        active_criteria_ids: Iterable[int],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserCriterionUpdateResponse:
        """
        Update User Custom Search Criteria Filters

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._put(
            f"/custom-searches/{custom_search_id}/user-criteria",
            body=maybe_transform(
                {"active_criteria_ids": active_criteria_ids}, user_criterion_update_params.UserCriterionUpdateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserCriterionUpdateResponse,
        )


class AsyncUserCriteriaResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUserCriteriaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncUserCriteriaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUserCriteriaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncUserCriteriaResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        custom_search_id: int,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        skip: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserCriterionRetrieveResponse:
        """
        Get Custom Search Criteria For User

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/custom-searches/{custom_search_id}/user-criteria",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "skip": skip,
                    },
                    user_criterion_retrieve_params.UserCriterionRetrieveParams,
                ),
            ),
            cast_to=UserCriterionRetrieveResponse,
        )

    async def update(
        self,
        custom_search_id: int,
        *,
        active_criteria_ids: Iterable[int],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserCriterionUpdateResponse:
        """
        Update User Custom Search Criteria Filters

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._put(
            f"/custom-searches/{custom_search_id}/user-criteria",
            body=await async_maybe_transform(
                {"active_criteria_ids": active_criteria_ids}, user_criterion_update_params.UserCriterionUpdateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserCriterionUpdateResponse,
        )


class UserCriteriaResourceWithRawResponse:
    def __init__(self, user_criteria: UserCriteriaResource) -> None:
        self._user_criteria = user_criteria

        self.retrieve = to_raw_response_wrapper(
            user_criteria.retrieve,
        )
        self.update = to_raw_response_wrapper(
            user_criteria.update,
        )


class AsyncUserCriteriaResourceWithRawResponse:
    def __init__(self, user_criteria: AsyncUserCriteriaResource) -> None:
        self._user_criteria = user_criteria

        self.retrieve = async_to_raw_response_wrapper(
            user_criteria.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            user_criteria.update,
        )


class UserCriteriaResourceWithStreamingResponse:
    def __init__(self, user_criteria: UserCriteriaResource) -> None:
        self._user_criteria = user_criteria

        self.retrieve = to_streamed_response_wrapper(
            user_criteria.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            user_criteria.update,
        )


class AsyncUserCriteriaResourceWithStreamingResponse:
    def __init__(self, user_criteria: AsyncUserCriteriaResource) -> None:
        self._user_criteria = user_criteria

        self.retrieve = async_to_streamed_response_wrapper(
            user_criteria.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            user_criteria.update,
        )
