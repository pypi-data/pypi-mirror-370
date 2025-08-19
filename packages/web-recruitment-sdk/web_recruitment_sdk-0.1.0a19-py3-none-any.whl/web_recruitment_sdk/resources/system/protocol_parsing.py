# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional

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
from ...types.system import protocol_parsing_set_error_params, protocol_parsing_set_success_params
from ...types.custom_searches.criteria_create_param import CriteriaCreateParam

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

    def set_error(
        self,
        job_id: str,
        *,
        tenant_db_name: str,
        status_message: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Set Protocol Parsing Status Error

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return self._post(
            f"/system/{tenant_db_name}/protocol-parsing/{job_id}/error",
            body=maybe_transform(
                {"status_message": status_message}, protocol_parsing_set_error_params.ProtocolParsingSetErrorParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def set_success(
        self,
        job_id: str,
        *,
        tenant_db_name: str,
        criteria_create: Iterable[CriteriaCreateParam],
        external_protocol_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Update Protocol With Parsed Criteria And Set Success

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return self._post(
            f"/system/{tenant_db_name}/protocol-parsing/{job_id}/success",
            body=maybe_transform(
                {
                    "criteria_create": criteria_create,
                    "external_protocol_id": external_protocol_id,
                },
                protocol_parsing_set_success_params.ProtocolParsingSetSuccessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
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

    async def set_error(
        self,
        job_id: str,
        *,
        tenant_db_name: str,
        status_message: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Set Protocol Parsing Status Error

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return await self._post(
            f"/system/{tenant_db_name}/protocol-parsing/{job_id}/error",
            body=await async_maybe_transform(
                {"status_message": status_message}, protocol_parsing_set_error_params.ProtocolParsingSetErrorParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def set_success(
        self,
        job_id: str,
        *,
        tenant_db_name: str,
        criteria_create: Iterable[CriteriaCreateParam],
        external_protocol_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Update Protocol With Parsed Criteria And Set Success

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return await self._post(
            f"/system/{tenant_db_name}/protocol-parsing/{job_id}/success",
            body=await async_maybe_transform(
                {
                    "criteria_create": criteria_create,
                    "external_protocol_id": external_protocol_id,
                },
                protocol_parsing_set_success_params.ProtocolParsingSetSuccessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class ProtocolParsingResourceWithRawResponse:
    def __init__(self, protocol_parsing: ProtocolParsingResource) -> None:
        self._protocol_parsing = protocol_parsing

        self.set_error = to_raw_response_wrapper(
            protocol_parsing.set_error,
        )
        self.set_success = to_raw_response_wrapper(
            protocol_parsing.set_success,
        )


class AsyncProtocolParsingResourceWithRawResponse:
    def __init__(self, protocol_parsing: AsyncProtocolParsingResource) -> None:
        self._protocol_parsing = protocol_parsing

        self.set_error = async_to_raw_response_wrapper(
            protocol_parsing.set_error,
        )
        self.set_success = async_to_raw_response_wrapper(
            protocol_parsing.set_success,
        )


class ProtocolParsingResourceWithStreamingResponse:
    def __init__(self, protocol_parsing: ProtocolParsingResource) -> None:
        self._protocol_parsing = protocol_parsing

        self.set_error = to_streamed_response_wrapper(
            protocol_parsing.set_error,
        )
        self.set_success = to_streamed_response_wrapper(
            protocol_parsing.set_success,
        )


class AsyncProtocolParsingResourceWithStreamingResponse:
    def __init__(self, protocol_parsing: AsyncProtocolParsingResource) -> None:
        self._protocol_parsing = protocol_parsing

        self.set_error = async_to_streamed_response_wrapper(
            protocol_parsing.set_error,
        )
        self.set_success = async_to_streamed_response_wrapper(
            protocol_parsing.set_success,
        )
