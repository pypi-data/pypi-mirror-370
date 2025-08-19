# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from .trially import (
    TriallyResource,
    AsyncTriallyResource,
    TriallyResourceWithRawResponse,
    AsyncTriallyResourceWithRawResponse,
    TriallyResourceWithStreamingResponse,
    AsyncTriallyResourceWithStreamingResponse,
)
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
from ...._base_client import make_request_options
from ....types.system import site_create_params, site_update_params
from ....types.site_read import SiteRead
from ....types.system.site_list_response import SiteListResponse

__all__ = ["SitesResource", "AsyncSitesResource"]


class SitesResource(SyncAPIResource):
    @cached_property
    def trially(self) -> TriallyResource:
        return TriallyResource(self._client)

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

    def create(
        self,
        tenant_db_name: str,
        *,
        name: str,
        is_on_carequality: bool | NotGiven = NOT_GIVEN,
        trially_site_id: Optional[str] | NotGiven = NOT_GIVEN,
        zip_code: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SiteRead:
        """
        Create Site

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._post(
            f"/system/{tenant_db_name}/sites",
            body=maybe_transform(
                {
                    "name": name,
                    "is_on_carequality": is_on_carequality,
                    "trially_site_id": trially_site_id,
                    "zip_code": zip_code,
                },
                site_create_params.SiteCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SiteRead,
        )

    def retrieve(
        self,
        site_id: str,
        *,
        tenant_db_name: str,
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
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not site_id:
            raise ValueError(f"Expected a non-empty value for `site_id` but received {site_id!r}")
        return self._get(
            f"/system/{tenant_db_name}/sites/{site_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SiteRead,
        )

    def update(
        self,
        site_id: str,
        *,
        tenant_db_name: str,
        is_on_carequality: Optional[bool] | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        trially_site_id: Optional[str] | NotGiven = NOT_GIVEN,
        zip_code: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SiteRead:
        """
        Update a site for a tenant

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not site_id:
            raise ValueError(f"Expected a non-empty value for `site_id` but received {site_id!r}")
        return self._patch(
            f"/system/{tenant_db_name}/sites/{site_id}",
            body=maybe_transform(
                {
                    "is_on_carequality": is_on_carequality,
                    "name": name,
                    "trially_site_id": trially_site_id,
                    "zip_code": zip_code,
                },
                site_update_params.SiteUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SiteRead,
        )

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
    ) -> SiteListResponse:
        """
        Get all sites for a tenant

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._get(
            f"/system/{tenant_db_name}/sites",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SiteListResponse,
        )

    def delete(
        self,
        site_id: str,
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
        Delete Site

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not site_id:
            raise ValueError(f"Expected a non-empty value for `site_id` but received {site_id!r}")
        return self._delete(
            f"/system/{tenant_db_name}/sites/{site_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncSitesResource(AsyncAPIResource):
    @cached_property
    def trially(self) -> AsyncTriallyResource:
        return AsyncTriallyResource(self._client)

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

    async def create(
        self,
        tenant_db_name: str,
        *,
        name: str,
        is_on_carequality: bool | NotGiven = NOT_GIVEN,
        trially_site_id: Optional[str] | NotGiven = NOT_GIVEN,
        zip_code: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SiteRead:
        """
        Create Site

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._post(
            f"/system/{tenant_db_name}/sites",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "is_on_carequality": is_on_carequality,
                    "trially_site_id": trially_site_id,
                    "zip_code": zip_code,
                },
                site_create_params.SiteCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SiteRead,
        )

    async def retrieve(
        self,
        site_id: str,
        *,
        tenant_db_name: str,
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
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not site_id:
            raise ValueError(f"Expected a non-empty value for `site_id` but received {site_id!r}")
        return await self._get(
            f"/system/{tenant_db_name}/sites/{site_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SiteRead,
        )

    async def update(
        self,
        site_id: str,
        *,
        tenant_db_name: str,
        is_on_carequality: Optional[bool] | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        trially_site_id: Optional[str] | NotGiven = NOT_GIVEN,
        zip_code: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SiteRead:
        """
        Update a site for a tenant

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not site_id:
            raise ValueError(f"Expected a non-empty value for `site_id` but received {site_id!r}")
        return await self._patch(
            f"/system/{tenant_db_name}/sites/{site_id}",
            body=await async_maybe_transform(
                {
                    "is_on_carequality": is_on_carequality,
                    "name": name,
                    "trially_site_id": trially_site_id,
                    "zip_code": zip_code,
                },
                site_update_params.SiteUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SiteRead,
        )

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
    ) -> SiteListResponse:
        """
        Get all sites for a tenant

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._get(
            f"/system/{tenant_db_name}/sites",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SiteListResponse,
        )

    async def delete(
        self,
        site_id: str,
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
        Delete Site

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not site_id:
            raise ValueError(f"Expected a non-empty value for `site_id` but received {site_id!r}")
        return await self._delete(
            f"/system/{tenant_db_name}/sites/{site_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class SitesResourceWithRawResponse:
    def __init__(self, sites: SitesResource) -> None:
        self._sites = sites

        self.create = to_raw_response_wrapper(
            sites.create,
        )
        self.retrieve = to_raw_response_wrapper(
            sites.retrieve,
        )
        self.update = to_raw_response_wrapper(
            sites.update,
        )
        self.list = to_raw_response_wrapper(
            sites.list,
        )
        self.delete = to_raw_response_wrapper(
            sites.delete,
        )

    @cached_property
    def trially(self) -> TriallyResourceWithRawResponse:
        return TriallyResourceWithRawResponse(self._sites.trially)


class AsyncSitesResourceWithRawResponse:
    def __init__(self, sites: AsyncSitesResource) -> None:
        self._sites = sites

        self.create = async_to_raw_response_wrapper(
            sites.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            sites.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            sites.update,
        )
        self.list = async_to_raw_response_wrapper(
            sites.list,
        )
        self.delete = async_to_raw_response_wrapper(
            sites.delete,
        )

    @cached_property
    def trially(self) -> AsyncTriallyResourceWithRawResponse:
        return AsyncTriallyResourceWithRawResponse(self._sites.trially)


class SitesResourceWithStreamingResponse:
    def __init__(self, sites: SitesResource) -> None:
        self._sites = sites

        self.create = to_streamed_response_wrapper(
            sites.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            sites.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            sites.update,
        )
        self.list = to_streamed_response_wrapper(
            sites.list,
        )
        self.delete = to_streamed_response_wrapper(
            sites.delete,
        )

    @cached_property
    def trially(self) -> TriallyResourceWithStreamingResponse:
        return TriallyResourceWithStreamingResponse(self._sites.trially)


class AsyncSitesResourceWithStreamingResponse:
    def __init__(self, sites: AsyncSitesResource) -> None:
        self._sites = sites

        self.create = async_to_streamed_response_wrapper(
            sites.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            sites.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            sites.update,
        )
        self.list = async_to_streamed_response_wrapper(
            sites.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            sites.delete,
        )

    @cached_property
    def trially(self) -> AsyncTriallyResourceWithStreamingResponse:
        return AsyncTriallyResourceWithStreamingResponse(self._sites.trially)
