# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.external.carequality import (
    PatientSearchResponse,
    PatientRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPatients:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: WebRecruitmentSDK) -> None:
        patient = client.external.carequality.patients.retrieve(
            carequality_patient_id="carequality_patient_id",
            x_api_key="X-API-Key",
        )
        assert_matches_type(PatientRetrieveResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        response = client.external.carequality.patients.with_raw_response.retrieve(
            carequality_patient_id="carequality_patient_id",
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(PatientRetrieveResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        with client.external.carequality.patients.with_streaming_response.retrieve(
            carequality_patient_id="carequality_patient_id",
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(PatientRetrieveResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `carequality_patient_id` but received ''"
        ):
            client.external.carequality.patients.with_raw_response.retrieve(
                carequality_patient_id="",
                x_api_key="X-API-Key",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_search(self, client: WebRecruitmentSDK) -> None:
        patient = client.external.carequality.patients.search(
            date_of_birth="dateOfBirth",
            first_name="firstName",
            gender="female",
            last_name="lastName",
            x_api_key="X-API-Key",
        )
        assert_matches_type(PatientSearchResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_search(self, client: WebRecruitmentSDK) -> None:
        response = client.external.carequality.patients.with_raw_response.search(
            date_of_birth="dateOfBirth",
            first_name="firstName",
            gender="female",
            last_name="lastName",
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(PatientSearchResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_search(self, client: WebRecruitmentSDK) -> None:
        with client.external.carequality.patients.with_streaming_response.search(
            date_of_birth="dateOfBirth",
            first_name="firstName",
            gender="female",
            last_name="lastName",
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(PatientSearchResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPatients:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.external.carequality.patients.retrieve(
            carequality_patient_id="carequality_patient_id",
            x_api_key="X-API-Key",
        )
        assert_matches_type(PatientRetrieveResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.external.carequality.patients.with_raw_response.retrieve(
            carequality_patient_id="carequality_patient_id",
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(PatientRetrieveResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.external.carequality.patients.with_streaming_response.retrieve(
            carequality_patient_id="carequality_patient_id",
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(PatientRetrieveResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `carequality_patient_id` but received ''"
        ):
            await async_client.external.carequality.patients.with_raw_response.retrieve(
                carequality_patient_id="",
                x_api_key="X-API-Key",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_search(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.external.carequality.patients.search(
            date_of_birth="dateOfBirth",
            first_name="firstName",
            gender="female",
            last_name="lastName",
            x_api_key="X-API-Key",
        )
        assert_matches_type(PatientSearchResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_search(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.external.carequality.patients.with_raw_response.search(
            date_of_birth="dateOfBirth",
            first_name="firstName",
            gender="female",
            last_name="lastName",
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(PatientSearchResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.external.carequality.patients.with_streaming_response.search(
            date_of_birth="dateOfBirth",
            first_name="firstName",
            gender="female",
            last_name="lastName",
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(PatientSearchResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True
