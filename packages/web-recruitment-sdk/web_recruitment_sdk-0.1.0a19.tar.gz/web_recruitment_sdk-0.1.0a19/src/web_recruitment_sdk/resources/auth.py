# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable, Optional

import httpx

from ..types import auth_update_user_authorization_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.authorization import Authorization
from ..types.auth_list_roles_response import AuthListRolesResponse

__all__ = ["AuthResource", "AsyncAuthResource"]


class AuthResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AuthResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AuthResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AuthResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AuthResourceWithStreamingResponse(self)

    def list_roles(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AuthListRolesResponse:
        """Get the assignable roles for the current user."""
        return self._get(
            "/auth/roles",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuthListRolesResponse,
        )

    def update_user_authorization(
        self,
        user_id: int,
        *,
        role_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        site_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Authorization:
        """
        Update the authorization of a user.

        **Note:** Avoid using the results of this endpoint. **Inconsistent results** may
        be returned from the Authress API. Roles and sites may take a few moments to
        become visible due to eventual consistency.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._patch(
            f"/auth/users/{user_id}",
            body=maybe_transform(
                {
                    "role_ids": role_ids,
                    "site_ids": site_ids,
                },
                auth_update_user_authorization_params.AuthUpdateUserAuthorizationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Authorization,
        )


class AsyncAuthResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAuthResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncAuthResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAuthResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncAuthResourceWithStreamingResponse(self)

    async def list_roles(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AuthListRolesResponse:
        """Get the assignable roles for the current user."""
        return await self._get(
            "/auth/roles",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuthListRolesResponse,
        )

    async def update_user_authorization(
        self,
        user_id: int,
        *,
        role_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        site_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Authorization:
        """
        Update the authorization of a user.

        **Note:** Avoid using the results of this endpoint. **Inconsistent results** may
        be returned from the Authress API. Roles and sites may take a few moments to
        become visible due to eventual consistency.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._patch(
            f"/auth/users/{user_id}",
            body=await async_maybe_transform(
                {
                    "role_ids": role_ids,
                    "site_ids": site_ids,
                },
                auth_update_user_authorization_params.AuthUpdateUserAuthorizationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Authorization,
        )


class AuthResourceWithRawResponse:
    def __init__(self, auth: AuthResource) -> None:
        self._auth = auth

        self.list_roles = to_raw_response_wrapper(
            auth.list_roles,
        )
        self.update_user_authorization = to_raw_response_wrapper(
            auth.update_user_authorization,
        )


class AsyncAuthResourceWithRawResponse:
    def __init__(self, auth: AsyncAuthResource) -> None:
        self._auth = auth

        self.list_roles = async_to_raw_response_wrapper(
            auth.list_roles,
        )
        self.update_user_authorization = async_to_raw_response_wrapper(
            auth.update_user_authorization,
        )


class AuthResourceWithStreamingResponse:
    def __init__(self, auth: AuthResource) -> None:
        self._auth = auth

        self.list_roles = to_streamed_response_wrapper(
            auth.list_roles,
        )
        self.update_user_authorization = to_streamed_response_wrapper(
            auth.update_user_authorization,
        )


class AsyncAuthResourceWithStreamingResponse:
    def __init__(self, auth: AsyncAuthResource) -> None:
        self._auth = auth

        self.list_roles = async_to_streamed_response_wrapper(
            auth.list_roles,
        )
        self.update_user_authorization = async_to_streamed_response_wrapper(
            auth.update_user_authorization,
        )
