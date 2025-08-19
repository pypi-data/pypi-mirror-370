# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.site_read import SiteRead
from ..types.site_list_response import SiteListResponse

__all__ = ["SitesResource", "AsyncSitesResource"]


class SitesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SitesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return SitesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SitesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return SitesResourceWithStreamingResponse(self)

    def retrieve(
        self,
        site_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SiteRead:
        """
        Get Site

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/sites/{site_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SiteRead,
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
    ) -> SiteListResponse:
        """Get Sites"""
        return self._get(
            "/sites",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SiteListResponse,
        )


class AsyncSitesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSitesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncSitesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSitesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncSitesResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        site_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SiteRead:
        """
        Get Site

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/sites/{site_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SiteRead,
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
    ) -> SiteListResponse:
        """Get Sites"""
        return await self._get(
            "/sites",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SiteListResponse,
        )


class SitesResourceWithRawResponse:
    def __init__(self, sites: SitesResource) -> None:
        self._sites = sites

        self.retrieve = to_raw_response_wrapper(
            sites.retrieve,
        )
        self.list = to_raw_response_wrapper(
            sites.list,
        )


class AsyncSitesResourceWithRawResponse:
    def __init__(self, sites: AsyncSitesResource) -> None:
        self._sites = sites

        self.retrieve = async_to_raw_response_wrapper(
            sites.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            sites.list,
        )


class SitesResourceWithStreamingResponse:
    def __init__(self, sites: SitesResource) -> None:
        self._sites = sites

        self.retrieve = to_streamed_response_wrapper(
            sites.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            sites.list,
        )


class AsyncSitesResourceWithStreamingResponse:
    def __init__(self, sites: AsyncSitesResource) -> None:
        self._sites = sites

        self.retrieve = async_to_streamed_response_wrapper(
            sites.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            sites.list,
        )
