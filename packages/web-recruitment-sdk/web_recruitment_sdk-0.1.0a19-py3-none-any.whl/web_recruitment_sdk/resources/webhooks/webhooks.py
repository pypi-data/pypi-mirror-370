# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

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
from .carequality.carequality import (
    CarequalityResource,
    AsyncCarequalityResource,
    CarequalityResourceWithRawResponse,
    AsyncCarequalityResourceWithRawResponse,
    CarequalityResourceWithStreamingResponse,
    AsyncCarequalityResourceWithStreamingResponse,
)
from ...types.webhook_log_payload_response import WebhookLogPayloadResponse

__all__ = ["WebhooksResource", "AsyncWebhooksResource"]


class WebhooksResource(SyncAPIResource):
    @cached_property
    def carequality(self) -> CarequalityResource:
        return CarequalityResource(self._client)

    @cached_property
    def with_raw_response(self) -> WebhooksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return WebhooksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> WebhooksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return WebhooksResourceWithStreamingResponse(self)

    def log_payload(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WebhookLogPayloadResponse:
        """
        Log payloads coming from Eventarc

        This is a hacky way to send a payload to the webhook endpoint to validate what
        the payload looks like since we cannot send events from Eventarc to our local
        environment.

        Args: request: The FastAPI request object eventarc_token: Validated Eventarc
        bearer token

        Returns: 200: Valid payload

        Raises: 400: Invalid payload
        """
        return self._post(
            "/webhooks/log",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WebhookLogPayloadResponse,
        )


class AsyncWebhooksResource(AsyncAPIResource):
    @cached_property
    def carequality(self) -> AsyncCarequalityResource:
        return AsyncCarequalityResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncWebhooksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncWebhooksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncWebhooksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncWebhooksResourceWithStreamingResponse(self)

    async def log_payload(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WebhookLogPayloadResponse:
        """
        Log payloads coming from Eventarc

        This is a hacky way to send a payload to the webhook endpoint to validate what
        the payload looks like since we cannot send events from Eventarc to our local
        environment.

        Args: request: The FastAPI request object eventarc_token: Validated Eventarc
        bearer token

        Returns: 200: Valid payload

        Raises: 400: Invalid payload
        """
        return await self._post(
            "/webhooks/log",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WebhookLogPayloadResponse,
        )


class WebhooksResourceWithRawResponse:
    def __init__(self, webhooks: WebhooksResource) -> None:
        self._webhooks = webhooks

        self.log_payload = to_raw_response_wrapper(
            webhooks.log_payload,
        )

    @cached_property
    def carequality(self) -> CarequalityResourceWithRawResponse:
        return CarequalityResourceWithRawResponse(self._webhooks.carequality)


class AsyncWebhooksResourceWithRawResponse:
    def __init__(self, webhooks: AsyncWebhooksResource) -> None:
        self._webhooks = webhooks

        self.log_payload = async_to_raw_response_wrapper(
            webhooks.log_payload,
        )

    @cached_property
    def carequality(self) -> AsyncCarequalityResourceWithRawResponse:
        return AsyncCarequalityResourceWithRawResponse(self._webhooks.carequality)


class WebhooksResourceWithStreamingResponse:
    def __init__(self, webhooks: WebhooksResource) -> None:
        self._webhooks = webhooks

        self.log_payload = to_streamed_response_wrapper(
            webhooks.log_payload,
        )

    @cached_property
    def carequality(self) -> CarequalityResourceWithStreamingResponse:
        return CarequalityResourceWithStreamingResponse(self._webhooks.carequality)


class AsyncWebhooksResourceWithStreamingResponse:
    def __init__(self, webhooks: AsyncWebhooksResource) -> None:
        self._webhooks = webhooks

        self.log_payload = async_to_streamed_response_wrapper(
            webhooks.log_payload,
        )

    @cached_property
    def carequality(self) -> AsyncCarequalityResourceWithStreamingResponse:
        return AsyncCarequalityResourceWithStreamingResponse(self._webhooks.carequality)
