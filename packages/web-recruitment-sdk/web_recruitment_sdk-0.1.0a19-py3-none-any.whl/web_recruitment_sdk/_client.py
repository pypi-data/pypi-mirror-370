# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Dict, Union, Mapping, cast
from typing_extensions import Self, Literal, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from .resources import (
    auth,
    crio,
    sites,
    health,
    criteria,
    dashboards,
    export_jobs,
    appointments,
    feature_flags,
    matching_jobs,
    custom_criteria,
    protocol_parsing,
    patients_by_external_id,
)
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError, WebRecruitmentSDKError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from .resources.admin import admin
from .resources.system import system
from .resources.external import external
from .resources.outreach import outreach
from .resources.patients import patients
from .resources.webhooks import webhooks
from .resources.protocols import protocols
from .resources.custom_searches import custom_searches

__all__ = [
    "ENVIRONMENTS",
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "WebRecruitmentSDK",
    "AsyncWebRecruitmentSDK",
    "Client",
    "AsyncClient",
]

ENVIRONMENTS: Dict[str, str] = {
    "development": "http://localhost:8080",
    "production": "https://trially-backend-production-861990824910.us-central1.run.app",
    "staging": "https://trially-backend-staging-965051512294.us-central1.run.app",
}


class WebRecruitmentSDK(SyncAPIClient):
    auth: auth.AuthResource
    admin: admin.AdminResource
    patients: patients.PatientsResource
    patients_by_external_id: patients_by_external_id.PatientsByExternalIDResource
    protocol_parsing: protocol_parsing.ProtocolParsingResource
    matching_jobs: matching_jobs.MatchingJobsResource
    custom_searches: custom_searches.CustomSearchesResource
    custom_criteria: custom_criteria.CustomCriteriaResource
    criteria: criteria.CriteriaResource
    appointments: appointments.AppointmentsResource
    sites: sites.SitesResource
    crio: crio.CrioResource
    health: health.HealthResource
    system: system.SystemResource
    feature_flags: feature_flags.FeatureFlagsResource
    dashboards: dashboards.DashboardsResource
    protocols: protocols.ProtocolsResource
    export_jobs: export_jobs.ExportJobsResource
    external: external.ExternalResource
    outreach: outreach.OutreachResource
    webhooks: webhooks.WebhooksResource
    with_raw_response: WebRecruitmentSDKWithRawResponse
    with_streaming_response: WebRecruitmentSDKWithStreamedResponse

    # client options
    bearer_token: str

    _environment: Literal["development", "production", "staging"] | NotGiven

    def __init__(
        self,
        *,
        bearer_token: str | None = None,
        environment: Literal["development", "production", "staging"] | NotGiven = NOT_GIVEN,
        base_url: str | httpx.URL | None | NotGiven = NOT_GIVEN,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous WebRecruitmentSDK client instance.

        This automatically infers the `bearer_token` argument from the `WEB_RECRUITMENT_SDK_BEARER_TOKEN` environment variable if it is not provided.
        """
        if bearer_token is None:
            bearer_token = os.environ.get("WEB_RECRUITMENT_SDK_BEARER_TOKEN")
        if bearer_token is None:
            raise WebRecruitmentSDKError(
                "The bearer_token client option must be set either by passing bearer_token to the client or by setting the WEB_RECRUITMENT_SDK_BEARER_TOKEN environment variable"
            )
        self.bearer_token = bearer_token

        self._environment = environment

        base_url_env = os.environ.get("WEB_RECRUITMENT_SDK_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `WEB_RECRUITMENT_SDK_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "development"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.auth = auth.AuthResource(self)
        self.admin = admin.AdminResource(self)
        self.patients = patients.PatientsResource(self)
        self.patients_by_external_id = patients_by_external_id.PatientsByExternalIDResource(self)
        self.protocol_parsing = protocol_parsing.ProtocolParsingResource(self)
        self.matching_jobs = matching_jobs.MatchingJobsResource(self)
        self.custom_searches = custom_searches.CustomSearchesResource(self)
        self.custom_criteria = custom_criteria.CustomCriteriaResource(self)
        self.criteria = criteria.CriteriaResource(self)
        self.appointments = appointments.AppointmentsResource(self)
        self.sites = sites.SitesResource(self)
        self.crio = crio.CrioResource(self)
        self.health = health.HealthResource(self)
        self.system = system.SystemResource(self)
        self.feature_flags = feature_flags.FeatureFlagsResource(self)
        self.dashboards = dashboards.DashboardsResource(self)
        self.protocols = protocols.ProtocolsResource(self)
        self.export_jobs = export_jobs.ExportJobsResource(self)
        self.external = external.ExternalResource(self)
        self.outreach = outreach.OutreachResource(self)
        self.webhooks = webhooks.WebhooksResource(self)
        self.with_raw_response = WebRecruitmentSDKWithRawResponse(self)
        self.with_streaming_response = WebRecruitmentSDKWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        bearer_token = self.bearer_token
        return {"Authorization": f"Bearer {bearer_token}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        bearer_token: str | None = None,
        environment: Literal["development", "production", "staging"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            bearer_token=bearer_token or self.bearer_token,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncWebRecruitmentSDK(AsyncAPIClient):
    auth: auth.AsyncAuthResource
    admin: admin.AsyncAdminResource
    patients: patients.AsyncPatientsResource
    patients_by_external_id: patients_by_external_id.AsyncPatientsByExternalIDResource
    protocol_parsing: protocol_parsing.AsyncProtocolParsingResource
    matching_jobs: matching_jobs.AsyncMatchingJobsResource
    custom_searches: custom_searches.AsyncCustomSearchesResource
    custom_criteria: custom_criteria.AsyncCustomCriteriaResource
    criteria: criteria.AsyncCriteriaResource
    appointments: appointments.AsyncAppointmentsResource
    sites: sites.AsyncSitesResource
    crio: crio.AsyncCrioResource
    health: health.AsyncHealthResource
    system: system.AsyncSystemResource
    feature_flags: feature_flags.AsyncFeatureFlagsResource
    dashboards: dashboards.AsyncDashboardsResource
    protocols: protocols.AsyncProtocolsResource
    export_jobs: export_jobs.AsyncExportJobsResource
    external: external.AsyncExternalResource
    outreach: outreach.AsyncOutreachResource
    webhooks: webhooks.AsyncWebhooksResource
    with_raw_response: AsyncWebRecruitmentSDKWithRawResponse
    with_streaming_response: AsyncWebRecruitmentSDKWithStreamedResponse

    # client options
    bearer_token: str

    _environment: Literal["development", "production", "staging"] | NotGiven

    def __init__(
        self,
        *,
        bearer_token: str | None = None,
        environment: Literal["development", "production", "staging"] | NotGiven = NOT_GIVEN,
        base_url: str | httpx.URL | None | NotGiven = NOT_GIVEN,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncWebRecruitmentSDK client instance.

        This automatically infers the `bearer_token` argument from the `WEB_RECRUITMENT_SDK_BEARER_TOKEN` environment variable if it is not provided.
        """
        if bearer_token is None:
            bearer_token = os.environ.get("WEB_RECRUITMENT_SDK_BEARER_TOKEN")
        if bearer_token is None:
            raise WebRecruitmentSDKError(
                "The bearer_token client option must be set either by passing bearer_token to the client or by setting the WEB_RECRUITMENT_SDK_BEARER_TOKEN environment variable"
            )
        self.bearer_token = bearer_token

        self._environment = environment

        base_url_env = os.environ.get("WEB_RECRUITMENT_SDK_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `WEB_RECRUITMENT_SDK_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "development"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.auth = auth.AsyncAuthResource(self)
        self.admin = admin.AsyncAdminResource(self)
        self.patients = patients.AsyncPatientsResource(self)
        self.patients_by_external_id = patients_by_external_id.AsyncPatientsByExternalIDResource(self)
        self.protocol_parsing = protocol_parsing.AsyncProtocolParsingResource(self)
        self.matching_jobs = matching_jobs.AsyncMatchingJobsResource(self)
        self.custom_searches = custom_searches.AsyncCustomSearchesResource(self)
        self.custom_criteria = custom_criteria.AsyncCustomCriteriaResource(self)
        self.criteria = criteria.AsyncCriteriaResource(self)
        self.appointments = appointments.AsyncAppointmentsResource(self)
        self.sites = sites.AsyncSitesResource(self)
        self.crio = crio.AsyncCrioResource(self)
        self.health = health.AsyncHealthResource(self)
        self.system = system.AsyncSystemResource(self)
        self.feature_flags = feature_flags.AsyncFeatureFlagsResource(self)
        self.dashboards = dashboards.AsyncDashboardsResource(self)
        self.protocols = protocols.AsyncProtocolsResource(self)
        self.export_jobs = export_jobs.AsyncExportJobsResource(self)
        self.external = external.AsyncExternalResource(self)
        self.outreach = outreach.AsyncOutreachResource(self)
        self.webhooks = webhooks.AsyncWebhooksResource(self)
        self.with_raw_response = AsyncWebRecruitmentSDKWithRawResponse(self)
        self.with_streaming_response = AsyncWebRecruitmentSDKWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        bearer_token = self.bearer_token
        return {"Authorization": f"Bearer {bearer_token}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        bearer_token: str | None = None,
        environment: Literal["development", "production", "staging"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            bearer_token=bearer_token or self.bearer_token,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class WebRecruitmentSDKWithRawResponse:
    def __init__(self, client: WebRecruitmentSDK) -> None:
        self.auth = auth.AuthResourceWithRawResponse(client.auth)
        self.admin = admin.AdminResourceWithRawResponse(client.admin)
        self.patients = patients.PatientsResourceWithRawResponse(client.patients)
        self.patients_by_external_id = patients_by_external_id.PatientsByExternalIDResourceWithRawResponse(
            client.patients_by_external_id
        )
        self.protocol_parsing = protocol_parsing.ProtocolParsingResourceWithRawResponse(client.protocol_parsing)
        self.matching_jobs = matching_jobs.MatchingJobsResourceWithRawResponse(client.matching_jobs)
        self.custom_searches = custom_searches.CustomSearchesResourceWithRawResponse(client.custom_searches)
        self.custom_criteria = custom_criteria.CustomCriteriaResourceWithRawResponse(client.custom_criteria)
        self.criteria = criteria.CriteriaResourceWithRawResponse(client.criteria)
        self.appointments = appointments.AppointmentsResourceWithRawResponse(client.appointments)
        self.sites = sites.SitesResourceWithRawResponse(client.sites)
        self.crio = crio.CrioResourceWithRawResponse(client.crio)
        self.health = health.HealthResourceWithRawResponse(client.health)
        self.system = system.SystemResourceWithRawResponse(client.system)
        self.feature_flags = feature_flags.FeatureFlagsResourceWithRawResponse(client.feature_flags)
        self.dashboards = dashboards.DashboardsResourceWithRawResponse(client.dashboards)
        self.protocols = protocols.ProtocolsResourceWithRawResponse(client.protocols)
        self.export_jobs = export_jobs.ExportJobsResourceWithRawResponse(client.export_jobs)
        self.external = external.ExternalResourceWithRawResponse(client.external)
        self.outreach = outreach.OutreachResourceWithRawResponse(client.outreach)
        self.webhooks = webhooks.WebhooksResourceWithRawResponse(client.webhooks)


class AsyncWebRecruitmentSDKWithRawResponse:
    def __init__(self, client: AsyncWebRecruitmentSDK) -> None:
        self.auth = auth.AsyncAuthResourceWithRawResponse(client.auth)
        self.admin = admin.AsyncAdminResourceWithRawResponse(client.admin)
        self.patients = patients.AsyncPatientsResourceWithRawResponse(client.patients)
        self.patients_by_external_id = patients_by_external_id.AsyncPatientsByExternalIDResourceWithRawResponse(
            client.patients_by_external_id
        )
        self.protocol_parsing = protocol_parsing.AsyncProtocolParsingResourceWithRawResponse(client.protocol_parsing)
        self.matching_jobs = matching_jobs.AsyncMatchingJobsResourceWithRawResponse(client.matching_jobs)
        self.custom_searches = custom_searches.AsyncCustomSearchesResourceWithRawResponse(client.custom_searches)
        self.custom_criteria = custom_criteria.AsyncCustomCriteriaResourceWithRawResponse(client.custom_criteria)
        self.criteria = criteria.AsyncCriteriaResourceWithRawResponse(client.criteria)
        self.appointments = appointments.AsyncAppointmentsResourceWithRawResponse(client.appointments)
        self.sites = sites.AsyncSitesResourceWithRawResponse(client.sites)
        self.crio = crio.AsyncCrioResourceWithRawResponse(client.crio)
        self.health = health.AsyncHealthResourceWithRawResponse(client.health)
        self.system = system.AsyncSystemResourceWithRawResponse(client.system)
        self.feature_flags = feature_flags.AsyncFeatureFlagsResourceWithRawResponse(client.feature_flags)
        self.dashboards = dashboards.AsyncDashboardsResourceWithRawResponse(client.dashboards)
        self.protocols = protocols.AsyncProtocolsResourceWithRawResponse(client.protocols)
        self.export_jobs = export_jobs.AsyncExportJobsResourceWithRawResponse(client.export_jobs)
        self.external = external.AsyncExternalResourceWithRawResponse(client.external)
        self.outreach = outreach.AsyncOutreachResourceWithRawResponse(client.outreach)
        self.webhooks = webhooks.AsyncWebhooksResourceWithRawResponse(client.webhooks)


class WebRecruitmentSDKWithStreamedResponse:
    def __init__(self, client: WebRecruitmentSDK) -> None:
        self.auth = auth.AuthResourceWithStreamingResponse(client.auth)
        self.admin = admin.AdminResourceWithStreamingResponse(client.admin)
        self.patients = patients.PatientsResourceWithStreamingResponse(client.patients)
        self.patients_by_external_id = patients_by_external_id.PatientsByExternalIDResourceWithStreamingResponse(
            client.patients_by_external_id
        )
        self.protocol_parsing = protocol_parsing.ProtocolParsingResourceWithStreamingResponse(client.protocol_parsing)
        self.matching_jobs = matching_jobs.MatchingJobsResourceWithStreamingResponse(client.matching_jobs)
        self.custom_searches = custom_searches.CustomSearchesResourceWithStreamingResponse(client.custom_searches)
        self.custom_criteria = custom_criteria.CustomCriteriaResourceWithStreamingResponse(client.custom_criteria)
        self.criteria = criteria.CriteriaResourceWithStreamingResponse(client.criteria)
        self.appointments = appointments.AppointmentsResourceWithStreamingResponse(client.appointments)
        self.sites = sites.SitesResourceWithStreamingResponse(client.sites)
        self.crio = crio.CrioResourceWithStreamingResponse(client.crio)
        self.health = health.HealthResourceWithStreamingResponse(client.health)
        self.system = system.SystemResourceWithStreamingResponse(client.system)
        self.feature_flags = feature_flags.FeatureFlagsResourceWithStreamingResponse(client.feature_flags)
        self.dashboards = dashboards.DashboardsResourceWithStreamingResponse(client.dashboards)
        self.protocols = protocols.ProtocolsResourceWithStreamingResponse(client.protocols)
        self.export_jobs = export_jobs.ExportJobsResourceWithStreamingResponse(client.export_jobs)
        self.external = external.ExternalResourceWithStreamingResponse(client.external)
        self.outreach = outreach.OutreachResourceWithStreamingResponse(client.outreach)
        self.webhooks = webhooks.WebhooksResourceWithStreamingResponse(client.webhooks)


class AsyncWebRecruitmentSDKWithStreamedResponse:
    def __init__(self, client: AsyncWebRecruitmentSDK) -> None:
        self.auth = auth.AsyncAuthResourceWithStreamingResponse(client.auth)
        self.admin = admin.AsyncAdminResourceWithStreamingResponse(client.admin)
        self.patients = patients.AsyncPatientsResourceWithStreamingResponse(client.patients)
        self.patients_by_external_id = patients_by_external_id.AsyncPatientsByExternalIDResourceWithStreamingResponse(
            client.patients_by_external_id
        )
        self.protocol_parsing = protocol_parsing.AsyncProtocolParsingResourceWithStreamingResponse(
            client.protocol_parsing
        )
        self.matching_jobs = matching_jobs.AsyncMatchingJobsResourceWithStreamingResponse(client.matching_jobs)
        self.custom_searches = custom_searches.AsyncCustomSearchesResourceWithStreamingResponse(client.custom_searches)
        self.custom_criteria = custom_criteria.AsyncCustomCriteriaResourceWithStreamingResponse(client.custom_criteria)
        self.criteria = criteria.AsyncCriteriaResourceWithStreamingResponse(client.criteria)
        self.appointments = appointments.AsyncAppointmentsResourceWithStreamingResponse(client.appointments)
        self.sites = sites.AsyncSitesResourceWithStreamingResponse(client.sites)
        self.crio = crio.AsyncCrioResourceWithStreamingResponse(client.crio)
        self.health = health.AsyncHealthResourceWithStreamingResponse(client.health)
        self.system = system.AsyncSystemResourceWithStreamingResponse(client.system)
        self.feature_flags = feature_flags.AsyncFeatureFlagsResourceWithStreamingResponse(client.feature_flags)
        self.dashboards = dashboards.AsyncDashboardsResourceWithStreamingResponse(client.dashboards)
        self.protocols = protocols.AsyncProtocolsResourceWithStreamingResponse(client.protocols)
        self.export_jobs = export_jobs.AsyncExportJobsResourceWithStreamingResponse(client.export_jobs)
        self.external = external.AsyncExternalResourceWithStreamingResponse(client.external)
        self.outreach = outreach.AsyncOutreachResourceWithStreamingResponse(client.outreach)
        self.webhooks = webhooks.AsyncWebhooksResourceWithStreamingResponse(client.webhooks)


Client = WebRecruitmentSDK

AsyncClient = AsyncWebRecruitmentSDK
