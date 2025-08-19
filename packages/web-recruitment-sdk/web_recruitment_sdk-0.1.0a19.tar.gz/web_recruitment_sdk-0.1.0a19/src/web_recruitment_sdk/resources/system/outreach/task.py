# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal

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
from ....types.system.outreach import task_start_handler_params
from ....types.system.outreach.task_start_handler_response import TaskStartHandlerResponse

__all__ = ["TaskResource", "AsyncTaskResource"]


class TaskResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TaskResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return TaskResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TaskResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return TaskResourceWithStreamingResponse(self)

    def start_handler(
        self,
        tenant_db_name: str,
        *,
        action_type: Literal["PHONE_CALL", "SMS"],
        booking_url: str,
        outreach_task_id: int,
        patient_campaign_id: int,
        scheduled_date: Union[str, datetime],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TaskStartHandlerResponse:
        """Handle outreach task execution from cloud task queue.

        Dispatches phone calls via
        LiveKit.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._post(
            f"/system/{tenant_db_name}/outreach/task/start",
            body=maybe_transform(
                {
                    "action_type": action_type,
                    "booking_url": booking_url,
                    "outreach_task_id": outreach_task_id,
                    "patient_campaign_id": patient_campaign_id,
                    "scheduled_date": scheduled_date,
                },
                task_start_handler_params.TaskStartHandlerParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskStartHandlerResponse,
        )


class AsyncTaskResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTaskResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncTaskResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTaskResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncTaskResourceWithStreamingResponse(self)

    async def start_handler(
        self,
        tenant_db_name: str,
        *,
        action_type: Literal["PHONE_CALL", "SMS"],
        booking_url: str,
        outreach_task_id: int,
        patient_campaign_id: int,
        scheduled_date: Union[str, datetime],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TaskStartHandlerResponse:
        """Handle outreach task execution from cloud task queue.

        Dispatches phone calls via
        LiveKit.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._post(
            f"/system/{tenant_db_name}/outreach/task/start",
            body=await async_maybe_transform(
                {
                    "action_type": action_type,
                    "booking_url": booking_url,
                    "outreach_task_id": outreach_task_id,
                    "patient_campaign_id": patient_campaign_id,
                    "scheduled_date": scheduled_date,
                },
                task_start_handler_params.TaskStartHandlerParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskStartHandlerResponse,
        )


class TaskResourceWithRawResponse:
    def __init__(self, task: TaskResource) -> None:
        self._task = task

        self.start_handler = to_raw_response_wrapper(
            task.start_handler,
        )


class AsyncTaskResourceWithRawResponse:
    def __init__(self, task: AsyncTaskResource) -> None:
        self._task = task

        self.start_handler = async_to_raw_response_wrapper(
            task.start_handler,
        )


class TaskResourceWithStreamingResponse:
    def __init__(self, task: TaskResource) -> None:
        self._task = task

        self.start_handler = to_streamed_response_wrapper(
            task.start_handler,
        )


class AsyncTaskResourceWithStreamingResponse:
    def __init__(self, task: AsyncTaskResource) -> None:
        self._task = task

        self.start_handler = async_to_streamed_response_wrapper(
            task.start_handler,
        )
