# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ..types import protocol_parsing_upload_params, protocol_parsing_get_statuses_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven, FileTypes
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
from ..types.protocol_read import ProtocolRead
from ..types.protocol_parsing_get_statuses_response import ProtocolParsingGetStatusesResponse

__all__ = ["ProtocolParsingResource", "AsyncProtocolParsingResource"]


class ProtocolParsingResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ProtocolParsingResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return ProtocolParsingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProtocolParsingResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return ProtocolParsingResourceWithStreamingResponse(self)

    def get_statuses(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolParsingGetStatusesResponse:
        """
        Get Protocol Parsing Statuses

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/protocol-parsing",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                    },
                    protocol_parsing_get_statuses_params.ProtocolParsingGetStatusesParams,
                ),
            ),
            cast_to=ProtocolParsingGetStatusesResponse,
        )

    def upload(
        self,
        *,
        file: FileTypes,
        title: str,
        site_ids: Iterable[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolRead:
        """
        Upload Protocol

        Args:
          file: The protocol file to upload

          title: The title of the protocol

          site_ids: The site IDs to associate with the protocol

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/protocol-parsing",
            body=maybe_transform(
                {
                    "file": file,
                    "title": title,
                    "site_ids": site_ids,
                },
                protocol_parsing_upload_params.ProtocolParsingUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolRead,
        )


class AsyncProtocolParsingResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncProtocolParsingResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncProtocolParsingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProtocolParsingResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncProtocolParsingResourceWithStreamingResponse(self)

    async def get_statuses(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolParsingGetStatusesResponse:
        """
        Get Protocol Parsing Statuses

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/protocol-parsing",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                    },
                    protocol_parsing_get_statuses_params.ProtocolParsingGetStatusesParams,
                ),
            ),
            cast_to=ProtocolParsingGetStatusesResponse,
        )

    async def upload(
        self,
        *,
        file: FileTypes,
        title: str,
        site_ids: Iterable[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolRead:
        """
        Upload Protocol

        Args:
          file: The protocol file to upload

          title: The title of the protocol

          site_ids: The site IDs to associate with the protocol

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/protocol-parsing",
            body=await async_maybe_transform(
                {
                    "file": file,
                    "title": title,
                    "site_ids": site_ids,
                },
                protocol_parsing_upload_params.ProtocolParsingUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolRead,
        )


class ProtocolParsingResourceWithRawResponse:
    def __init__(self, protocol_parsing: ProtocolParsingResource) -> None:
        self._protocol_parsing = protocol_parsing

        self.get_statuses = to_raw_response_wrapper(
            protocol_parsing.get_statuses,
        )
        self.upload = to_raw_response_wrapper(
            protocol_parsing.upload,
        )


class AsyncProtocolParsingResourceWithRawResponse:
    def __init__(self, protocol_parsing: AsyncProtocolParsingResource) -> None:
        self._protocol_parsing = protocol_parsing

        self.get_statuses = async_to_raw_response_wrapper(
            protocol_parsing.get_statuses,
        )
        self.upload = async_to_raw_response_wrapper(
            protocol_parsing.upload,
        )


class ProtocolParsingResourceWithStreamingResponse:
    def __init__(self, protocol_parsing: ProtocolParsingResource) -> None:
        self._protocol_parsing = protocol_parsing

        self.get_statuses = to_streamed_response_wrapper(
            protocol_parsing.get_statuses,
        )
        self.upload = to_streamed_response_wrapper(
            protocol_parsing.upload,
        )


class AsyncProtocolParsingResourceWithStreamingResponse:
    def __init__(self, protocol_parsing: AsyncProtocolParsingResource) -> None:
        self._protocol_parsing = protocol_parsing

        self.get_statuses = async_to_streamed_response_wrapper(
            protocol_parsing.get_statuses,
        )
        self.upload = async_to_streamed_response_wrapper(
            protocol_parsing.upload,
        )
