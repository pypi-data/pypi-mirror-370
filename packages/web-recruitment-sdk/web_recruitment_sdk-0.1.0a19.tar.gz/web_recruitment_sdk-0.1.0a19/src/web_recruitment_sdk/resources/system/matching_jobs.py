# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

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
from ...types.system import (
    matching_job_process_params,
    matching_job_error_task_params,
    matching_job_complete_task_params,
)
from ...types.system.matching_job_read import MatchingJobRead
from ...types.system.matching_task_read import MatchingTaskRead
from ...types.criteria_instance_create_param import CriteriaInstanceCreateParam

__all__ = ["MatchingJobsResource", "AsyncMatchingJobsResource"]


class MatchingJobsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MatchingJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return MatchingJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MatchingJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return MatchingJobsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        matching_job_id: int,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MatchingJobRead:
        """
        Get Matching Job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._get(
            f"/system/{tenant_db_name}/matching_jobs/{matching_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MatchingJobRead,
        )

    def cancel(
        self,
        matching_job_id: int,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MatchingJobRead:
        """
        Cancel a matching job and its pending tasks.

        This will:

        - Delete tasks from the queue
        - Mark tasks as CANCELLED in the database
        - Mark the job as CANCELLED

        If the job is already in a final state (SUCCESS, ERROR, CANCELLED), it will not
        be modified.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._post(
            f"/system/{tenant_db_name}/matching_jobs/{matching_job_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MatchingJobRead,
        )

    def complete_task(
        self,
        path_tenant_db_name: str,
        *,
        criteria_instances: Iterable[CriteriaInstanceCreateParam],
        task_id: int,
        task_name: str,
        body_tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MatchingTaskRead:
        """
        Complete a matching task

        Args:
          task_id: The ID of the task as it exists in the database

          task_name: The name of the task

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_tenant_db_name:
            raise ValueError(
                f"Expected a non-empty value for `path_tenant_db_name` but received {path_tenant_db_name!r}"
            )
        return self._post(
            f"/system/{path_tenant_db_name}/matching_jobs/complete_task",
            body=maybe_transform(
                {
                    "criteria_instances": criteria_instances,
                    "task_id": task_id,
                    "task_name": task_name,
                    "body_tenant_db_name": body_tenant_db_name,
                },
                matching_job_complete_task_params.MatchingJobCompleteTaskParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MatchingTaskRead,
        )

    def error_task(
        self,
        path_tenant_db_name: str,
        *,
        error_message: str,
        task_id: int,
        task_name: str,
        body_tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MatchingTaskRead:
        """
        Error a matching task

        Args:
          task_id: The ID of the task as it exists in the database

          task_name: The name of the task

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_tenant_db_name:
            raise ValueError(
                f"Expected a non-empty value for `path_tenant_db_name` but received {path_tenant_db_name!r}"
            )
        return self._post(
            f"/system/{path_tenant_db_name}/matching_jobs/error_task",
            body=maybe_transform(
                {
                    "error_message": error_message,
                    "task_id": task_id,
                    "task_name": task_name,
                    "body_tenant_db_name": body_tenant_db_name,
                },
                matching_job_error_task_params.MatchingJobErrorTaskParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MatchingTaskRead,
        )

    def process(
        self,
        path_tenant_db_name: str,
        *,
        job_id: int,
        task_name: str,
        body_tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MatchingJobRead:
        """
        Process a matching job that is in CREATED status.

        This endpoint is called by the job trigger queue to trigger patient processing
        for a job that was previously created.

        The job must be in CREATED status to be processed.

        Args:
          task_name: The name of the task

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_tenant_db_name:
            raise ValueError(
                f"Expected a non-empty value for `path_tenant_db_name` but received {path_tenant_db_name!r}"
            )
        return self._post(
            f"/system/{path_tenant_db_name}/matching_jobs/process",
            body=maybe_transform(
                {
                    "job_id": job_id,
                    "task_name": task_name,
                    "body_tenant_db_name": body_tenant_db_name,
                },
                matching_job_process_params.MatchingJobProcessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MatchingJobRead,
        )

    def start_all(
        self,
        tenant_db_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Create matching jobs for all protocols and custom searches of a tenant

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._post(
            f"/system/{tenant_db_name}/matching_jobs/start_all",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncMatchingJobsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMatchingJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncMatchingJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMatchingJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncMatchingJobsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        matching_job_id: int,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MatchingJobRead:
        """
        Get Matching Job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._get(
            f"/system/{tenant_db_name}/matching_jobs/{matching_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MatchingJobRead,
        )

    async def cancel(
        self,
        matching_job_id: int,
        *,
        tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MatchingJobRead:
        """
        Cancel a matching job and its pending tasks.

        This will:

        - Delete tasks from the queue
        - Mark tasks as CANCELLED in the database
        - Mark the job as CANCELLED

        If the job is already in a final state (SUCCESS, ERROR, CANCELLED), it will not
        be modified.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._post(
            f"/system/{tenant_db_name}/matching_jobs/{matching_job_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MatchingJobRead,
        )

    async def complete_task(
        self,
        path_tenant_db_name: str,
        *,
        criteria_instances: Iterable[CriteriaInstanceCreateParam],
        task_id: int,
        task_name: str,
        body_tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MatchingTaskRead:
        """
        Complete a matching task

        Args:
          task_id: The ID of the task as it exists in the database

          task_name: The name of the task

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_tenant_db_name:
            raise ValueError(
                f"Expected a non-empty value for `path_tenant_db_name` but received {path_tenant_db_name!r}"
            )
        return await self._post(
            f"/system/{path_tenant_db_name}/matching_jobs/complete_task",
            body=await async_maybe_transform(
                {
                    "criteria_instances": criteria_instances,
                    "task_id": task_id,
                    "task_name": task_name,
                    "body_tenant_db_name": body_tenant_db_name,
                },
                matching_job_complete_task_params.MatchingJobCompleteTaskParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MatchingTaskRead,
        )

    async def error_task(
        self,
        path_tenant_db_name: str,
        *,
        error_message: str,
        task_id: int,
        task_name: str,
        body_tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MatchingTaskRead:
        """
        Error a matching task

        Args:
          task_id: The ID of the task as it exists in the database

          task_name: The name of the task

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_tenant_db_name:
            raise ValueError(
                f"Expected a non-empty value for `path_tenant_db_name` but received {path_tenant_db_name!r}"
            )
        return await self._post(
            f"/system/{path_tenant_db_name}/matching_jobs/error_task",
            body=await async_maybe_transform(
                {
                    "error_message": error_message,
                    "task_id": task_id,
                    "task_name": task_name,
                    "body_tenant_db_name": body_tenant_db_name,
                },
                matching_job_error_task_params.MatchingJobErrorTaskParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MatchingTaskRead,
        )

    async def process(
        self,
        path_tenant_db_name: str,
        *,
        job_id: int,
        task_name: str,
        body_tenant_db_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MatchingJobRead:
        """
        Process a matching job that is in CREATED status.

        This endpoint is called by the job trigger queue to trigger patient processing
        for a job that was previously created.

        The job must be in CREATED status to be processed.

        Args:
          task_name: The name of the task

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_tenant_db_name:
            raise ValueError(
                f"Expected a non-empty value for `path_tenant_db_name` but received {path_tenant_db_name!r}"
            )
        return await self._post(
            f"/system/{path_tenant_db_name}/matching_jobs/process",
            body=await async_maybe_transform(
                {
                    "job_id": job_id,
                    "task_name": task_name,
                    "body_tenant_db_name": body_tenant_db_name,
                },
                matching_job_process_params.MatchingJobProcessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MatchingJobRead,
        )

    async def start_all(
        self,
        tenant_db_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Create matching jobs for all protocols and custom searches of a tenant

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._post(
            f"/system/{tenant_db_name}/matching_jobs/start_all",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class MatchingJobsResourceWithRawResponse:
    def __init__(self, matching_jobs: MatchingJobsResource) -> None:
        self._matching_jobs = matching_jobs

        self.retrieve = to_raw_response_wrapper(
            matching_jobs.retrieve,
        )
        self.cancel = to_raw_response_wrapper(
            matching_jobs.cancel,
        )
        self.complete_task = to_raw_response_wrapper(
            matching_jobs.complete_task,
        )
        self.error_task = to_raw_response_wrapper(
            matching_jobs.error_task,
        )
        self.process = to_raw_response_wrapper(
            matching_jobs.process,
        )
        self.start_all = to_raw_response_wrapper(
            matching_jobs.start_all,
        )


class AsyncMatchingJobsResourceWithRawResponse:
    def __init__(self, matching_jobs: AsyncMatchingJobsResource) -> None:
        self._matching_jobs = matching_jobs

        self.retrieve = async_to_raw_response_wrapper(
            matching_jobs.retrieve,
        )
        self.cancel = async_to_raw_response_wrapper(
            matching_jobs.cancel,
        )
        self.complete_task = async_to_raw_response_wrapper(
            matching_jobs.complete_task,
        )
        self.error_task = async_to_raw_response_wrapper(
            matching_jobs.error_task,
        )
        self.process = async_to_raw_response_wrapper(
            matching_jobs.process,
        )
        self.start_all = async_to_raw_response_wrapper(
            matching_jobs.start_all,
        )


class MatchingJobsResourceWithStreamingResponse:
    def __init__(self, matching_jobs: MatchingJobsResource) -> None:
        self._matching_jobs = matching_jobs

        self.retrieve = to_streamed_response_wrapper(
            matching_jobs.retrieve,
        )
        self.cancel = to_streamed_response_wrapper(
            matching_jobs.cancel,
        )
        self.complete_task = to_streamed_response_wrapper(
            matching_jobs.complete_task,
        )
        self.error_task = to_streamed_response_wrapper(
            matching_jobs.error_task,
        )
        self.process = to_streamed_response_wrapper(
            matching_jobs.process,
        )
        self.start_all = to_streamed_response_wrapper(
            matching_jobs.start_all,
        )


class AsyncMatchingJobsResourceWithStreamingResponse:
    def __init__(self, matching_jobs: AsyncMatchingJobsResource) -> None:
        self._matching_jobs = matching_jobs

        self.retrieve = async_to_streamed_response_wrapper(
            matching_jobs.retrieve,
        )
        self.cancel = async_to_streamed_response_wrapper(
            matching_jobs.cancel,
        )
        self.complete_task = async_to_streamed_response_wrapper(
            matching_jobs.complete_task,
        )
        self.error_task = async_to_streamed_response_wrapper(
            matching_jobs.error_task,
        )
        self.process = async_to_streamed_response_wrapper(
            matching_jobs.process,
        )
        self.start_all = async_to_streamed_response_wrapper(
            matching_jobs.start_all,
        )
