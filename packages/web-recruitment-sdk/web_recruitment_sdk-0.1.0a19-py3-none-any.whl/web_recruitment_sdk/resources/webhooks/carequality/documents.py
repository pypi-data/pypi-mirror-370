# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

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
from ....types.webhooks.carequality import document_confirm_upload_params

__all__ = ["DocumentsResource", "AsyncDocumentsResource"]


class DocumentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DocumentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return DocumentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DocumentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return DocumentsResourceWithStreamingResponse(self)

    def confirm_upload(
        self,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Confirm a CareQuality document upload completion.

        This endpoint is called by Eventarc when a file is uploaded to GCS. It validates
        the upload and enqueues the webhook for processing.

        Args: request: Upload confirmation details including MD5 hash and status
        eventarc_token: Validated Eventarc bearer token

        Returns: 202: Accepted and queued for processing

        Raises: 400: Invalid request, checksum mismatch, or validation error 404:
        Document not found 409: Document not in PENDING_UPLOAD status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/webhooks/carequality/documents/uploaded",
            body=maybe_transform(body, document_confirm_upload_params.DocumentConfirmUploadParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncDocumentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDocumentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncDocumentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDocumentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncDocumentsResourceWithStreamingResponse(self)

    async def confirm_upload(
        self,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Confirm a CareQuality document upload completion.

        This endpoint is called by Eventarc when a file is uploaded to GCS. It validates
        the upload and enqueues the webhook for processing.

        Args: request: Upload confirmation details including MD5 hash and status
        eventarc_token: Validated Eventarc bearer token

        Returns: 202: Accepted and queued for processing

        Raises: 400: Invalid request, checksum mismatch, or validation error 404:
        Document not found 409: Document not in PENDING_UPLOAD status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/webhooks/carequality/documents/uploaded",
            body=await async_maybe_transform(body, document_confirm_upload_params.DocumentConfirmUploadParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class DocumentsResourceWithRawResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.confirm_upload = to_raw_response_wrapper(
            documents.confirm_upload,
        )


class AsyncDocumentsResourceWithRawResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.confirm_upload = async_to_raw_response_wrapper(
            documents.confirm_upload,
        )


class DocumentsResourceWithStreamingResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.confirm_upload = to_streamed_response_wrapper(
            documents.confirm_upload,
        )


class AsyncDocumentsResourceWithStreamingResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.confirm_upload = async_to_streamed_response_wrapper(
            documents.confirm_upload,
        )
