# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .users import (
    UsersResource,
    AsyncUsersResource,
    UsersResourceWithRawResponse,
    AsyncUsersResourceWithRawResponse,
    UsersResourceWithStreamingResponse,
    AsyncUsersResourceWithStreamingResponse,
)
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.admin_list_accounts_response import AdminListAccountsResponse

__all__ = ["AdminResource", "AsyncAdminResource"]


class AdminResource(SyncAPIResource):
    @cached_property
    def users(self) -> UsersResource:
        return UsersResource(self._client)

    @cached_property
    def with_raw_response(self) -> AdminResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AdminResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AdminResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AdminResourceWithStreamingResponse(self)

    def list_accounts(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AdminListAccountsResponse:
        """Get Accounts"""
        return self._get(
            "/admin/accounts",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AdminListAccountsResponse,
        )


class AsyncAdminResource(AsyncAPIResource):
    @cached_property
    def users(self) -> AsyncUsersResource:
        return AsyncUsersResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAdminResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncAdminResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAdminResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncAdminResourceWithStreamingResponse(self)

    async def list_accounts(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AdminListAccountsResponse:
        """Get Accounts"""
        return await self._get(
            "/admin/accounts",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AdminListAccountsResponse,
        )


class AdminResourceWithRawResponse:
    def __init__(self, admin: AdminResource) -> None:
        self._admin = admin

        self.list_accounts = to_raw_response_wrapper(
            admin.list_accounts,
        )

    @cached_property
    def users(self) -> UsersResourceWithRawResponse:
        return UsersResourceWithRawResponse(self._admin.users)


class AsyncAdminResourceWithRawResponse:
    def __init__(self, admin: AsyncAdminResource) -> None:
        self._admin = admin

        self.list_accounts = async_to_raw_response_wrapper(
            admin.list_accounts,
        )

    @cached_property
    def users(self) -> AsyncUsersResourceWithRawResponse:
        return AsyncUsersResourceWithRawResponse(self._admin.users)


class AdminResourceWithStreamingResponse:
    def __init__(self, admin: AdminResource) -> None:
        self._admin = admin

        self.list_accounts = to_streamed_response_wrapper(
            admin.list_accounts,
        )

    @cached_property
    def users(self) -> UsersResourceWithStreamingResponse:
        return UsersResourceWithStreamingResponse(self._admin.users)


class AsyncAdminResourceWithStreamingResponse:
    def __init__(self, admin: AsyncAdminResource) -> None:
        self._admin = admin

        self.list_accounts = async_to_streamed_response_wrapper(
            admin.list_accounts,
        )

    @cached_property
    def users(self) -> AsyncUsersResourceWithStreamingResponse:
        return AsyncUsersResourceWithStreamingResponse(self._admin.users)
