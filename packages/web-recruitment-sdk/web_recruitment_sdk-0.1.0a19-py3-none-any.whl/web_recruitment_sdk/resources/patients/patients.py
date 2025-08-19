# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .notes import (
    NotesResource,
    AsyncNotesResource,
    NotesResourceWithRawResponse,
    AsyncNotesResourceWithRawResponse,
    NotesResourceWithStreamingResponse,
    AsyncNotesResourceWithStreamingResponse,
)
from ...types import (
    patient_list_params,
    patient_update_params,
    patient_import_csv_params,
    patient_get_by_protocol_params,
)
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
from ...types.patient_read import PatientRead
from ...types.patient_list_response import PatientListResponse
from ...types.patient_import_csv_response import PatientImportCsvResponse
from ...types.patient_get_exports_response import PatientGetExportsResponse
from ...types.patient_get_by_protocol_response import PatientGetByProtocolResponse
from ...types.patient_get_protocol_matches_response import PatientGetProtocolMatchesResponse

__all__ = ["PatientsResource", "AsyncPatientsResource"]


class PatientsResource(SyncAPIResource):
    @cached_property
    def notes(self) -> NotesResource:
        return NotesResource(self._client)

    @cached_property
    def with_raw_response(self) -> PatientsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return PatientsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PatientsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return PatientsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        patient_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientRead:
        """
        Get Patient

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/patients/{patient_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientRead,
        )

    def update(
        self,
        patient_id: int,
        *,
        do_not_call: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientRead:
        """
        Patch Patient

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._patch(
            f"/patients/{patient_id}",
            body=maybe_transform({"do_not_call": do_not_call}, patient_update_params.PatientUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientRead,
        )

    def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientListResponse:
        """
        Get All Patients

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/patients",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"limit": limit}, patient_list_params.PatientListParams),
            ),
            cast_to=PatientListResponse,
        )

    def get_by_protocol(
        self,
        protocol_id: int,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientGetByProtocolResponse:
        """
        Get Patients By Protocol

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/patients/protocol/{protocol_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"limit": limit}, patient_get_by_protocol_params.PatientGetByProtocolParams),
            ),
            cast_to=PatientGetByProtocolResponse,
        )

    def get_exports(
        self,
        patient_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientGetExportsResponse:
        """
        Get all CTMS exports for a patient.

        Args: patient_id: The patient's trially_patient_id service: Patient export
        service

        Returns: List of CTMS export information for the patient

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not patient_id:
            raise ValueError(f"Expected a non-empty value for `patient_id` but received {patient_id!r}")
        return self._get(
            f"/patients/{patient_id}/exports",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientGetExportsResponse,
        )

    def get_protocol_matches(
        self,
        patient_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientGetProtocolMatchesResponse:
        """
        Get all protocols a patient has a match with.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/patients/{patient_id}/protocol-matches",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientGetProtocolMatchesResponse,
        )

    def import_csv(
        self,
        *,
        fallback_zip_code: str,
        site_id: int,
        storage_url: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientImportCsvResponse:
        """
        Import patients from CSV file stored in GCS.

        CSV Columns Expected:

        - LAST NAME, FIRST NAME, MIDDLE, DOB, PHONE1, SMS PHONE1 OK, PHONE2, SMS PHONE2
          OK, EMAIL, ZIP

        Authorization: User must have patient creation permissions for the site.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/patients/import-csv",
            body=maybe_transform(
                {
                    "fallback_zip_code": fallback_zip_code,
                    "site_id": site_id,
                    "storage_url": storage_url,
                },
                patient_import_csv_params.PatientImportCsvParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientImportCsvResponse,
        )


class AsyncPatientsResource(AsyncAPIResource):
    @cached_property
    def notes(self) -> AsyncNotesResource:
        return AsyncNotesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncPatientsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncPatientsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPatientsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncPatientsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        patient_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientRead:
        """
        Get Patient

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/patients/{patient_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientRead,
        )

    async def update(
        self,
        patient_id: int,
        *,
        do_not_call: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientRead:
        """
        Patch Patient

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._patch(
            f"/patients/{patient_id}",
            body=await async_maybe_transform({"do_not_call": do_not_call}, patient_update_params.PatientUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientRead,
        )

    async def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientListResponse:
        """
        Get All Patients

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/patients",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"limit": limit}, patient_list_params.PatientListParams),
            ),
            cast_to=PatientListResponse,
        )

    async def get_by_protocol(
        self,
        protocol_id: int,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientGetByProtocolResponse:
        """
        Get Patients By Protocol

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/patients/protocol/{protocol_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"limit": limit}, patient_get_by_protocol_params.PatientGetByProtocolParams
                ),
            ),
            cast_to=PatientGetByProtocolResponse,
        )

    async def get_exports(
        self,
        patient_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientGetExportsResponse:
        """
        Get all CTMS exports for a patient.

        Args: patient_id: The patient's trially_patient_id service: Patient export
        service

        Returns: List of CTMS export information for the patient

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not patient_id:
            raise ValueError(f"Expected a non-empty value for `patient_id` but received {patient_id!r}")
        return await self._get(
            f"/patients/{patient_id}/exports",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientGetExportsResponse,
        )

    async def get_protocol_matches(
        self,
        patient_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientGetProtocolMatchesResponse:
        """
        Get all protocols a patient has a match with.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/patients/{patient_id}/protocol-matches",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientGetProtocolMatchesResponse,
        )

    async def import_csv(
        self,
        *,
        fallback_zip_code: str,
        site_id: int,
        storage_url: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientImportCsvResponse:
        """
        Import patients from CSV file stored in GCS.

        CSV Columns Expected:

        - LAST NAME, FIRST NAME, MIDDLE, DOB, PHONE1, SMS PHONE1 OK, PHONE2, SMS PHONE2
          OK, EMAIL, ZIP

        Authorization: User must have patient creation permissions for the site.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/patients/import-csv",
            body=await async_maybe_transform(
                {
                    "fallback_zip_code": fallback_zip_code,
                    "site_id": site_id,
                    "storage_url": storage_url,
                },
                patient_import_csv_params.PatientImportCsvParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientImportCsvResponse,
        )


class PatientsResourceWithRawResponse:
    def __init__(self, patients: PatientsResource) -> None:
        self._patients = patients

        self.retrieve = to_raw_response_wrapper(
            patients.retrieve,
        )
        self.update = to_raw_response_wrapper(
            patients.update,
        )
        self.list = to_raw_response_wrapper(
            patients.list,
        )
        self.get_by_protocol = to_raw_response_wrapper(
            patients.get_by_protocol,
        )
        self.get_exports = to_raw_response_wrapper(
            patients.get_exports,
        )
        self.get_protocol_matches = to_raw_response_wrapper(
            patients.get_protocol_matches,
        )
        self.import_csv = to_raw_response_wrapper(
            patients.import_csv,
        )

    @cached_property
    def notes(self) -> NotesResourceWithRawResponse:
        return NotesResourceWithRawResponse(self._patients.notes)


class AsyncPatientsResourceWithRawResponse:
    def __init__(self, patients: AsyncPatientsResource) -> None:
        self._patients = patients

        self.retrieve = async_to_raw_response_wrapper(
            patients.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            patients.update,
        )
        self.list = async_to_raw_response_wrapper(
            patients.list,
        )
        self.get_by_protocol = async_to_raw_response_wrapper(
            patients.get_by_protocol,
        )
        self.get_exports = async_to_raw_response_wrapper(
            patients.get_exports,
        )
        self.get_protocol_matches = async_to_raw_response_wrapper(
            patients.get_protocol_matches,
        )
        self.import_csv = async_to_raw_response_wrapper(
            patients.import_csv,
        )

    @cached_property
    def notes(self) -> AsyncNotesResourceWithRawResponse:
        return AsyncNotesResourceWithRawResponse(self._patients.notes)


class PatientsResourceWithStreamingResponse:
    def __init__(self, patients: PatientsResource) -> None:
        self._patients = patients

        self.retrieve = to_streamed_response_wrapper(
            patients.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            patients.update,
        )
        self.list = to_streamed_response_wrapper(
            patients.list,
        )
        self.get_by_protocol = to_streamed_response_wrapper(
            patients.get_by_protocol,
        )
        self.get_exports = to_streamed_response_wrapper(
            patients.get_exports,
        )
        self.get_protocol_matches = to_streamed_response_wrapper(
            patients.get_protocol_matches,
        )
        self.import_csv = to_streamed_response_wrapper(
            patients.import_csv,
        )

    @cached_property
    def notes(self) -> NotesResourceWithStreamingResponse:
        return NotesResourceWithStreamingResponse(self._patients.notes)


class AsyncPatientsResourceWithStreamingResponse:
    def __init__(self, patients: AsyncPatientsResource) -> None:
        self._patients = patients

        self.retrieve = async_to_streamed_response_wrapper(
            patients.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            patients.update,
        )
        self.list = async_to_streamed_response_wrapper(
            patients.list,
        )
        self.get_by_protocol = async_to_streamed_response_wrapper(
            patients.get_by_protocol,
        )
        self.get_exports = async_to_streamed_response_wrapper(
            patients.get_exports,
        )
        self.get_protocol_matches = async_to_streamed_response_wrapper(
            patients.get_protocol_matches,
        )
        self.import_csv = async_to_streamed_response_wrapper(
            patients.import_csv,
        )

    @cached_property
    def notes(self) -> AsyncNotesResourceWithStreamingResponse:
        return AsyncNotesResourceWithStreamingResponse(self._patients.notes)
