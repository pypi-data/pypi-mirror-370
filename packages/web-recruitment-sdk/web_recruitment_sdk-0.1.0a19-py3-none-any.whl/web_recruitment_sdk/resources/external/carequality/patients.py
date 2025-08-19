# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

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
from ....types.external.carequality import patient_search_params
from ....types.external.carequality.patient_search_response import PatientSearchResponse
from ....types.external.carequality.patient_retrieve_response import PatientRetrieveResponse

__all__ = ["PatientsResource", "AsyncPatientsResource"]


class PatientsResource(SyncAPIResource):
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
        carequality_patient_id: str,
        *,
        x_api_key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientRetrieveResponse:
        """
        Get a specific patient by CareQuality ID from CareQuality-enabled tenants.

        - Verify patient belongs to CareQuality-enabled tenant
        - Return patient details

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not carequality_patient_id:
            raise ValueError(
                f"Expected a non-empty value for `carequality_patient_id` but received {carequality_patient_id!r}"
            )
        extra_headers = {"X-API-Key": x_api_key, **(extra_headers or {})}
        return self._get(
            f"/external/carequality/patients/{carequality_patient_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientRetrieveResponse,
        )

    def search(
        self,
        *,
        date_of_birth: str,
        first_name: str,
        gender: Literal["female", "other", "unknown", "male"],
        last_name: str,
        x_api_key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientSearchResponse:
        """
        Search for patients across CareQuality-enabled tenants.

        - Get accounts with CareQuality enabled
        - Search patients based on criteria
        - Return aggregated results with encrypted patient IDs

        Args:
          date_of_birth: The date of birth of the patient in YYYY-MM-DD format

          first_name: The first name of the patient

          last_name: The last name of the patient

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"X-API-Key": x_api_key, **(extra_headers or {})}
        return self._post(
            "/external/carequality/patients/search",
            body=maybe_transform(
                {
                    "date_of_birth": date_of_birth,
                    "first_name": first_name,
                    "gender": gender,
                    "last_name": last_name,
                },
                patient_search_params.PatientSearchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientSearchResponse,
        )


class AsyncPatientsResource(AsyncAPIResource):
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
        carequality_patient_id: str,
        *,
        x_api_key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientRetrieveResponse:
        """
        Get a specific patient by CareQuality ID from CareQuality-enabled tenants.

        - Verify patient belongs to CareQuality-enabled tenant
        - Return patient details

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not carequality_patient_id:
            raise ValueError(
                f"Expected a non-empty value for `carequality_patient_id` but received {carequality_patient_id!r}"
            )
        extra_headers = {"X-API-Key": x_api_key, **(extra_headers or {})}
        return await self._get(
            f"/external/carequality/patients/{carequality_patient_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientRetrieveResponse,
        )

    async def search(
        self,
        *,
        date_of_birth: str,
        first_name: str,
        gender: Literal["female", "other", "unknown", "male"],
        last_name: str,
        x_api_key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientSearchResponse:
        """
        Search for patients across CareQuality-enabled tenants.

        - Get accounts with CareQuality enabled
        - Search patients based on criteria
        - Return aggregated results with encrypted patient IDs

        Args:
          date_of_birth: The date of birth of the patient in YYYY-MM-DD format

          first_name: The first name of the patient

          last_name: The last name of the patient

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"X-API-Key": x_api_key, **(extra_headers or {})}
        return await self._post(
            "/external/carequality/patients/search",
            body=await async_maybe_transform(
                {
                    "date_of_birth": date_of_birth,
                    "first_name": first_name,
                    "gender": gender,
                    "last_name": last_name,
                },
                patient_search_params.PatientSearchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientSearchResponse,
        )


class PatientsResourceWithRawResponse:
    def __init__(self, patients: PatientsResource) -> None:
        self._patients = patients

        self.retrieve = to_raw_response_wrapper(
            patients.retrieve,
        )
        self.search = to_raw_response_wrapper(
            patients.search,
        )


class AsyncPatientsResourceWithRawResponse:
    def __init__(self, patients: AsyncPatientsResource) -> None:
        self._patients = patients

        self.retrieve = async_to_raw_response_wrapper(
            patients.retrieve,
        )
        self.search = async_to_raw_response_wrapper(
            patients.search,
        )


class PatientsResourceWithStreamingResponse:
    def __init__(self, patients: PatientsResource) -> None:
        self._patients = patients

        self.retrieve = to_streamed_response_wrapper(
            patients.retrieve,
        )
        self.search = to_streamed_response_wrapper(
            patients.search,
        )


class AsyncPatientsResourceWithStreamingResponse:
    def __init__(self, patients: AsyncPatientsResource) -> None:
        self._patients = patients

        self.retrieve = async_to_streamed_response_wrapper(
            patients.retrieve,
        )
        self.search = async_to_streamed_response_wrapper(
            patients.search,
        )
