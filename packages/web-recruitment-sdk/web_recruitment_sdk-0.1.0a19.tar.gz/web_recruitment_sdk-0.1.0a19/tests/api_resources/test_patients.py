# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types import (
    PatientRead,
    PatientListResponse,
    PatientImportCsvResponse,
    PatientGetExportsResponse,
    PatientGetByProtocolResponse,
    PatientGetProtocolMatchesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPatients:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: WebRecruitmentSDK) -> None:
        patient = client.patients.retrieve(
            0,
        )
        assert_matches_type(PatientRead, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        response = client.patients.with_raw_response.retrieve(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(PatientRead, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        with client.patients.with_streaming_response.retrieve(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(PatientRead, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: WebRecruitmentSDK) -> None:
        patient = client.patients.update(
            patient_id=0,
            do_not_call=True,
        )
        assert_matches_type(PatientRead, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: WebRecruitmentSDK) -> None:
        response = client.patients.with_raw_response.update(
            patient_id=0,
            do_not_call=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(PatientRead, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: WebRecruitmentSDK) -> None:
        with client.patients.with_streaming_response.update(
            patient_id=0,
            do_not_call=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(PatientRead, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: WebRecruitmentSDK) -> None:
        patient = client.patients.list()
        assert_matches_type(PatientListResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: WebRecruitmentSDK) -> None:
        patient = client.patients.list(
            limit=0,
        )
        assert_matches_type(PatientListResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: WebRecruitmentSDK) -> None:
        response = client.patients.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(PatientListResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: WebRecruitmentSDK) -> None:
        with client.patients.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(PatientListResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_by_protocol(self, client: WebRecruitmentSDK) -> None:
        patient = client.patients.get_by_protocol(
            protocol_id=0,
        )
        assert_matches_type(PatientGetByProtocolResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_by_protocol_with_all_params(self, client: WebRecruitmentSDK) -> None:
        patient = client.patients.get_by_protocol(
            protocol_id=0,
            limit=0,
        )
        assert_matches_type(PatientGetByProtocolResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_by_protocol(self, client: WebRecruitmentSDK) -> None:
        response = client.patients.with_raw_response.get_by_protocol(
            protocol_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(PatientGetByProtocolResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_by_protocol(self, client: WebRecruitmentSDK) -> None:
        with client.patients.with_streaming_response.get_by_protocol(
            protocol_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(PatientGetByProtocolResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_exports(self, client: WebRecruitmentSDK) -> None:
        patient = client.patients.get_exports(
            "patient_id",
        )
        assert_matches_type(PatientGetExportsResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_exports(self, client: WebRecruitmentSDK) -> None:
        response = client.patients.with_raw_response.get_exports(
            "patient_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(PatientGetExportsResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_exports(self, client: WebRecruitmentSDK) -> None:
        with client.patients.with_streaming_response.get_exports(
            "patient_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(PatientGetExportsResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_exports(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `patient_id` but received ''"):
            client.patients.with_raw_response.get_exports(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_protocol_matches(self, client: WebRecruitmentSDK) -> None:
        patient = client.patients.get_protocol_matches(
            0,
        )
        assert_matches_type(PatientGetProtocolMatchesResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_protocol_matches(self, client: WebRecruitmentSDK) -> None:
        response = client.patients.with_raw_response.get_protocol_matches(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(PatientGetProtocolMatchesResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_protocol_matches(self, client: WebRecruitmentSDK) -> None:
        with client.patients.with_streaming_response.get_protocol_matches(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(PatientGetProtocolMatchesResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_import_csv(self, client: WebRecruitmentSDK) -> None:
        patient = client.patients.import_csv(
            fallback_zip_code="fallbackZipCode",
            site_id=0,
            storage_url="storageUrl",
        )
        assert_matches_type(PatientImportCsvResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_import_csv(self, client: WebRecruitmentSDK) -> None:
        response = client.patients.with_raw_response.import_csv(
            fallback_zip_code="fallbackZipCode",
            site_id=0,
            storage_url="storageUrl",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(PatientImportCsvResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_import_csv(self, client: WebRecruitmentSDK) -> None:
        with client.patients.with_streaming_response.import_csv(
            fallback_zip_code="fallbackZipCode",
            site_id=0,
            storage_url="storageUrl",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(PatientImportCsvResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPatients:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.patients.retrieve(
            0,
        )
        assert_matches_type(PatientRead, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.patients.with_raw_response.retrieve(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(PatientRead, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.patients.with_streaming_response.retrieve(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(PatientRead, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.patients.update(
            patient_id=0,
            do_not_call=True,
        )
        assert_matches_type(PatientRead, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.patients.with_raw_response.update(
            patient_id=0,
            do_not_call=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(PatientRead, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.patients.with_streaming_response.update(
            patient_id=0,
            do_not_call=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(PatientRead, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.patients.list()
        assert_matches_type(PatientListResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.patients.list(
            limit=0,
        )
        assert_matches_type(PatientListResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.patients.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(PatientListResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.patients.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(PatientListResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_by_protocol(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.patients.get_by_protocol(
            protocol_id=0,
        )
        assert_matches_type(PatientGetByProtocolResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_by_protocol_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.patients.get_by_protocol(
            protocol_id=0,
            limit=0,
        )
        assert_matches_type(PatientGetByProtocolResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_by_protocol(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.patients.with_raw_response.get_by_protocol(
            protocol_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(PatientGetByProtocolResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_by_protocol(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.patients.with_streaming_response.get_by_protocol(
            protocol_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(PatientGetByProtocolResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_exports(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.patients.get_exports(
            "patient_id",
        )
        assert_matches_type(PatientGetExportsResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_exports(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.patients.with_raw_response.get_exports(
            "patient_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(PatientGetExportsResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_exports(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.patients.with_streaming_response.get_exports(
            "patient_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(PatientGetExportsResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_exports(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `patient_id` but received ''"):
            await async_client.patients.with_raw_response.get_exports(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_protocol_matches(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.patients.get_protocol_matches(
            0,
        )
        assert_matches_type(PatientGetProtocolMatchesResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_protocol_matches(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.patients.with_raw_response.get_protocol_matches(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(PatientGetProtocolMatchesResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_protocol_matches(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.patients.with_streaming_response.get_protocol_matches(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(PatientGetProtocolMatchesResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_import_csv(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.patients.import_csv(
            fallback_zip_code="fallbackZipCode",
            site_id=0,
            storage_url="storageUrl",
        )
        assert_matches_type(PatientImportCsvResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_import_csv(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.patients.with_raw_response.import_csv(
            fallback_zip_code="fallbackZipCode",
            site_id=0,
            storage_url="storageUrl",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(PatientImportCsvResponse, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_import_csv(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.patients.with_streaming_response.import_csv(
            fallback_zip_code="fallbackZipCode",
            site_id=0,
            storage_url="storageUrl",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(PatientImportCsvResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True
