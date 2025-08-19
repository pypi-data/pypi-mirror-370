# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Optional, cast
from typing_extensions import Literal, overload

import httpx

from ....._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ....._utils import required_args, maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.outreach.campaigns.patients import action_create_params
from .....types.outreach.campaigns.patients.action_list_response import ActionListResponse
from .....types.outreach.campaigns.patients.action_create_response import ActionCreateResponse

__all__ = ["ActionsResource", "AsyncActionsResource"]


class ActionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ActionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return ActionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ActionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return ActionsResourceWithStreamingResponse(self)

    @overload
    def create(
        self,
        patient_id: str,
        *,
        campaign_id: int,
        caller_phone_number: str,
        duration_seconds: int,
        recipient_phone_number: str,
        status: Literal[
            "NO_ANSWER",
            "VOICEMAIL_LEFT",
            "WRONG_NUMBER",
            "HANGUP",
            "INTERESTED",
            "NOT_INTERESTED",
            "SCHEDULED",
            "DO_NOT_CALL",
        ],
        task_id: int,
        type: Literal["PHONE_CALL"],
        previous_action_id: Optional[int] | NotGiven = NOT_GIVEN,
        transcript_url: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionCreateResponse:
        """
        Create a new outreach action for a patient in a campaign

        Args:
          status: Status values specific to phone call actions

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        patient_id: str,
        *,
        campaign_id: int,
        message: str,
        recipient_phone_number: str,
        sender_phone_number: str,
        status: Literal[
            "SENT",
            "FAILED_TO_SEND",
            "REPLIED",
            "INTERESTED",
            "NOT_INTERESTED",
            "BOOKING_LINK_SENT",
            "SCHEDULED",
            "DO_NOT_CALL",
        ],
        task_id: int,
        type: Literal["SMS"],
        previous_action_id: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionCreateResponse:
        """
        Create a new outreach action for a patient in a campaign

        Args:
          status: Status values specific to SMS actions

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(
        [
            "campaign_id",
            "caller_phone_number",
            "duration_seconds",
            "recipient_phone_number",
            "status",
            "task_id",
            "type",
        ],
        ["campaign_id", "message", "recipient_phone_number", "sender_phone_number", "status", "task_id", "type"],
    )
    def create(
        self,
        patient_id: str,
        *,
        campaign_id: int,
        caller_phone_number: str | NotGiven = NOT_GIVEN,
        duration_seconds: int | NotGiven = NOT_GIVEN,
        recipient_phone_number: str,
        status: Literal[
            "NO_ANSWER",
            "VOICEMAIL_LEFT",
            "WRONG_NUMBER",
            "HANGUP",
            "INTERESTED",
            "NOT_INTERESTED",
            "SCHEDULED",
            "DO_NOT_CALL",
        ]
        | Literal[
            "SENT",
            "FAILED_TO_SEND",
            "REPLIED",
            "INTERESTED",
            "NOT_INTERESTED",
            "BOOKING_LINK_SENT",
            "SCHEDULED",
            "DO_NOT_CALL",
        ],
        task_id: int,
        type: Literal["PHONE_CALL"] | Literal["SMS"],
        previous_action_id: Optional[int] | NotGiven = NOT_GIVEN,
        transcript_url: Optional[str] | NotGiven = NOT_GIVEN,
        message: str | NotGiven = NOT_GIVEN,
        sender_phone_number: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionCreateResponse:
        if not patient_id:
            raise ValueError(f"Expected a non-empty value for `patient_id` but received {patient_id!r}")
        return cast(
            ActionCreateResponse,
            self._post(
                f"/outreach/campaigns/{campaign_id}/patients/{patient_id}/actions",
                body=maybe_transform(
                    {
                        "caller_phone_number": caller_phone_number,
                        "duration_seconds": duration_seconds,
                        "recipient_phone_number": recipient_phone_number,
                        "status": status,
                        "task_id": task_id,
                        "type": type,
                        "previous_action_id": previous_action_id,
                        "transcript_url": transcript_url,
                        "message": message,
                        "sender_phone_number": sender_phone_number,
                    },
                    action_create_params.ActionCreateParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionCreateResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def list(
        self,
        patient_id: str,
        *,
        campaign_id: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionListResponse:
        """
        Get all outreach actions for a patient in a campaign

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not patient_id:
            raise ValueError(f"Expected a non-empty value for `patient_id` but received {patient_id!r}")
        return self._get(
            f"/outreach/campaigns/{campaign_id}/patients/{patient_id}/actions",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionListResponse,
        )


class AsyncActionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncActionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncActionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncActionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncActionsResourceWithStreamingResponse(self)

    @overload
    async def create(
        self,
        patient_id: str,
        *,
        campaign_id: int,
        caller_phone_number: str,
        duration_seconds: int,
        recipient_phone_number: str,
        status: Literal[
            "NO_ANSWER",
            "VOICEMAIL_LEFT",
            "WRONG_NUMBER",
            "HANGUP",
            "INTERESTED",
            "NOT_INTERESTED",
            "SCHEDULED",
            "DO_NOT_CALL",
        ],
        task_id: int,
        type: Literal["PHONE_CALL"],
        previous_action_id: Optional[int] | NotGiven = NOT_GIVEN,
        transcript_url: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionCreateResponse:
        """
        Create a new outreach action for a patient in a campaign

        Args:
          status: Status values specific to phone call actions

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        patient_id: str,
        *,
        campaign_id: int,
        message: str,
        recipient_phone_number: str,
        sender_phone_number: str,
        status: Literal[
            "SENT",
            "FAILED_TO_SEND",
            "REPLIED",
            "INTERESTED",
            "NOT_INTERESTED",
            "BOOKING_LINK_SENT",
            "SCHEDULED",
            "DO_NOT_CALL",
        ],
        task_id: int,
        type: Literal["SMS"],
        previous_action_id: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionCreateResponse:
        """
        Create a new outreach action for a patient in a campaign

        Args:
          status: Status values specific to SMS actions

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(
        [
            "campaign_id",
            "caller_phone_number",
            "duration_seconds",
            "recipient_phone_number",
            "status",
            "task_id",
            "type",
        ],
        ["campaign_id", "message", "recipient_phone_number", "sender_phone_number", "status", "task_id", "type"],
    )
    async def create(
        self,
        patient_id: str,
        *,
        campaign_id: int,
        caller_phone_number: str | NotGiven = NOT_GIVEN,
        duration_seconds: int | NotGiven = NOT_GIVEN,
        recipient_phone_number: str,
        status: Literal[
            "NO_ANSWER",
            "VOICEMAIL_LEFT",
            "WRONG_NUMBER",
            "HANGUP",
            "INTERESTED",
            "NOT_INTERESTED",
            "SCHEDULED",
            "DO_NOT_CALL",
        ]
        | Literal[
            "SENT",
            "FAILED_TO_SEND",
            "REPLIED",
            "INTERESTED",
            "NOT_INTERESTED",
            "BOOKING_LINK_SENT",
            "SCHEDULED",
            "DO_NOT_CALL",
        ],
        task_id: int,
        type: Literal["PHONE_CALL"] | Literal["SMS"],
        previous_action_id: Optional[int] | NotGiven = NOT_GIVEN,
        transcript_url: Optional[str] | NotGiven = NOT_GIVEN,
        message: str | NotGiven = NOT_GIVEN,
        sender_phone_number: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionCreateResponse:
        if not patient_id:
            raise ValueError(f"Expected a non-empty value for `patient_id` but received {patient_id!r}")
        return cast(
            ActionCreateResponse,
            await self._post(
                f"/outreach/campaigns/{campaign_id}/patients/{patient_id}/actions",
                body=await async_maybe_transform(
                    {
                        "caller_phone_number": caller_phone_number,
                        "duration_seconds": duration_seconds,
                        "recipient_phone_number": recipient_phone_number,
                        "status": status,
                        "task_id": task_id,
                        "type": type,
                        "previous_action_id": previous_action_id,
                        "transcript_url": transcript_url,
                        "message": message,
                        "sender_phone_number": sender_phone_number,
                    },
                    action_create_params.ActionCreateParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionCreateResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def list(
        self,
        patient_id: str,
        *,
        campaign_id: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionListResponse:
        """
        Get all outreach actions for a patient in a campaign

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not patient_id:
            raise ValueError(f"Expected a non-empty value for `patient_id` but received {patient_id!r}")
        return await self._get(
            f"/outreach/campaigns/{campaign_id}/patients/{patient_id}/actions",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionListResponse,
        )


class ActionsResourceWithRawResponse:
    def __init__(self, actions: ActionsResource) -> None:
        self._actions = actions

        self.create = to_raw_response_wrapper(
            actions.create,
        )
        self.list = to_raw_response_wrapper(
            actions.list,
        )


class AsyncActionsResourceWithRawResponse:
    def __init__(self, actions: AsyncActionsResource) -> None:
        self._actions = actions

        self.create = async_to_raw_response_wrapper(
            actions.create,
        )
        self.list = async_to_raw_response_wrapper(
            actions.list,
        )


class ActionsResourceWithStreamingResponse:
    def __init__(self, actions: ActionsResource) -> None:
        self._actions = actions

        self.create = to_streamed_response_wrapper(
            actions.create,
        )
        self.list = to_streamed_response_wrapper(
            actions.list,
        )


class AsyncActionsResourceWithStreamingResponse:
    def __init__(self, actions: AsyncActionsResource) -> None:
        self._actions = actions

        self.create = async_to_streamed_response_wrapper(
            actions.create,
        )
        self.list = async_to_streamed_response_wrapper(
            actions.list,
        )
