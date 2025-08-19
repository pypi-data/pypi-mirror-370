# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types import PatientRead

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPatientsByExternalID:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: WebRecruitmentSDK) -> None:
        patients_by_external_id = client.patients_by_external_id.retrieve(
            "external_id",
        )
        assert_matches_type(PatientRead, patients_by_external_id, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        response = client.patients_by_external_id.with_raw_response.retrieve(
            "external_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patients_by_external_id = response.parse()
        assert_matches_type(PatientRead, patients_by_external_id, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        with client.patients_by_external_id.with_streaming_response.retrieve(
            "external_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patients_by_external_id = response.parse()
            assert_matches_type(PatientRead, patients_by_external_id, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `external_id` but received ''"):
            client.patients_by_external_id.with_raw_response.retrieve(
                "",
            )


class TestAsyncPatientsByExternalID:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patients_by_external_id = await async_client.patients_by_external_id.retrieve(
            "external_id",
        )
        assert_matches_type(PatientRead, patients_by_external_id, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.patients_by_external_id.with_raw_response.retrieve(
            "external_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patients_by_external_id = await response.parse()
        assert_matches_type(PatientRead, patients_by_external_id, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.patients_by_external_id.with_streaming_response.retrieve(
            "external_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patients_by_external_id = await response.parse()
            assert_matches_type(PatientRead, patients_by_external_id, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `external_id` but received ''"):
            await async_client.patients_by_external_id.with_raw_response.retrieve(
                "",
            )
