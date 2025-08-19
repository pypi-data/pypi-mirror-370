# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types import (
    SystemUpdateAccountResponse,
    SystemSearchEntitiesResponse,
    SystemPatchPatientExportResponse,
    SystemGetPatientMatchDataResponse,
    SystemCreateCriteriaInstanceResponse,
    SystemCreateEntitySearchIndexResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSystem:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_bulk_search_patient_match_data(self, client: WebRecruitmentSDK) -> None:
        system = client.system.bulk_search_patient_match_data(
            tenant_db_name="tenant_db_name",
            search_text="searchText",
            trially_patient_ids=["string"],
        )
        assert_matches_type(object, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_bulk_search_patient_match_data(self, client: WebRecruitmentSDK) -> None:
        response = client.system.with_raw_response.bulk_search_patient_match_data(
            tenant_db_name="tenant_db_name",
            search_text="searchText",
            trially_patient_ids=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = response.parse()
        assert_matches_type(object, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_bulk_search_patient_match_data(self, client: WebRecruitmentSDK) -> None:
        with client.system.with_streaming_response.bulk_search_patient_match_data(
            tenant_db_name="tenant_db_name",
            search_text="searchText",
            trially_patient_ids=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = response.parse()
            assert_matches_type(object, system, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_bulk_search_patient_match_data(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.with_raw_response.bulk_search_patient_match_data(
                tenant_db_name="",
                search_text="searchText",
                trially_patient_ids=["string"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_criteria_instance(self, client: WebRecruitmentSDK) -> None:
        system = client.system.create_criteria_instance(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "answer": "yes",
                    "criteria_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(SystemCreateCriteriaInstanceResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_criteria_instance(self, client: WebRecruitmentSDK) -> None:
        response = client.system.with_raw_response.create_criteria_instance(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "answer": "yes",
                    "criteria_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = response.parse()
        assert_matches_type(SystemCreateCriteriaInstanceResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_criteria_instance(self, client: WebRecruitmentSDK) -> None:
        with client.system.with_streaming_response.create_criteria_instance(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "answer": "yes",
                    "criteria_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = response.parse()
            assert_matches_type(SystemCreateCriteriaInstanceResponse, system, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_criteria_instance(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.with_raw_response.create_criteria_instance(
                tenant_db_name="",
                body=[
                    {
                        "answer": "yes",
                        "criteria_id": 0,
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_entity_search_index(self, client: WebRecruitmentSDK) -> None:
        system = client.system.create_entity_search_index(
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(SystemCreateEntitySearchIndexResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_entity_search_index_with_all_params(self, client: WebRecruitmentSDK) -> None:
        system = client.system.create_entity_search_index(
            tenant_db_name="tenant_db_name",
            override_num_leaves=0,
            recreate=True,
        )
        assert_matches_type(SystemCreateEntitySearchIndexResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_entity_search_index(self, client: WebRecruitmentSDK) -> None:
        response = client.system.with_raw_response.create_entity_search_index(
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = response.parse()
        assert_matches_type(SystemCreateEntitySearchIndexResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_entity_search_index(self, client: WebRecruitmentSDK) -> None:
        with client.system.with_streaming_response.create_entity_search_index(
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = response.parse()
            assert_matches_type(SystemCreateEntitySearchIndexResponse, system, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_entity_search_index(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.with_raw_response.create_entity_search_index(
                tenant_db_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_connection_pool_status(self, client: WebRecruitmentSDK) -> None:
        system = client.system.get_connection_pool_status(
            "db_name",
        )
        assert_matches_type(str, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_connection_pool_status(self, client: WebRecruitmentSDK) -> None:
        response = client.system.with_raw_response.get_connection_pool_status(
            "db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = response.parse()
        assert_matches_type(str, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_connection_pool_status(self, client: WebRecruitmentSDK) -> None:
        with client.system.with_streaming_response.get_connection_pool_status(
            "db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = response.parse()
            assert_matches_type(str, system, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_connection_pool_status(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `db_name` but received ''"):
            client.system.with_raw_response.get_connection_pool_status(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_patient_match_data(self, client: WebRecruitmentSDK) -> None:
        system = client.system.get_patient_match_data(
            tenant_db_name="tenant_db_name",
            criteria_id=0,
            patient_ids=["string"],
        )
        assert_matches_type(SystemGetPatientMatchDataResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_patient_match_data(self, client: WebRecruitmentSDK) -> None:
        response = client.system.with_raw_response.get_patient_match_data(
            tenant_db_name="tenant_db_name",
            criteria_id=0,
            patient_ids=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = response.parse()
        assert_matches_type(SystemGetPatientMatchDataResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_patient_match_data(self, client: WebRecruitmentSDK) -> None:
        with client.system.with_streaming_response.get_patient_match_data(
            tenant_db_name="tenant_db_name",
            criteria_id=0,
            patient_ids=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = response.parse()
            assert_matches_type(SystemGetPatientMatchDataResponse, system, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_patient_match_data(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.with_raw_response.get_patient_match_data(
                tenant_db_name="",
                criteria_id=0,
                patient_ids=["string"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_patch_patient_export(self, client: WebRecruitmentSDK) -> None:
        system = client.system.patch_patient_export(
            patient_ctms_export_id=0,
            tenant_db_name="tenant_db_name",
            status="IN_PROGRESS",
        )
        assert_matches_type(SystemPatchPatientExportResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_patch_patient_export(self, client: WebRecruitmentSDK) -> None:
        response = client.system.with_raw_response.patch_patient_export(
            patient_ctms_export_id=0,
            tenant_db_name="tenant_db_name",
            status="IN_PROGRESS",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = response.parse()
        assert_matches_type(SystemPatchPatientExportResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_patch_patient_export(self, client: WebRecruitmentSDK) -> None:
        with client.system.with_streaming_response.patch_patient_export(
            patient_ctms_export_id=0,
            tenant_db_name="tenant_db_name",
            status="IN_PROGRESS",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = response.parse()
            assert_matches_type(SystemPatchPatientExportResponse, system, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_patch_patient_export(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.with_raw_response.patch_patient_export(
                patient_ctms_export_id=0,
                tenant_db_name="",
                status="IN_PROGRESS",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_ping(self, client: WebRecruitmentSDK) -> None:
        system = client.system.ping()
        assert_matches_type(object, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_ping(self, client: WebRecruitmentSDK) -> None:
        response = client.system.with_raw_response.ping()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = response.parse()
        assert_matches_type(object, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_ping(self, client: WebRecruitmentSDK) -> None:
        with client.system.with_streaming_response.ping() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = response.parse()
            assert_matches_type(object, system, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_search_entities(self, client: WebRecruitmentSDK) -> None:
        system = client.system.search_entities(
            tenant_db_name="tenant_db_name",
            search_text="x",
        )
        assert_matches_type(SystemSearchEntitiesResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_search_entities_with_all_params(self, client: WebRecruitmentSDK) -> None:
        system = client.system.search_entities(
            tenant_db_name="tenant_db_name",
            search_text="x",
            limit=1,
            similarity_threshold=0,
        )
        assert_matches_type(SystemSearchEntitiesResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_search_entities(self, client: WebRecruitmentSDK) -> None:
        response = client.system.with_raw_response.search_entities(
            tenant_db_name="tenant_db_name",
            search_text="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = response.parse()
        assert_matches_type(SystemSearchEntitiesResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_search_entities(self, client: WebRecruitmentSDK) -> None:
        with client.system.with_streaming_response.search_entities(
            tenant_db_name="tenant_db_name",
            search_text="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = response.parse()
            assert_matches_type(SystemSearchEntitiesResponse, system, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_search_entities(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.with_raw_response.search_entities(
                tenant_db_name="",
                search_text="x",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_account(self, client: WebRecruitmentSDK) -> None:
        system = client.system.update_account(
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(SystemUpdateAccountResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_account_with_all_params(self, client: WebRecruitmentSDK) -> None:
        system = client.system.update_account(
            tenant_db_name="tenant_db_name",
            has_carequality_sites=True,
        )
        assert_matches_type(SystemUpdateAccountResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_account(self, client: WebRecruitmentSDK) -> None:
        response = client.system.with_raw_response.update_account(
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = response.parse()
        assert_matches_type(SystemUpdateAccountResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_account(self, client: WebRecruitmentSDK) -> None:
        with client.system.with_streaming_response.update_account(
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = response.parse()
            assert_matches_type(SystemUpdateAccountResponse, system, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_account(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.with_raw_response.update_account(
                tenant_db_name="",
            )


class TestAsyncSystem:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_bulk_search_patient_match_data(self, async_client: AsyncWebRecruitmentSDK) -> None:
        system = await async_client.system.bulk_search_patient_match_data(
            tenant_db_name="tenant_db_name",
            search_text="searchText",
            trially_patient_ids=["string"],
        )
        assert_matches_type(object, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_bulk_search_patient_match_data(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.with_raw_response.bulk_search_patient_match_data(
            tenant_db_name="tenant_db_name",
            search_text="searchText",
            trially_patient_ids=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = await response.parse()
        assert_matches_type(object, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_bulk_search_patient_match_data(
        self, async_client: AsyncWebRecruitmentSDK
    ) -> None:
        async with async_client.system.with_streaming_response.bulk_search_patient_match_data(
            tenant_db_name="tenant_db_name",
            search_text="searchText",
            trially_patient_ids=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = await response.parse()
            assert_matches_type(object, system, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_bulk_search_patient_match_data(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.with_raw_response.bulk_search_patient_match_data(
                tenant_db_name="",
                search_text="searchText",
                trially_patient_ids=["string"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_criteria_instance(self, async_client: AsyncWebRecruitmentSDK) -> None:
        system = await async_client.system.create_criteria_instance(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "answer": "yes",
                    "criteria_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(SystemCreateCriteriaInstanceResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_criteria_instance(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.with_raw_response.create_criteria_instance(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "answer": "yes",
                    "criteria_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = await response.parse()
        assert_matches_type(SystemCreateCriteriaInstanceResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_criteria_instance(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.with_streaming_response.create_criteria_instance(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "answer": "yes",
                    "criteria_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = await response.parse()
            assert_matches_type(SystemCreateCriteriaInstanceResponse, system, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_criteria_instance(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.with_raw_response.create_criteria_instance(
                tenant_db_name="",
                body=[
                    {
                        "answer": "yes",
                        "criteria_id": 0,
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_entity_search_index(self, async_client: AsyncWebRecruitmentSDK) -> None:
        system = await async_client.system.create_entity_search_index(
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(SystemCreateEntitySearchIndexResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_entity_search_index_with_all_params(
        self, async_client: AsyncWebRecruitmentSDK
    ) -> None:
        system = await async_client.system.create_entity_search_index(
            tenant_db_name="tenant_db_name",
            override_num_leaves=0,
            recreate=True,
        )
        assert_matches_type(SystemCreateEntitySearchIndexResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_entity_search_index(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.with_raw_response.create_entity_search_index(
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = await response.parse()
        assert_matches_type(SystemCreateEntitySearchIndexResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_entity_search_index(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.with_streaming_response.create_entity_search_index(
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = await response.parse()
            assert_matches_type(SystemCreateEntitySearchIndexResponse, system, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_entity_search_index(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.with_raw_response.create_entity_search_index(
                tenant_db_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_connection_pool_status(self, async_client: AsyncWebRecruitmentSDK) -> None:
        system = await async_client.system.get_connection_pool_status(
            "db_name",
        )
        assert_matches_type(str, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_connection_pool_status(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.with_raw_response.get_connection_pool_status(
            "db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = await response.parse()
        assert_matches_type(str, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_connection_pool_status(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.with_streaming_response.get_connection_pool_status(
            "db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = await response.parse()
            assert_matches_type(str, system, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_connection_pool_status(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `db_name` but received ''"):
            await async_client.system.with_raw_response.get_connection_pool_status(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_patient_match_data(self, async_client: AsyncWebRecruitmentSDK) -> None:
        system = await async_client.system.get_patient_match_data(
            tenant_db_name="tenant_db_name",
            criteria_id=0,
            patient_ids=["string"],
        )
        assert_matches_type(SystemGetPatientMatchDataResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_patient_match_data(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.with_raw_response.get_patient_match_data(
            tenant_db_name="tenant_db_name",
            criteria_id=0,
            patient_ids=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = await response.parse()
        assert_matches_type(SystemGetPatientMatchDataResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_patient_match_data(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.with_streaming_response.get_patient_match_data(
            tenant_db_name="tenant_db_name",
            criteria_id=0,
            patient_ids=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = await response.parse()
            assert_matches_type(SystemGetPatientMatchDataResponse, system, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_patient_match_data(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.with_raw_response.get_patient_match_data(
                tenant_db_name="",
                criteria_id=0,
                patient_ids=["string"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_patch_patient_export(self, async_client: AsyncWebRecruitmentSDK) -> None:
        system = await async_client.system.patch_patient_export(
            patient_ctms_export_id=0,
            tenant_db_name="tenant_db_name",
            status="IN_PROGRESS",
        )
        assert_matches_type(SystemPatchPatientExportResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_patch_patient_export(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.with_raw_response.patch_patient_export(
            patient_ctms_export_id=0,
            tenant_db_name="tenant_db_name",
            status="IN_PROGRESS",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = await response.parse()
        assert_matches_type(SystemPatchPatientExportResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_patch_patient_export(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.with_streaming_response.patch_patient_export(
            patient_ctms_export_id=0,
            tenant_db_name="tenant_db_name",
            status="IN_PROGRESS",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = await response.parse()
            assert_matches_type(SystemPatchPatientExportResponse, system, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_patch_patient_export(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.with_raw_response.patch_patient_export(
                patient_ctms_export_id=0,
                tenant_db_name="",
                status="IN_PROGRESS",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_ping(self, async_client: AsyncWebRecruitmentSDK) -> None:
        system = await async_client.system.ping()
        assert_matches_type(object, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_ping(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.with_raw_response.ping()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = await response.parse()
        assert_matches_type(object, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_ping(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.with_streaming_response.ping() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = await response.parse()
            assert_matches_type(object, system, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_search_entities(self, async_client: AsyncWebRecruitmentSDK) -> None:
        system = await async_client.system.search_entities(
            tenant_db_name="tenant_db_name",
            search_text="x",
        )
        assert_matches_type(SystemSearchEntitiesResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_search_entities_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        system = await async_client.system.search_entities(
            tenant_db_name="tenant_db_name",
            search_text="x",
            limit=1,
            similarity_threshold=0,
        )
        assert_matches_type(SystemSearchEntitiesResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_search_entities(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.with_raw_response.search_entities(
            tenant_db_name="tenant_db_name",
            search_text="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = await response.parse()
        assert_matches_type(SystemSearchEntitiesResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_search_entities(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.with_streaming_response.search_entities(
            tenant_db_name="tenant_db_name",
            search_text="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = await response.parse()
            assert_matches_type(SystemSearchEntitiesResponse, system, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_search_entities(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.with_raw_response.search_entities(
                tenant_db_name="",
                search_text="x",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_account(self, async_client: AsyncWebRecruitmentSDK) -> None:
        system = await async_client.system.update_account(
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(SystemUpdateAccountResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_account_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        system = await async_client.system.update_account(
            tenant_db_name="tenant_db_name",
            has_carequality_sites=True,
        )
        assert_matches_type(SystemUpdateAccountResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_account(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.with_raw_response.update_account(
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = await response.parse()
        assert_matches_type(SystemUpdateAccountResponse, system, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_account(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.with_streaming_response.update_account(
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = await response.parse()
            assert_matches_type(SystemUpdateAccountResponse, system, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_account(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.with_raw_response.update_account(
                tenant_db_name="",
            )
