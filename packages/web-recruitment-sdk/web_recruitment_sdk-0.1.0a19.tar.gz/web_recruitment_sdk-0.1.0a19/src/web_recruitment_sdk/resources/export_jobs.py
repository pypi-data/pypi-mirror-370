# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ..types import export_job_create_params
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
from ..types.export_job_list_response import ExportJobListResponse
from ..types.export_job_create_response import ExportJobCreateResponse
from ..types.export_job_retrieve_patients_response import ExportJobRetrievePatientsResponse

__all__ = ["ExportJobsResource", "AsyncExportJobsResource"]


class ExportJobsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ExportJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return ExportJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ExportJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return ExportJobsResourceWithStreamingResponse(self)

    def create(
        self,
        site_id: int,
        *,
        client_id: str,
        ctms: str,
        ctms_site_id: str,
        patients: Iterable[export_job_create_params.Patient],
        referral_source_category_key: int,
        referral_source_key: int,
        study_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExportJobCreateResponse:
        """
        Start an export job to export given patients to a CTMS

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            f"/export-job/sites/{site_id}",
            body=maybe_transform(
                {
                    "client_id": client_id,
                    "ctms": ctms,
                    "ctms_site_id": ctms_site_id,
                    "patients": patients,
                    "referral_source_category_key": referral_source_category_key,
                    "referral_source_key": referral_source_key,
                    "study_id": study_id,
                },
                export_job_create_params.ExportJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExportJobCreateResponse,
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
    ) -> ExportJobListResponse:
        """Get all export jobs with their status for the current user."""
        return self._get(
            "/export-jobs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExportJobListResponse,
        )

    def retrieve_patients(
        self,
        export_job_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExportJobRetrievePatientsResponse:
        """
        Get detailed patient export statuses for a specific export job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/export-jobs/{export_job_id}/patients",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExportJobRetrievePatientsResponse,
        )


class AsyncExportJobsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncExportJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncExportJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncExportJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncExportJobsResourceWithStreamingResponse(self)

    async def create(
        self,
        site_id: int,
        *,
        client_id: str,
        ctms: str,
        ctms_site_id: str,
        patients: Iterable[export_job_create_params.Patient],
        referral_source_category_key: int,
        referral_source_key: int,
        study_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExportJobCreateResponse:
        """
        Start an export job to export given patients to a CTMS

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            f"/export-job/sites/{site_id}",
            body=await async_maybe_transform(
                {
                    "client_id": client_id,
                    "ctms": ctms,
                    "ctms_site_id": ctms_site_id,
                    "patients": patients,
                    "referral_source_category_key": referral_source_category_key,
                    "referral_source_key": referral_source_key,
                    "study_id": study_id,
                },
                export_job_create_params.ExportJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExportJobCreateResponse,
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
    ) -> ExportJobListResponse:
        """Get all export jobs with their status for the current user."""
        return await self._get(
            "/export-jobs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExportJobListResponse,
        )

    async def retrieve_patients(
        self,
        export_job_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExportJobRetrievePatientsResponse:
        """
        Get detailed patient export statuses for a specific export job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/export-jobs/{export_job_id}/patients",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExportJobRetrievePatientsResponse,
        )


class ExportJobsResourceWithRawResponse:
    def __init__(self, export_jobs: ExportJobsResource) -> None:
        self._export_jobs = export_jobs

        self.create = to_raw_response_wrapper(
            export_jobs.create,
        )
        self.list = to_raw_response_wrapper(
            export_jobs.list,
        )
        self.retrieve_patients = to_raw_response_wrapper(
            export_jobs.retrieve_patients,
        )


class AsyncExportJobsResourceWithRawResponse:
    def __init__(self, export_jobs: AsyncExportJobsResource) -> None:
        self._export_jobs = export_jobs

        self.create = async_to_raw_response_wrapper(
            export_jobs.create,
        )
        self.list = async_to_raw_response_wrapper(
            export_jobs.list,
        )
        self.retrieve_patients = async_to_raw_response_wrapper(
            export_jobs.retrieve_patients,
        )


class ExportJobsResourceWithStreamingResponse:
    def __init__(self, export_jobs: ExportJobsResource) -> None:
        self._export_jobs = export_jobs

        self.create = to_streamed_response_wrapper(
            export_jobs.create,
        )
        self.list = to_streamed_response_wrapper(
            export_jobs.list,
        )
        self.retrieve_patients = to_streamed_response_wrapper(
            export_jobs.retrieve_patients,
        )


class AsyncExportJobsResourceWithStreamingResponse:
    def __init__(self, export_jobs: AsyncExportJobsResource) -> None:
        self._export_jobs = export_jobs

        self.create = async_to_streamed_response_wrapper(
            export_jobs.create,
        )
        self.list = async_to_streamed_response_wrapper(
            export_jobs.list,
        )
        self.retrieve_patients = async_to_streamed_response_wrapper(
            export_jobs.retrieve_patients,
        )
