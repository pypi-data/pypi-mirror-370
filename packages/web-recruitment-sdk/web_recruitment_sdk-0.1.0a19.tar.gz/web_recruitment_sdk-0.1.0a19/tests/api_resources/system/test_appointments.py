# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.system import AppointmentListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAppointments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: WebRecruitmentSDK) -> None:
        appointment = client.system.appointments.list(
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(AppointmentListResponse, appointment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: WebRecruitmentSDK) -> None:
        appointment = client.system.appointments.list(
            tenant_db_name="tenant_db_name",
            limit=0,
        )
        assert_matches_type(AppointmentListResponse, appointment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: WebRecruitmentSDK) -> None:
        response = client.system.appointments.with_raw_response.list(
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        appointment = response.parse()
        assert_matches_type(AppointmentListResponse, appointment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: WebRecruitmentSDK) -> None:
        with client.system.appointments.with_streaming_response.list(
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            appointment = response.parse()
            assert_matches_type(AppointmentListResponse, appointment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.appointments.with_raw_response.list(
                tenant_db_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: WebRecruitmentSDK) -> None:
        appointment = client.system.appointments.delete(
            trially_appointment_id="trially_appointment_id",
            tenant_db_name="tenant_db_name",
        )
        assert appointment is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: WebRecruitmentSDK) -> None:
        response = client.system.appointments.with_raw_response.delete(
            trially_appointment_id="trially_appointment_id",
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        appointment = response.parse()
        assert appointment is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: WebRecruitmentSDK) -> None:
        with client.system.appointments.with_streaming_response.delete(
            trially_appointment_id="trially_appointment_id",
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            appointment = response.parse()
            assert appointment is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.appointments.with_raw_response.delete(
                trially_appointment_id="trially_appointment_id",
                tenant_db_name="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `trially_appointment_id` but received ''"
        ):
            client.system.appointments.with_raw_response.delete(
                trially_appointment_id="",
                tenant_db_name="tenant_db_name",
            )


class TestAsyncAppointments:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        appointment = await async_client.system.appointments.list(
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(AppointmentListResponse, appointment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        appointment = await async_client.system.appointments.list(
            tenant_db_name="tenant_db_name",
            limit=0,
        )
        assert_matches_type(AppointmentListResponse, appointment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.appointments.with_raw_response.list(
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        appointment = await response.parse()
        assert_matches_type(AppointmentListResponse, appointment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.appointments.with_streaming_response.list(
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            appointment = await response.parse()
            assert_matches_type(AppointmentListResponse, appointment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.appointments.with_raw_response.list(
                tenant_db_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        appointment = await async_client.system.appointments.delete(
            trially_appointment_id="trially_appointment_id",
            tenant_db_name="tenant_db_name",
        )
        assert appointment is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.appointments.with_raw_response.delete(
            trially_appointment_id="trially_appointment_id",
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        appointment = await response.parse()
        assert appointment is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.appointments.with_streaming_response.delete(
            trially_appointment_id="trially_appointment_id",
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            appointment = await response.parse()
            assert appointment is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.appointments.with_raw_response.delete(
                trially_appointment_id="trially_appointment_id",
                tenant_db_name="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `trially_appointment_id` but received ''"
        ):
            await async_client.system.appointments.with_raw_response.delete(
                trially_appointment_id="",
                tenant_db_name="tenant_db_name",
            )
