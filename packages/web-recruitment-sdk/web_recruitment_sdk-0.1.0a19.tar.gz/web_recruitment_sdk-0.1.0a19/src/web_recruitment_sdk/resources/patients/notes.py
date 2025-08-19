# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
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
from ...types.patients import note_create_params
from ...types.patients.note_read import NoteRead
from ...types.patients.note_list_response import NoteListResponse

__all__ = ["NotesResource", "AsyncNotesResource"]


class NotesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> NotesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return NotesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> NotesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return NotesResourceWithStreamingResponse(self)

    def create(
        self,
        path_patient_id: int,
        *,
        note: str,
        body_patient_id: Optional[int] | NotGiven = NOT_GIVEN,
        user_id: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NoteRead:
        """
        Create Note

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            f"/patients/{path_patient_id}/notes",
            body=maybe_transform(
                {
                    "note": note,
                    "body_patient_id": body_patient_id,
                    "user_id": user_id,
                },
                note_create_params.NoteCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoteRead,
        )

    def list(
        self,
        patient_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NoteListResponse:
        """
        Get Patient Notes

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/patients/{patient_id}/notes",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoteListResponse,
        )

    def delete(
        self,
        note_id: int,
        *,
        patient_id: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete a note from a patient

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/patients/{patient_id}/notes/{note_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncNotesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncNotesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncNotesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncNotesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncNotesResourceWithStreamingResponse(self)

    async def create(
        self,
        path_patient_id: int,
        *,
        note: str,
        body_patient_id: Optional[int] | NotGiven = NOT_GIVEN,
        user_id: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NoteRead:
        """
        Create Note

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            f"/patients/{path_patient_id}/notes",
            body=await async_maybe_transform(
                {
                    "note": note,
                    "body_patient_id": body_patient_id,
                    "user_id": user_id,
                },
                note_create_params.NoteCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoteRead,
        )

    async def list(
        self,
        patient_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NoteListResponse:
        """
        Get Patient Notes

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/patients/{patient_id}/notes",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoteListResponse,
        )

    async def delete(
        self,
        note_id: int,
        *,
        patient_id: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete a note from a patient

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/patients/{patient_id}/notes/{note_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class NotesResourceWithRawResponse:
    def __init__(self, notes: NotesResource) -> None:
        self._notes = notes

        self.create = to_raw_response_wrapper(
            notes.create,
        )
        self.list = to_raw_response_wrapper(
            notes.list,
        )
        self.delete = to_raw_response_wrapper(
            notes.delete,
        )


class AsyncNotesResourceWithRawResponse:
    def __init__(self, notes: AsyncNotesResource) -> None:
        self._notes = notes

        self.create = async_to_raw_response_wrapper(
            notes.create,
        )
        self.list = async_to_raw_response_wrapper(
            notes.list,
        )
        self.delete = async_to_raw_response_wrapper(
            notes.delete,
        )


class NotesResourceWithStreamingResponse:
    def __init__(self, notes: NotesResource) -> None:
        self._notes = notes

        self.create = to_streamed_response_wrapper(
            notes.create,
        )
        self.list = to_streamed_response_wrapper(
            notes.list,
        )
        self.delete = to_streamed_response_wrapper(
            notes.delete,
        )


class AsyncNotesResourceWithStreamingResponse:
    def __init__(self, notes: AsyncNotesResource) -> None:
        self._notes = notes

        self.create = async_to_streamed_response_wrapper(
            notes.create,
        )
        self.list = async_to_streamed_response_wrapper(
            notes.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            notes.delete,
        )
