# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

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
from ....types.system.patients import (
    bulk_update_entity_params,
    bulk_update_vitals_params,
    bulk_update_history_params,
    bulk_update_allergies_params,
    bulk_update_conditions_params,
    bulk_update_procedures_params,
    bulk_update_lab_results_params,
    bulk_update_medications_params,
    bulk_create_appointments_params,
    bulk_update_demographics_params,
    bulk_update_entity_search_params,
)
from ....types.system.patient_create_param import PatientCreateParam
from ....types.system.patients.bulk_insert_result import BulkInsertResult

__all__ = ["BulkResource", "AsyncBulkResource"]


class BulkResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BulkResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return BulkResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BulkResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return BulkResourceWithStreamingResponse(self)

    def create_appointments(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_create_appointments_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Create Appointments Bulk

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._put(
            f"/system/{tenant_db_name}/patients/bulk/appointments",
            body=maybe_transform(body, Iterable[bulk_create_appointments_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    def update_allergies(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_allergies_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update patient allergies

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._put(
            f"/system/{tenant_db_name}/patients/bulk/allergies",
            body=maybe_transform(body, Iterable[bulk_update_allergies_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    def update_conditions(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_conditions_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update patient conditions

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._put(
            f"/system/{tenant_db_name}/patients/bulk/conditions",
            body=maybe_transform(body, Iterable[bulk_update_conditions_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    def update_demographics(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_demographics_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update patient demographics

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._put(
            f"/system/{tenant_db_name}/patients/bulk/patient_demographics",
            body=maybe_transform(body, Iterable[bulk_update_demographics_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    def update_entity(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_entity_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update patient entity

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._put(
            f"/system/{tenant_db_name}/patients/bulk/patient_entity",
            body=maybe_transform(body, Iterable[bulk_update_entity_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    def update_entity_search(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_entity_search_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update entity search

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._put(
            f"/system/{tenant_db_name}/patients/bulk/entity_search",
            body=maybe_transform(body, Iterable[bulk_update_entity_search_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    def update_history(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_history_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update patient history

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._put(
            f"/system/{tenant_db_name}/patients/bulk/patient_history",
            body=maybe_transform(body, Iterable[bulk_update_history_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    def update_lab_results(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_lab_results_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update patient lab results

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._put(
            f"/system/{tenant_db_name}/patients/bulk/lab_results",
            body=maybe_transform(body, Iterable[bulk_update_lab_results_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    def update_medications(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_medications_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update patient medications

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._put(
            f"/system/{tenant_db_name}/patients/bulk/medications",
            body=maybe_transform(body, Iterable[bulk_update_medications_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    def update_procedures(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_procedures_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update patient procedures

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._put(
            f"/system/{tenant_db_name}/patients/bulk/procedures",
            body=maybe_transform(body, Iterable[bulk_update_procedures_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    def update_vitals(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_vitals_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update patient vitals

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._put(
            f"/system/{tenant_db_name}/patients/bulk/patient_vitals",
            body=maybe_transform(body, Iterable[bulk_update_vitals_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    def upsert(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[PatientCreateParam],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk Upsert Patient

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._put(
            f"/system/{tenant_db_name}/patients/bulk",
            body=maybe_transform(body, Iterable[PatientCreateParam]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )


class AsyncBulkResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBulkResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncBulkResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBulkResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncBulkResourceWithStreamingResponse(self)

    async def create_appointments(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_create_appointments_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Create Appointments Bulk

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._put(
            f"/system/{tenant_db_name}/patients/bulk/appointments",
            body=await async_maybe_transform(body, Iterable[bulk_create_appointments_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    async def update_allergies(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_allergies_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update patient allergies

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._put(
            f"/system/{tenant_db_name}/patients/bulk/allergies",
            body=await async_maybe_transform(body, Iterable[bulk_update_allergies_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    async def update_conditions(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_conditions_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update patient conditions

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._put(
            f"/system/{tenant_db_name}/patients/bulk/conditions",
            body=await async_maybe_transform(body, Iterable[bulk_update_conditions_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    async def update_demographics(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_demographics_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update patient demographics

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._put(
            f"/system/{tenant_db_name}/patients/bulk/patient_demographics",
            body=await async_maybe_transform(body, Iterable[bulk_update_demographics_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    async def update_entity(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_entity_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update patient entity

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._put(
            f"/system/{tenant_db_name}/patients/bulk/patient_entity",
            body=await async_maybe_transform(body, Iterable[bulk_update_entity_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    async def update_entity_search(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_entity_search_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update entity search

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._put(
            f"/system/{tenant_db_name}/patients/bulk/entity_search",
            body=await async_maybe_transform(body, Iterable[bulk_update_entity_search_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    async def update_history(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_history_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update patient history

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._put(
            f"/system/{tenant_db_name}/patients/bulk/patient_history",
            body=await async_maybe_transform(body, Iterable[bulk_update_history_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    async def update_lab_results(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_lab_results_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update patient lab results

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._put(
            f"/system/{tenant_db_name}/patients/bulk/lab_results",
            body=await async_maybe_transform(body, Iterable[bulk_update_lab_results_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    async def update_medications(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_medications_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update patient medications

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._put(
            f"/system/{tenant_db_name}/patients/bulk/medications",
            body=await async_maybe_transform(body, Iterable[bulk_update_medications_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    async def update_procedures(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_procedures_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update patient procedures

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._put(
            f"/system/{tenant_db_name}/patients/bulk/procedures",
            body=await async_maybe_transform(body, Iterable[bulk_update_procedures_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    async def update_vitals(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[bulk_update_vitals_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk update patient vitals

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._put(
            f"/system/{tenant_db_name}/patients/bulk/patient_vitals",
            body=await async_maybe_transform(body, Iterable[bulk_update_vitals_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )

    async def upsert(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[PatientCreateParam],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkInsertResult:
        """
        Bulk Upsert Patient

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._put(
            f"/system/{tenant_db_name}/patients/bulk",
            body=await async_maybe_transform(body, Iterable[PatientCreateParam]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkInsertResult,
        )


class BulkResourceWithRawResponse:
    def __init__(self, bulk: BulkResource) -> None:
        self._bulk = bulk

        self.create_appointments = to_raw_response_wrapper(
            bulk.create_appointments,
        )
        self.update_allergies = to_raw_response_wrapper(
            bulk.update_allergies,
        )
        self.update_conditions = to_raw_response_wrapper(
            bulk.update_conditions,
        )
        self.update_demographics = to_raw_response_wrapper(
            bulk.update_demographics,
        )
        self.update_entity = to_raw_response_wrapper(
            bulk.update_entity,
        )
        self.update_entity_search = to_raw_response_wrapper(
            bulk.update_entity_search,
        )
        self.update_history = to_raw_response_wrapper(
            bulk.update_history,
        )
        self.update_lab_results = to_raw_response_wrapper(
            bulk.update_lab_results,
        )
        self.update_medications = to_raw_response_wrapper(
            bulk.update_medications,
        )
        self.update_procedures = to_raw_response_wrapper(
            bulk.update_procedures,
        )
        self.update_vitals = to_raw_response_wrapper(
            bulk.update_vitals,
        )
        self.upsert = to_raw_response_wrapper(
            bulk.upsert,
        )


class AsyncBulkResourceWithRawResponse:
    def __init__(self, bulk: AsyncBulkResource) -> None:
        self._bulk = bulk

        self.create_appointments = async_to_raw_response_wrapper(
            bulk.create_appointments,
        )
        self.update_allergies = async_to_raw_response_wrapper(
            bulk.update_allergies,
        )
        self.update_conditions = async_to_raw_response_wrapper(
            bulk.update_conditions,
        )
        self.update_demographics = async_to_raw_response_wrapper(
            bulk.update_demographics,
        )
        self.update_entity = async_to_raw_response_wrapper(
            bulk.update_entity,
        )
        self.update_entity_search = async_to_raw_response_wrapper(
            bulk.update_entity_search,
        )
        self.update_history = async_to_raw_response_wrapper(
            bulk.update_history,
        )
        self.update_lab_results = async_to_raw_response_wrapper(
            bulk.update_lab_results,
        )
        self.update_medications = async_to_raw_response_wrapper(
            bulk.update_medications,
        )
        self.update_procedures = async_to_raw_response_wrapper(
            bulk.update_procedures,
        )
        self.update_vitals = async_to_raw_response_wrapper(
            bulk.update_vitals,
        )
        self.upsert = async_to_raw_response_wrapper(
            bulk.upsert,
        )


class BulkResourceWithStreamingResponse:
    def __init__(self, bulk: BulkResource) -> None:
        self._bulk = bulk

        self.create_appointments = to_streamed_response_wrapper(
            bulk.create_appointments,
        )
        self.update_allergies = to_streamed_response_wrapper(
            bulk.update_allergies,
        )
        self.update_conditions = to_streamed_response_wrapper(
            bulk.update_conditions,
        )
        self.update_demographics = to_streamed_response_wrapper(
            bulk.update_demographics,
        )
        self.update_entity = to_streamed_response_wrapper(
            bulk.update_entity,
        )
        self.update_entity_search = to_streamed_response_wrapper(
            bulk.update_entity_search,
        )
        self.update_history = to_streamed_response_wrapper(
            bulk.update_history,
        )
        self.update_lab_results = to_streamed_response_wrapper(
            bulk.update_lab_results,
        )
        self.update_medications = to_streamed_response_wrapper(
            bulk.update_medications,
        )
        self.update_procedures = to_streamed_response_wrapper(
            bulk.update_procedures,
        )
        self.update_vitals = to_streamed_response_wrapper(
            bulk.update_vitals,
        )
        self.upsert = to_streamed_response_wrapper(
            bulk.upsert,
        )


class AsyncBulkResourceWithStreamingResponse:
    def __init__(self, bulk: AsyncBulkResource) -> None:
        self._bulk = bulk

        self.create_appointments = async_to_streamed_response_wrapper(
            bulk.create_appointments,
        )
        self.update_allergies = async_to_streamed_response_wrapper(
            bulk.update_allergies,
        )
        self.update_conditions = async_to_streamed_response_wrapper(
            bulk.update_conditions,
        )
        self.update_demographics = async_to_streamed_response_wrapper(
            bulk.update_demographics,
        )
        self.update_entity = async_to_streamed_response_wrapper(
            bulk.update_entity,
        )
        self.update_entity_search = async_to_streamed_response_wrapper(
            bulk.update_entity_search,
        )
        self.update_history = async_to_streamed_response_wrapper(
            bulk.update_history,
        )
        self.update_lab_results = async_to_streamed_response_wrapper(
            bulk.update_lab_results,
        )
        self.update_medications = async_to_streamed_response_wrapper(
            bulk.update_medications,
        )
        self.update_procedures = async_to_streamed_response_wrapper(
            bulk.update_procedures,
        )
        self.update_vitals = async_to_streamed_response_wrapper(
            bulk.update_vitals,
        )
        self.upsert = async_to_streamed_response_wrapper(
            bulk.upsert,
        )
