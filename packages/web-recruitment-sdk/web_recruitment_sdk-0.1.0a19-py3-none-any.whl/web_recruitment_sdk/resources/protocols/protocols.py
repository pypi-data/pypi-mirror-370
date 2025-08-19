# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional

import httpx

from .sites import (
    SitesResource,
    AsyncSitesResource,
    SitesResourceWithRawResponse,
    AsyncSitesResourceWithRawResponse,
    SitesResourceWithStreamingResponse,
    AsyncSitesResourceWithStreamingResponse,
)
from ...types import (
    ProtocolStatus,
    protocol_update_params,
    protocol_get_funnel_params,
    protocol_get_matches_params,
    protocol_get_criteria_instances_params,
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
from ...types.protocol_read import ProtocolRead
from ...types.protocol_status import ProtocolStatus
from ...types.protocol_parsing_read import ProtocolParsingRead
from ...types.protocol_list_response import ProtocolListResponse
from ...types.protocol_get_matches_response import ProtocolGetMatchesResponse
from ...types.protocol_get_criteria_instances_response import ProtocolGetCriteriaInstancesResponse

__all__ = ["ProtocolsResource", "AsyncProtocolsResource"]


class ProtocolsResource(SyncAPIResource):
    @cached_property
    def sites(self) -> SitesResource:
        return SitesResource(self._client)

    @cached_property
    def criteria(self) -> CriteriaResource:
        return CriteriaResource(self._client)

    @cached_property
    def user_criteria(self) -> UserCriteriaResource:
        return UserCriteriaResource(self._client)

    @cached_property
    def with_raw_response(self) -> ProtocolsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return ProtocolsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProtocolsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return ProtocolsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        protocol_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolRead:
        """
        Get Protocol

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/protocols/{protocol_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolRead,
        )

    def update(
        self,
        protocol_id: int,
        *,
        external_protocol_id: Optional[str] | NotGiven = NOT_GIVEN,
        sites: Optional[Iterable[protocol_update_params.Site]] | NotGiven = NOT_GIVEN,
        status: ProtocolStatus | NotGiven = NOT_GIVEN,
        title: Optional[str] | NotGiven = NOT_GIVEN,
        version: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolRead:
        """
        Patch Protocol

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._patch(
            f"/protocols/{protocol_id}",
            body=maybe_transform(
                {
                    "external_protocol_id": external_protocol_id,
                    "sites": sites,
                    "status": status,
                    "title": title,
                    "version": version,
                },
                protocol_update_params.ProtocolUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolRead,
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
    ) -> ProtocolListResponse:
        """Get All Protocols"""
        return self._get(
            "/protocols",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolListResponse,
        )

    def delete(
        self,
        protocol_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete Protocol

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/protocols/{protocol_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get_criteria_instances(
        self,
        protocol_id: int,
        *,
        trially_patient_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolGetCriteriaInstancesResponse:
        """
        Get Criteria Instances

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/protocols/{protocol_id}/criteria_instances",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"trially_patient_id": trially_patient_id},
                    protocol_get_criteria_instances_params.ProtocolGetCriteriaInstancesParams,
                ),
            ),
            cast_to=ProtocolGetCriteriaInstancesResponse,
        )

    def get_funnel(
        self,
        protocol_id: int,
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
        Get Protocol Funnel

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/protocols/{protocol_id}/funnel",
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
                    protocol_get_funnel_params.ProtocolGetFunnelParams,
                ),
            ),
            cast_to=FunnelStats,
        )

    def get_matches(
        self,
        protocol_id: int,
        *,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolGetMatchesResponse:
        """
        Get Protocol Matches

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/protocols/{protocol_id}/matches",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"matching_criteria_ids": matching_criteria_ids},
                    protocol_get_matches_params.ProtocolGetMatchesParams,
                ),
            ),
            cast_to=ProtocolGetMatchesResponse,
        )

    def get_parsing_status(
        self,
        protocol_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolParsingRead:
        """
        Get Protocol Parsing Status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/protocols/{protocol_id}/protocol-parsing",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolParsingRead,
        )

    def set_ready(
        self,
        protocol_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolRead:
        """
        Set Protocol Ready

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            f"/protocols/{protocol_id}/ready",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolRead,
        )


class AsyncProtocolsResource(AsyncAPIResource):
    @cached_property
    def sites(self) -> AsyncSitesResource:
        return AsyncSitesResource(self._client)

    @cached_property
    def criteria(self) -> AsyncCriteriaResource:
        return AsyncCriteriaResource(self._client)

    @cached_property
    def user_criteria(self) -> AsyncUserCriteriaResource:
        return AsyncUserCriteriaResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncProtocolsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncProtocolsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProtocolsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncProtocolsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        protocol_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolRead:
        """
        Get Protocol

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/protocols/{protocol_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolRead,
        )

    async def update(
        self,
        protocol_id: int,
        *,
        external_protocol_id: Optional[str] | NotGiven = NOT_GIVEN,
        sites: Optional[Iterable[protocol_update_params.Site]] | NotGiven = NOT_GIVEN,
        status: ProtocolStatus | NotGiven = NOT_GIVEN,
        title: Optional[str] | NotGiven = NOT_GIVEN,
        version: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolRead:
        """
        Patch Protocol

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._patch(
            f"/protocols/{protocol_id}",
            body=await async_maybe_transform(
                {
                    "external_protocol_id": external_protocol_id,
                    "sites": sites,
                    "status": status,
                    "title": title,
                    "version": version,
                },
                protocol_update_params.ProtocolUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolRead,
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
    ) -> ProtocolListResponse:
        """Get All Protocols"""
        return await self._get(
            "/protocols",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolListResponse,
        )

    async def delete(
        self,
        protocol_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete Protocol

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/protocols/{protocol_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get_criteria_instances(
        self,
        protocol_id: int,
        *,
        trially_patient_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolGetCriteriaInstancesResponse:
        """
        Get Criteria Instances

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/protocols/{protocol_id}/criteria_instances",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"trially_patient_id": trially_patient_id},
                    protocol_get_criteria_instances_params.ProtocolGetCriteriaInstancesParams,
                ),
            ),
            cast_to=ProtocolGetCriteriaInstancesResponse,
        )

    async def get_funnel(
        self,
        protocol_id: int,
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
        Get Protocol Funnel

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/protocols/{protocol_id}/funnel",
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
                    protocol_get_funnel_params.ProtocolGetFunnelParams,
                ),
            ),
            cast_to=FunnelStats,
        )

    async def get_matches(
        self,
        protocol_id: int,
        *,
        matching_criteria_ids: Optional[Iterable[int]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolGetMatchesResponse:
        """
        Get Protocol Matches

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/protocols/{protocol_id}/matches",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"matching_criteria_ids": matching_criteria_ids},
                    protocol_get_matches_params.ProtocolGetMatchesParams,
                ),
            ),
            cast_to=ProtocolGetMatchesResponse,
        )

    async def get_parsing_status(
        self,
        protocol_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolParsingRead:
        """
        Get Protocol Parsing Status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/protocols/{protocol_id}/protocol-parsing",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolParsingRead,
        )

    async def set_ready(
        self,
        protocol_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolRead:
        """
        Set Protocol Ready

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            f"/protocols/{protocol_id}/ready",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolRead,
        )


class ProtocolsResourceWithRawResponse:
    def __init__(self, protocols: ProtocolsResource) -> None:
        self._protocols = protocols

        self.retrieve = to_raw_response_wrapper(
            protocols.retrieve,
        )
        self.update = to_raw_response_wrapper(
            protocols.update,
        )
        self.list = to_raw_response_wrapper(
            protocols.list,
        )
        self.delete = to_raw_response_wrapper(
            protocols.delete,
        )
        self.get_criteria_instances = to_raw_response_wrapper(
            protocols.get_criteria_instances,
        )
        self.get_funnel = to_raw_response_wrapper(
            protocols.get_funnel,
        )
        self.get_matches = to_raw_response_wrapper(
            protocols.get_matches,
        )
        self.get_parsing_status = to_raw_response_wrapper(
            protocols.get_parsing_status,
        )
        self.set_ready = to_raw_response_wrapper(
            protocols.set_ready,
        )

    @cached_property
    def sites(self) -> SitesResourceWithRawResponse:
        return SitesResourceWithRawResponse(self._protocols.sites)

    @cached_property
    def criteria(self) -> CriteriaResourceWithRawResponse:
        return CriteriaResourceWithRawResponse(self._protocols.criteria)

    @cached_property
    def user_criteria(self) -> UserCriteriaResourceWithRawResponse:
        return UserCriteriaResourceWithRawResponse(self._protocols.user_criteria)


class AsyncProtocolsResourceWithRawResponse:
    def __init__(self, protocols: AsyncProtocolsResource) -> None:
        self._protocols = protocols

        self.retrieve = async_to_raw_response_wrapper(
            protocols.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            protocols.update,
        )
        self.list = async_to_raw_response_wrapper(
            protocols.list,
        )
        self.delete = async_to_raw_response_wrapper(
            protocols.delete,
        )
        self.get_criteria_instances = async_to_raw_response_wrapper(
            protocols.get_criteria_instances,
        )
        self.get_funnel = async_to_raw_response_wrapper(
            protocols.get_funnel,
        )
        self.get_matches = async_to_raw_response_wrapper(
            protocols.get_matches,
        )
        self.get_parsing_status = async_to_raw_response_wrapper(
            protocols.get_parsing_status,
        )
        self.set_ready = async_to_raw_response_wrapper(
            protocols.set_ready,
        )

    @cached_property
    def sites(self) -> AsyncSitesResourceWithRawResponse:
        return AsyncSitesResourceWithRawResponse(self._protocols.sites)

    @cached_property
    def criteria(self) -> AsyncCriteriaResourceWithRawResponse:
        return AsyncCriteriaResourceWithRawResponse(self._protocols.criteria)

    @cached_property
    def user_criteria(self) -> AsyncUserCriteriaResourceWithRawResponse:
        return AsyncUserCriteriaResourceWithRawResponse(self._protocols.user_criteria)


class ProtocolsResourceWithStreamingResponse:
    def __init__(self, protocols: ProtocolsResource) -> None:
        self._protocols = protocols

        self.retrieve = to_streamed_response_wrapper(
            protocols.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            protocols.update,
        )
        self.list = to_streamed_response_wrapper(
            protocols.list,
        )
        self.delete = to_streamed_response_wrapper(
            protocols.delete,
        )
        self.get_criteria_instances = to_streamed_response_wrapper(
            protocols.get_criteria_instances,
        )
        self.get_funnel = to_streamed_response_wrapper(
            protocols.get_funnel,
        )
        self.get_matches = to_streamed_response_wrapper(
            protocols.get_matches,
        )
        self.get_parsing_status = to_streamed_response_wrapper(
            protocols.get_parsing_status,
        )
        self.set_ready = to_streamed_response_wrapper(
            protocols.set_ready,
        )

    @cached_property
    def sites(self) -> SitesResourceWithStreamingResponse:
        return SitesResourceWithStreamingResponse(self._protocols.sites)

    @cached_property
    def criteria(self) -> CriteriaResourceWithStreamingResponse:
        return CriteriaResourceWithStreamingResponse(self._protocols.criteria)

    @cached_property
    def user_criteria(self) -> UserCriteriaResourceWithStreamingResponse:
        return UserCriteriaResourceWithStreamingResponse(self._protocols.user_criteria)


class AsyncProtocolsResourceWithStreamingResponse:
    def __init__(self, protocols: AsyncProtocolsResource) -> None:
        self._protocols = protocols

        self.retrieve = async_to_streamed_response_wrapper(
            protocols.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            protocols.update,
        )
        self.list = async_to_streamed_response_wrapper(
            protocols.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            protocols.delete,
        )
        self.get_criteria_instances = async_to_streamed_response_wrapper(
            protocols.get_criteria_instances,
        )
        self.get_funnel = async_to_streamed_response_wrapper(
            protocols.get_funnel,
        )
        self.get_matches = async_to_streamed_response_wrapper(
            protocols.get_matches,
        )
        self.get_parsing_status = async_to_streamed_response_wrapper(
            protocols.get_parsing_status,
        )
        self.set_ready = async_to_streamed_response_wrapper(
            protocols.set_ready,
        )

    @cached_property
    def sites(self) -> AsyncSitesResourceWithStreamingResponse:
        return AsyncSitesResourceWithStreamingResponse(self._protocols.sites)

    @cached_property
    def criteria(self) -> AsyncCriteriaResourceWithStreamingResponse:
        return AsyncCriteriaResourceWithStreamingResponse(self._protocols.criteria)

    @cached_property
    def user_criteria(self) -> AsyncUserCriteriaResourceWithStreamingResponse:
        return AsyncUserCriteriaResourceWithStreamingResponse(self._protocols.user_criteria)
