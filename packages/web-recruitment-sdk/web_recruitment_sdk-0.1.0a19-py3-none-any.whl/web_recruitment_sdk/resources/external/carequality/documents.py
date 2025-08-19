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
from ....types.external.carequality import document_generate_upload_url_params
from ....types.external.carequality.document_generate_upload_url_response import DocumentGenerateUploadURLResponse

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

    def generate_upload_url(
        self,
        *,
        carequality_patient_id: str,
        content_type: str,
        file_md5_hash: str,
        file_name: str,
        file_size_bytes: int,
        x_api_key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentGenerateUploadURLResponse:
        """
        Generate a signed URL for uploading a CareQuality document.

        - Validates the encrypted patient ID
        - Checks file size limits (max 10MB)
        - Creates a document record with PENDING status
        - Returns a time-limited signed URL for upload

        Args:
          carequality_patient_id: The encrypted CareQuality patient ID (format: encrypted(tenant:patient_id))

          content_type: The content type of the file (e.g., application/xml, application/pdf)

          file_md5_hash: Base64-encoded MD5 hash of the file for integrity validation

          file_name: The name of the file to upload

          file_size_bytes: The size of the file in bytes

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"X-API-Key": x_api_key, **(extra_headers or {})}
        return self._post(
            "/external/carequality/documents/upload-url",
            body=maybe_transform(
                {
                    "carequality_patient_id": carequality_patient_id,
                    "content_type": content_type,
                    "file_md5_hash": file_md5_hash,
                    "file_name": file_name,
                    "file_size_bytes": file_size_bytes,
                },
                document_generate_upload_url_params.DocumentGenerateUploadURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentGenerateUploadURLResponse,
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

    async def generate_upload_url(
        self,
        *,
        carequality_patient_id: str,
        content_type: str,
        file_md5_hash: str,
        file_name: str,
        file_size_bytes: int,
        x_api_key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentGenerateUploadURLResponse:
        """
        Generate a signed URL for uploading a CareQuality document.

        - Validates the encrypted patient ID
        - Checks file size limits (max 10MB)
        - Creates a document record with PENDING status
        - Returns a time-limited signed URL for upload

        Args:
          carequality_patient_id: The encrypted CareQuality patient ID (format: encrypted(tenant:patient_id))

          content_type: The content type of the file (e.g., application/xml, application/pdf)

          file_md5_hash: Base64-encoded MD5 hash of the file for integrity validation

          file_name: The name of the file to upload

          file_size_bytes: The size of the file in bytes

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"X-API-Key": x_api_key, **(extra_headers or {})}
        return await self._post(
            "/external/carequality/documents/upload-url",
            body=await async_maybe_transform(
                {
                    "carequality_patient_id": carequality_patient_id,
                    "content_type": content_type,
                    "file_md5_hash": file_md5_hash,
                    "file_name": file_name,
                    "file_size_bytes": file_size_bytes,
                },
                document_generate_upload_url_params.DocumentGenerateUploadURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentGenerateUploadURLResponse,
        )


class DocumentsResourceWithRawResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.generate_upload_url = to_raw_response_wrapper(
            documents.generate_upload_url,
        )


class AsyncDocumentsResourceWithRawResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.generate_upload_url = async_to_raw_response_wrapper(
            documents.generate_upload_url,
        )


class DocumentsResourceWithStreamingResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.generate_upload_url = to_streamed_response_wrapper(
            documents.generate_upload_url,
        )


class AsyncDocumentsResourceWithStreamingResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.generate_upload_url = async_to_streamed_response_wrapper(
            documents.generate_upload_url,
        )
