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
from ....types.system.sites.trially_get_active_protocols_response import TriallyGetActiveProtocolsResponse
from ....types.system.sites.trially_get_active_custom_searches_response import TriallyGetActiveCustomSearchesResponse

__all__ = ["TriallyResource", "AsyncTriallyResource"]


class TriallyResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TriallyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return TriallyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TriallyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return TriallyResourceWithStreamingResponse(self)

    def get_active_custom_searches(
        self,
        trially_site_id: str,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TriallyGetActiveCustomSearchesResponse:
        """
        Get all active custom searches for a site with the given trially_site_id

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not trially_site_id:
            raise ValueError(f"Expected a non-empty value for `trially_site_id` but received {trially_site_id!r}")
        return self._get(
            f"/system/{tenant_db_name}/sites/trially/{trially_site_id}/custom-searches",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TriallyGetActiveCustomSearchesResponse,
        )

    def get_active_protocols(
        self,
        trially_site_id: str,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TriallyGetActiveProtocolsResponse:
        """
        Get all active protocols for a site with the given trially_site_id

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not trially_site_id:
            raise ValueError(f"Expected a non-empty value for `trially_site_id` but received {trially_site_id!r}")
        return self._get(
            f"/system/{tenant_db_name}/sites/trially/{trially_site_id}/protocols",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TriallyGetActiveProtocolsResponse,
        )


class AsyncTriallyResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTriallyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncTriallyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTriallyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncTriallyResourceWithStreamingResponse(self)

    async def get_active_custom_searches(
        self,
        trially_site_id: str,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TriallyGetActiveCustomSearchesResponse:
        """
        Get all active custom searches for a site with the given trially_site_id

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not trially_site_id:
            raise ValueError(f"Expected a non-empty value for `trially_site_id` but received {trially_site_id!r}")
        return await self._get(
            f"/system/{tenant_db_name}/sites/trially/{trially_site_id}/custom-searches",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TriallyGetActiveCustomSearchesResponse,
        )

    async def get_active_protocols(
        self,
        trially_site_id: str,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TriallyGetActiveProtocolsResponse:
        """
        Get all active protocols for a site with the given trially_site_id

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not trially_site_id:
            raise ValueError(f"Expected a non-empty value for `trially_site_id` but received {trially_site_id!r}")
        return await self._get(
            f"/system/{tenant_db_name}/sites/trially/{trially_site_id}/protocols",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TriallyGetActiveProtocolsResponse,
        )


class TriallyResourceWithRawResponse:
    def __init__(self, trially: TriallyResource) -> None:
        self._trially = trially

        self.get_active_custom_searches = to_raw_response_wrapper(
            trially.get_active_custom_searches,
        )
        self.get_active_protocols = to_raw_response_wrapper(
            trially.get_active_protocols,
        )


class AsyncTriallyResourceWithRawResponse:
    def __init__(self, trially: AsyncTriallyResource) -> None:
        self._trially = trially

        self.get_active_custom_searches = async_to_raw_response_wrapper(
            trially.get_active_custom_searches,
        )
        self.get_active_protocols = async_to_raw_response_wrapper(
            trially.get_active_protocols,
        )


class TriallyResourceWithStreamingResponse:
    def __init__(self, trially: TriallyResource) -> None:
        self._trially = trially

        self.get_active_custom_searches = to_streamed_response_wrapper(
            trially.get_active_custom_searches,
        )
        self.get_active_protocols = to_streamed_response_wrapper(
            trially.get_active_protocols,
        )


class AsyncTriallyResourceWithStreamingResponse:
    def __init__(self, trially: AsyncTriallyResource) -> None:
        self._trially = trially

        self.get_active_custom_searches = async_to_streamed_response_wrapper(
            trially.get_active_custom_searches,
        )
        self.get_active_protocols = async_to_streamed_response_wrapper(
            trially.get_active_protocols,
        )
