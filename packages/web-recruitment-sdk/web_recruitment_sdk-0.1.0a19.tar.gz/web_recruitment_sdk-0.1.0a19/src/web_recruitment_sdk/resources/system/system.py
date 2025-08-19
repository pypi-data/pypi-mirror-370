# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable, Optional

import httpx

from .bulk import (
    BulkResource,
    AsyncBulkResource,
    BulkResourceWithRawResponse,
    AsyncBulkResourceWithRawResponse,
    BulkResourceWithStreamingResponse,
    AsyncBulkResourceWithStreamingResponse,
)
from .cache import (
    CacheResource,
    AsyncCacheResource,
    CacheResourceWithRawResponse,
    AsyncCacheResourceWithRawResponse,
    CacheResourceWithStreamingResponse,
    AsyncCacheResourceWithStreamingResponse,
)
from ...types import (
    ExportStatus,
    system_update_account_params,
    system_search_entities_params,
    system_patch_patient_export_params,
    system_get_patient_match_data_params,
    system_create_entity_search_index_params,
    system_bulk_search_patient_match_data_params,
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
from .sites.sites import (
    SitesResource,
    AsyncSitesResource,
    SitesResourceWithRawResponse,
    AsyncSitesResourceWithRawResponse,
    SitesResourceWithStreamingResponse,
    AsyncSitesResourceWithStreamingResponse,
)
from .appointments import (
    AppointmentsResource,
    AsyncAppointmentsResource,
    AppointmentsResourceWithRawResponse,
    AsyncAppointmentsResourceWithRawResponse,
    AppointmentsResourceWithStreamingResponse,
    AsyncAppointmentsResourceWithStreamingResponse,
)
from .matching_jobs import (
    MatchingJobsResource,
    AsyncMatchingJobsResource,
    MatchingJobsResourceWithRawResponse,
    AsyncMatchingJobsResourceWithRawResponse,
    MatchingJobsResourceWithStreamingResponse,
    AsyncMatchingJobsResourceWithStreamingResponse,
)
from ..._base_client import make_request_options
from .protocol_parsing import (
    ProtocolParsingResource,
    AsyncProtocolParsingResource,
    ProtocolParsingResourceWithRawResponse,
    AsyncProtocolParsingResourceWithRawResponse,
    ProtocolParsingResourceWithStreamingResponse,
    AsyncProtocolParsingResourceWithStreamingResponse,
)
from .criteria.criteria import (
    CriteriaResource,
    AsyncCriteriaResource,
    CriteriaResourceWithRawResponse,
    AsyncCriteriaResourceWithRawResponse,
    CriteriaResourceWithStreamingResponse,
    AsyncCriteriaResourceWithStreamingResponse,
)
from .outreach.outreach import (
    OutreachResource,
    AsyncOutreachResource,
    OutreachResourceWithRawResponse,
    AsyncOutreachResourceWithRawResponse,
    OutreachResourceWithStreamingResponse,
    AsyncOutreachResourceWithStreamingResponse,
)
from .patients.patients import (
    PatientsResource,
    AsyncPatientsResource,
    PatientsResourceWithRawResponse,
    AsyncPatientsResourceWithRawResponse,
    PatientsResourceWithStreamingResponse,
    AsyncPatientsResourceWithStreamingResponse,
)
from .protocols.protocols import (
    ProtocolsResource,
    AsyncProtocolsResource,
    ProtocolsResourceWithRawResponse,
    AsyncProtocolsResourceWithRawResponse,
    ProtocolsResourceWithStreamingResponse,
    AsyncProtocolsResourceWithStreamingResponse,
)
from ...types.export_status import ExportStatus
from .carequality.carequality import (
    CarequalityResource,
    AsyncCarequalityResource,
    CarequalityResourceWithRawResponse,
    AsyncCarequalityResourceWithRawResponse,
    CarequalityResourceWithStreamingResponse,
    AsyncCarequalityResourceWithStreamingResponse,
)
from .custom_searches.custom_searches import (
    CustomSearchesResource,
    AsyncCustomSearchesResource,
    CustomSearchesResourceWithRawResponse,
    AsyncCustomSearchesResourceWithRawResponse,
    CustomSearchesResourceWithStreamingResponse,
    AsyncCustomSearchesResourceWithStreamingResponse,
)
from ...types.criteria_instance_create_param import CriteriaInstanceCreateParam
from ...types.system_update_account_response import SystemUpdateAccountResponse
from ...types.system_search_entities_response import SystemSearchEntitiesResponse
from ...types.system_patch_patient_export_response import SystemPatchPatientExportResponse
from ...types.system_get_patient_match_data_response import SystemGetPatientMatchDataResponse
from ...types.system_create_criteria_instance_response import SystemCreateCriteriaInstanceResponse
from ...types.system_create_entity_search_index_response import SystemCreateEntitySearchIndexResponse

__all__ = ["SystemResource", "AsyncSystemResource"]


class SystemResource(SyncAPIResource):
    @cached_property
    def protocols(self) -> ProtocolsResource:
        return ProtocolsResource(self._client)

    @cached_property
    def criteria(self) -> CriteriaResource:
        return CriteriaResource(self._client)

    @cached_property
    def protocol_parsing(self) -> ProtocolParsingResource:
        return ProtocolParsingResource(self._client)

    @cached_property
    def sites(self) -> SitesResource:
        return SitesResource(self._client)

    @cached_property
    def patients(self) -> PatientsResource:
        return PatientsResource(self._client)

    @cached_property
    def appointments(self) -> AppointmentsResource:
        return AppointmentsResource(self._client)

    @cached_property
    def bulk(self) -> BulkResource:
        return BulkResource(self._client)

    @cached_property
    def matching_jobs(self) -> MatchingJobsResource:
        return MatchingJobsResource(self._client)

    @cached_property
    def cache(self) -> CacheResource:
        return CacheResource(self._client)

    @cached_property
    def custom_searches(self) -> CustomSearchesResource:
        return CustomSearchesResource(self._client)

    @cached_property
    def carequality(self) -> CarequalityResource:
        return CarequalityResource(self._client)

    @cached_property
    def outreach(self) -> OutreachResource:
        return OutreachResource(self._client)

    @cached_property
    def with_raw_response(self) -> SystemResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return SystemResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SystemResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return SystemResourceWithStreamingResponse(self)

    def bulk_search_patient_match_data(
        self,
        tenant_db_name: str,
        *,
        search_text: str,
        trially_patient_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Search for patient match data based on a list of patient IDs and a search text.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._post(
            f"/system/{tenant_db_name}/patient-match-data/bulk-search",
            body=maybe_transform(
                {
                    "search_text": search_text,
                    "trially_patient_ids": trially_patient_ids,
                },
                system_bulk_search_patient_match_data_params.SystemBulkSearchPatientMatchDataParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def create_criteria_instance(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[CriteriaInstanceCreateParam],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SystemCreateCriteriaInstanceResponse:
        """
        Create Criteria Instances

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._post(
            f"/system/{tenant_db_name}/criteria_instances",
            body=maybe_transform(body, Iterable[CriteriaInstanceCreateParam]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SystemCreateCriteriaInstanceResponse,
        )

    def create_entity_search_index(
        self,
        tenant_db_name: str,
        *,
        override_num_leaves: Optional[int] | NotGiven = NOT_GIVEN,
        recreate: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SystemCreateEntitySearchIndexResponse:
        """
        Create or recreate ScaNN index on entity_search.embedding with dynamic
        num_leaves.

        Args:
          override_num_leaves: Override computed num_leaves

          recreate: Drop and recreate the index

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._post(
            f"/system/{tenant_db_name}/entity-search/index",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "override_num_leaves": override_num_leaves,
                        "recreate": recreate,
                    },
                    system_create_entity_search_index_params.SystemCreateEntitySearchIndexParams,
                ),
            ),
            cast_to=SystemCreateEntitySearchIndexResponse,
        )

    def get_connection_pool_status(
        self,
        db_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Get Connection Pool Status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not db_name:
            raise ValueError(f"Expected a non-empty value for `db_name` but received {db_name!r}")
        return self._get(
            f"/system/{db_name}/connection-pool-status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )

    def get_patient_match_data(
        self,
        tenant_db_name: str,
        *,
        criteria_id: int,
        patient_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SystemGetPatientMatchDataResponse:
        """
        Get patient match data based on a list of patient IDs and a criteria ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._post(
            f"/system/{tenant_db_name}/patient-match-data",
            body=maybe_transform(
                {
                    "criteria_id": criteria_id,
                    "patient_ids": patient_ids,
                },
                system_get_patient_match_data_params.SystemGetPatientMatchDataParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SystemGetPatientMatchDataResponse,
        )

    def patch_patient_export(
        self,
        patient_ctms_export_id: int,
        *,
        tenant_db_name: str,
        status: ExportStatus,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SystemPatchPatientExportResponse:
        """
        Update a patient CTMS export's status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._patch(
            f"/system/{tenant_db_name}/patient-ctms-exports/{patient_ctms_export_id}",
            body=maybe_transform({"status": status}, system_patch_patient_export_params.SystemPatchPatientExportParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SystemPatchPatientExportResponse,
        )

    def ping(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Simple health check endpoint to verify the API is running"""
        return self._get(
            "/system/ping",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def search_entities(
        self,
        tenant_db_name: str,
        *,
        search_text: str,
        limit: int | NotGiven = NOT_GIVEN,
        similarity_threshold: Optional[float] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SystemSearchEntitiesResponse:
        """
        Search for entities similar to the provided search text.

        Args:
          search_text: Text to search for similar entities

          limit: Maximum number of results to return

          similarity_threshold: Minimum similarity score for returned entities

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._post(
            f"/system/{tenant_db_name}/entity-search",
            body=maybe_transform(
                {
                    "search_text": search_text,
                    "limit": limit,
                    "similarity_threshold": similarity_threshold,
                },
                system_search_entities_params.SystemSearchEntitiesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SystemSearchEntitiesResponse,
        )

    def update_account(
        self,
        tenant_db_name: str,
        *,
        has_carequality_sites: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SystemUpdateAccountResponse:
        """
        Update an account.

        Args: tenant_db_name: The tenant database name account_update: The account
        update object

        Returns: AccountRead: The updated account object

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return self._patch(
            f"/system/{tenant_db_name}/account",
            body=maybe_transform(
                {"has_carequality_sites": has_carequality_sites}, system_update_account_params.SystemUpdateAccountParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SystemUpdateAccountResponse,
        )


class AsyncSystemResource(AsyncAPIResource):
    @cached_property
    def protocols(self) -> AsyncProtocolsResource:
        return AsyncProtocolsResource(self._client)

    @cached_property
    def criteria(self) -> AsyncCriteriaResource:
        return AsyncCriteriaResource(self._client)

    @cached_property
    def protocol_parsing(self) -> AsyncProtocolParsingResource:
        return AsyncProtocolParsingResource(self._client)

    @cached_property
    def sites(self) -> AsyncSitesResource:
        return AsyncSitesResource(self._client)

    @cached_property
    def patients(self) -> AsyncPatientsResource:
        return AsyncPatientsResource(self._client)

    @cached_property
    def appointments(self) -> AsyncAppointmentsResource:
        return AsyncAppointmentsResource(self._client)

    @cached_property
    def bulk(self) -> AsyncBulkResource:
        return AsyncBulkResource(self._client)

    @cached_property
    def matching_jobs(self) -> AsyncMatchingJobsResource:
        return AsyncMatchingJobsResource(self._client)

    @cached_property
    def cache(self) -> AsyncCacheResource:
        return AsyncCacheResource(self._client)

    @cached_property
    def custom_searches(self) -> AsyncCustomSearchesResource:
        return AsyncCustomSearchesResource(self._client)

    @cached_property
    def carequality(self) -> AsyncCarequalityResource:
        return AsyncCarequalityResource(self._client)

    @cached_property
    def outreach(self) -> AsyncOutreachResource:
        return AsyncOutreachResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncSystemResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncSystemResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSystemResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncSystemResourceWithStreamingResponse(self)

    async def bulk_search_patient_match_data(
        self,
        tenant_db_name: str,
        *,
        search_text: str,
        trially_patient_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Search for patient match data based on a list of patient IDs and a search text.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._post(
            f"/system/{tenant_db_name}/patient-match-data/bulk-search",
            body=await async_maybe_transform(
                {
                    "search_text": search_text,
                    "trially_patient_ids": trially_patient_ids,
                },
                system_bulk_search_patient_match_data_params.SystemBulkSearchPatientMatchDataParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def create_criteria_instance(
        self,
        tenant_db_name: str,
        *,
        body: Iterable[CriteriaInstanceCreateParam],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SystemCreateCriteriaInstanceResponse:
        """
        Create Criteria Instances

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._post(
            f"/system/{tenant_db_name}/criteria_instances",
            body=await async_maybe_transform(body, Iterable[CriteriaInstanceCreateParam]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SystemCreateCriteriaInstanceResponse,
        )

    async def create_entity_search_index(
        self,
        tenant_db_name: str,
        *,
        override_num_leaves: Optional[int] | NotGiven = NOT_GIVEN,
        recreate: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SystemCreateEntitySearchIndexResponse:
        """
        Create or recreate ScaNN index on entity_search.embedding with dynamic
        num_leaves.

        Args:
          override_num_leaves: Override computed num_leaves

          recreate: Drop and recreate the index

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._post(
            f"/system/{tenant_db_name}/entity-search/index",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "override_num_leaves": override_num_leaves,
                        "recreate": recreate,
                    },
                    system_create_entity_search_index_params.SystemCreateEntitySearchIndexParams,
                ),
            ),
            cast_to=SystemCreateEntitySearchIndexResponse,
        )

    async def get_connection_pool_status(
        self,
        db_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Get Connection Pool Status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not db_name:
            raise ValueError(f"Expected a non-empty value for `db_name` but received {db_name!r}")
        return await self._get(
            f"/system/{db_name}/connection-pool-status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )

    async def get_patient_match_data(
        self,
        tenant_db_name: str,
        *,
        criteria_id: int,
        patient_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SystemGetPatientMatchDataResponse:
        """
        Get patient match data based on a list of patient IDs and a criteria ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._post(
            f"/system/{tenant_db_name}/patient-match-data",
            body=await async_maybe_transform(
                {
                    "criteria_id": criteria_id,
                    "patient_ids": patient_ids,
                },
                system_get_patient_match_data_params.SystemGetPatientMatchDataParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SystemGetPatientMatchDataResponse,
        )

    async def patch_patient_export(
        self,
        patient_ctms_export_id: int,
        *,
        tenant_db_name: str,
        status: ExportStatus,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SystemPatchPatientExportResponse:
        """
        Update a patient CTMS export's status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._patch(
            f"/system/{tenant_db_name}/patient-ctms-exports/{patient_ctms_export_id}",
            body=await async_maybe_transform(
                {"status": status}, system_patch_patient_export_params.SystemPatchPatientExportParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SystemPatchPatientExportResponse,
        )

    async def ping(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Simple health check endpoint to verify the API is running"""
        return await self._get(
            "/system/ping",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def search_entities(
        self,
        tenant_db_name: str,
        *,
        search_text: str,
        limit: int | NotGiven = NOT_GIVEN,
        similarity_threshold: Optional[float] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SystemSearchEntitiesResponse:
        """
        Search for entities similar to the provided search text.

        Args:
          search_text: Text to search for similar entities

          limit: Maximum number of results to return

          similarity_threshold: Minimum similarity score for returned entities

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._post(
            f"/system/{tenant_db_name}/entity-search",
            body=await async_maybe_transform(
                {
                    "search_text": search_text,
                    "limit": limit,
                    "similarity_threshold": similarity_threshold,
                },
                system_search_entities_params.SystemSearchEntitiesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SystemSearchEntitiesResponse,
        )

    async def update_account(
        self,
        tenant_db_name: str,
        *,
        has_carequality_sites: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SystemUpdateAccountResponse:
        """
        Update an account.

        Args: tenant_db_name: The tenant database name account_update: The account
        update object

        Returns: AccountRead: The updated account object

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_db_name:
            raise ValueError(f"Expected a non-empty value for `tenant_db_name` but received {tenant_db_name!r}")
        return await self._patch(
            f"/system/{tenant_db_name}/account",
            body=await async_maybe_transform(
                {"has_carequality_sites": has_carequality_sites}, system_update_account_params.SystemUpdateAccountParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SystemUpdateAccountResponse,
        )


class SystemResourceWithRawResponse:
    def __init__(self, system: SystemResource) -> None:
        self._system = system

        self.bulk_search_patient_match_data = to_raw_response_wrapper(
            system.bulk_search_patient_match_data,
        )
        self.create_criteria_instance = to_raw_response_wrapper(
            system.create_criteria_instance,
        )
        self.create_entity_search_index = to_raw_response_wrapper(
            system.create_entity_search_index,
        )
        self.get_connection_pool_status = to_raw_response_wrapper(
            system.get_connection_pool_status,
        )
        self.get_patient_match_data = to_raw_response_wrapper(
            system.get_patient_match_data,
        )
        self.patch_patient_export = to_raw_response_wrapper(
            system.patch_patient_export,
        )
        self.ping = to_raw_response_wrapper(
            system.ping,
        )
        self.search_entities = to_raw_response_wrapper(
            system.search_entities,
        )
        self.update_account = to_raw_response_wrapper(
            system.update_account,
        )

    @cached_property
    def protocols(self) -> ProtocolsResourceWithRawResponse:
        return ProtocolsResourceWithRawResponse(self._system.protocols)

    @cached_property
    def criteria(self) -> CriteriaResourceWithRawResponse:
        return CriteriaResourceWithRawResponse(self._system.criteria)

    @cached_property
    def protocol_parsing(self) -> ProtocolParsingResourceWithRawResponse:
        return ProtocolParsingResourceWithRawResponse(self._system.protocol_parsing)

    @cached_property
    def sites(self) -> SitesResourceWithRawResponse:
        return SitesResourceWithRawResponse(self._system.sites)

    @cached_property
    def patients(self) -> PatientsResourceWithRawResponse:
        return PatientsResourceWithRawResponse(self._system.patients)

    @cached_property
    def appointments(self) -> AppointmentsResourceWithRawResponse:
        return AppointmentsResourceWithRawResponse(self._system.appointments)

    @cached_property
    def bulk(self) -> BulkResourceWithRawResponse:
        return BulkResourceWithRawResponse(self._system.bulk)

    @cached_property
    def matching_jobs(self) -> MatchingJobsResourceWithRawResponse:
        return MatchingJobsResourceWithRawResponse(self._system.matching_jobs)

    @cached_property
    def cache(self) -> CacheResourceWithRawResponse:
        return CacheResourceWithRawResponse(self._system.cache)

    @cached_property
    def custom_searches(self) -> CustomSearchesResourceWithRawResponse:
        return CustomSearchesResourceWithRawResponse(self._system.custom_searches)

    @cached_property
    def carequality(self) -> CarequalityResourceWithRawResponse:
        return CarequalityResourceWithRawResponse(self._system.carequality)

    @cached_property
    def outreach(self) -> OutreachResourceWithRawResponse:
        return OutreachResourceWithRawResponse(self._system.outreach)


class AsyncSystemResourceWithRawResponse:
    def __init__(self, system: AsyncSystemResource) -> None:
        self._system = system

        self.bulk_search_patient_match_data = async_to_raw_response_wrapper(
            system.bulk_search_patient_match_data,
        )
        self.create_criteria_instance = async_to_raw_response_wrapper(
            system.create_criteria_instance,
        )
        self.create_entity_search_index = async_to_raw_response_wrapper(
            system.create_entity_search_index,
        )
        self.get_connection_pool_status = async_to_raw_response_wrapper(
            system.get_connection_pool_status,
        )
        self.get_patient_match_data = async_to_raw_response_wrapper(
            system.get_patient_match_data,
        )
        self.patch_patient_export = async_to_raw_response_wrapper(
            system.patch_patient_export,
        )
        self.ping = async_to_raw_response_wrapper(
            system.ping,
        )
        self.search_entities = async_to_raw_response_wrapper(
            system.search_entities,
        )
        self.update_account = async_to_raw_response_wrapper(
            system.update_account,
        )

    @cached_property
    def protocols(self) -> AsyncProtocolsResourceWithRawResponse:
        return AsyncProtocolsResourceWithRawResponse(self._system.protocols)

    @cached_property
    def criteria(self) -> AsyncCriteriaResourceWithRawResponse:
        return AsyncCriteriaResourceWithRawResponse(self._system.criteria)

    @cached_property
    def protocol_parsing(self) -> AsyncProtocolParsingResourceWithRawResponse:
        return AsyncProtocolParsingResourceWithRawResponse(self._system.protocol_parsing)

    @cached_property
    def sites(self) -> AsyncSitesResourceWithRawResponse:
        return AsyncSitesResourceWithRawResponse(self._system.sites)

    @cached_property
    def patients(self) -> AsyncPatientsResourceWithRawResponse:
        return AsyncPatientsResourceWithRawResponse(self._system.patients)

    @cached_property
    def appointments(self) -> AsyncAppointmentsResourceWithRawResponse:
        return AsyncAppointmentsResourceWithRawResponse(self._system.appointments)

    @cached_property
    def bulk(self) -> AsyncBulkResourceWithRawResponse:
        return AsyncBulkResourceWithRawResponse(self._system.bulk)

    @cached_property
    def matching_jobs(self) -> AsyncMatchingJobsResourceWithRawResponse:
        return AsyncMatchingJobsResourceWithRawResponse(self._system.matching_jobs)

    @cached_property
    def cache(self) -> AsyncCacheResourceWithRawResponse:
        return AsyncCacheResourceWithRawResponse(self._system.cache)

    @cached_property
    def custom_searches(self) -> AsyncCustomSearchesResourceWithRawResponse:
        return AsyncCustomSearchesResourceWithRawResponse(self._system.custom_searches)

    @cached_property
    def carequality(self) -> AsyncCarequalityResourceWithRawResponse:
        return AsyncCarequalityResourceWithRawResponse(self._system.carequality)

    @cached_property
    def outreach(self) -> AsyncOutreachResourceWithRawResponse:
        return AsyncOutreachResourceWithRawResponse(self._system.outreach)


class SystemResourceWithStreamingResponse:
    def __init__(self, system: SystemResource) -> None:
        self._system = system

        self.bulk_search_patient_match_data = to_streamed_response_wrapper(
            system.bulk_search_patient_match_data,
        )
        self.create_criteria_instance = to_streamed_response_wrapper(
            system.create_criteria_instance,
        )
        self.create_entity_search_index = to_streamed_response_wrapper(
            system.create_entity_search_index,
        )
        self.get_connection_pool_status = to_streamed_response_wrapper(
            system.get_connection_pool_status,
        )
        self.get_patient_match_data = to_streamed_response_wrapper(
            system.get_patient_match_data,
        )
        self.patch_patient_export = to_streamed_response_wrapper(
            system.patch_patient_export,
        )
        self.ping = to_streamed_response_wrapper(
            system.ping,
        )
        self.search_entities = to_streamed_response_wrapper(
            system.search_entities,
        )
        self.update_account = to_streamed_response_wrapper(
            system.update_account,
        )

    @cached_property
    def protocols(self) -> ProtocolsResourceWithStreamingResponse:
        return ProtocolsResourceWithStreamingResponse(self._system.protocols)

    @cached_property
    def criteria(self) -> CriteriaResourceWithStreamingResponse:
        return CriteriaResourceWithStreamingResponse(self._system.criteria)

    @cached_property
    def protocol_parsing(self) -> ProtocolParsingResourceWithStreamingResponse:
        return ProtocolParsingResourceWithStreamingResponse(self._system.protocol_parsing)

    @cached_property
    def sites(self) -> SitesResourceWithStreamingResponse:
        return SitesResourceWithStreamingResponse(self._system.sites)

    @cached_property
    def patients(self) -> PatientsResourceWithStreamingResponse:
        return PatientsResourceWithStreamingResponse(self._system.patients)

    @cached_property
    def appointments(self) -> AppointmentsResourceWithStreamingResponse:
        return AppointmentsResourceWithStreamingResponse(self._system.appointments)

    @cached_property
    def bulk(self) -> BulkResourceWithStreamingResponse:
        return BulkResourceWithStreamingResponse(self._system.bulk)

    @cached_property
    def matching_jobs(self) -> MatchingJobsResourceWithStreamingResponse:
        return MatchingJobsResourceWithStreamingResponse(self._system.matching_jobs)

    @cached_property
    def cache(self) -> CacheResourceWithStreamingResponse:
        return CacheResourceWithStreamingResponse(self._system.cache)

    @cached_property
    def custom_searches(self) -> CustomSearchesResourceWithStreamingResponse:
        return CustomSearchesResourceWithStreamingResponse(self._system.custom_searches)

    @cached_property
    def carequality(self) -> CarequalityResourceWithStreamingResponse:
        return CarequalityResourceWithStreamingResponse(self._system.carequality)

    @cached_property
    def outreach(self) -> OutreachResourceWithStreamingResponse:
        return OutreachResourceWithStreamingResponse(self._system.outreach)


class AsyncSystemResourceWithStreamingResponse:
    def __init__(self, system: AsyncSystemResource) -> None:
        self._system = system

        self.bulk_search_patient_match_data = async_to_streamed_response_wrapper(
            system.bulk_search_patient_match_data,
        )
        self.create_criteria_instance = async_to_streamed_response_wrapper(
            system.create_criteria_instance,
        )
        self.create_entity_search_index = async_to_streamed_response_wrapper(
            system.create_entity_search_index,
        )
        self.get_connection_pool_status = async_to_streamed_response_wrapper(
            system.get_connection_pool_status,
        )
        self.get_patient_match_data = async_to_streamed_response_wrapper(
            system.get_patient_match_data,
        )
        self.patch_patient_export = async_to_streamed_response_wrapper(
            system.patch_patient_export,
        )
        self.ping = async_to_streamed_response_wrapper(
            system.ping,
        )
        self.search_entities = async_to_streamed_response_wrapper(
            system.search_entities,
        )
        self.update_account = async_to_streamed_response_wrapper(
            system.update_account,
        )

    @cached_property
    def protocols(self) -> AsyncProtocolsResourceWithStreamingResponse:
        return AsyncProtocolsResourceWithStreamingResponse(self._system.protocols)

    @cached_property
    def criteria(self) -> AsyncCriteriaResourceWithStreamingResponse:
        return AsyncCriteriaResourceWithStreamingResponse(self._system.criteria)

    @cached_property
    def protocol_parsing(self) -> AsyncProtocolParsingResourceWithStreamingResponse:
        return AsyncProtocolParsingResourceWithStreamingResponse(self._system.protocol_parsing)

    @cached_property
    def sites(self) -> AsyncSitesResourceWithStreamingResponse:
        return AsyncSitesResourceWithStreamingResponse(self._system.sites)

    @cached_property
    def patients(self) -> AsyncPatientsResourceWithStreamingResponse:
        return AsyncPatientsResourceWithStreamingResponse(self._system.patients)

    @cached_property
    def appointments(self) -> AsyncAppointmentsResourceWithStreamingResponse:
        return AsyncAppointmentsResourceWithStreamingResponse(self._system.appointments)

    @cached_property
    def bulk(self) -> AsyncBulkResourceWithStreamingResponse:
        return AsyncBulkResourceWithStreamingResponse(self._system.bulk)

    @cached_property
    def matching_jobs(self) -> AsyncMatchingJobsResourceWithStreamingResponse:
        return AsyncMatchingJobsResourceWithStreamingResponse(self._system.matching_jobs)

    @cached_property
    def cache(self) -> AsyncCacheResourceWithStreamingResponse:
        return AsyncCacheResourceWithStreamingResponse(self._system.cache)

    @cached_property
    def custom_searches(self) -> AsyncCustomSearchesResourceWithStreamingResponse:
        return AsyncCustomSearchesResourceWithStreamingResponse(self._system.custom_searches)

    @cached_property
    def carequality(self) -> AsyncCarequalityResourceWithStreamingResponse:
        return AsyncCarequalityResourceWithStreamingResponse(self._system.carequality)

    @cached_property
    def outreach(self) -> AsyncOutreachResourceWithStreamingResponse:
        return AsyncOutreachResourceWithStreamingResponse(self._system.outreach)
