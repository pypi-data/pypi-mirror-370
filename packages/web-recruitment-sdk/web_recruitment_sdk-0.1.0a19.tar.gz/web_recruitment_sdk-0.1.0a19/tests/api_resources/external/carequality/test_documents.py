# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.external.carequality import (
    DocumentGenerateUploadURLResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDocuments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_upload_url(self, client: WebRecruitmentSDK) -> None:
        document = client.external.carequality.documents.generate_upload_url(
            carequality_patient_id="carequalityPatientId",
            content_type="contentType",
            file_md5_hash="2e/xAv1b/zE+/N+eC1+0f+==",
            file_name="fileName",
            file_size_bytes=1,
            x_api_key="X-API-Key",
        )
        assert_matches_type(DocumentGenerateUploadURLResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_generate_upload_url(self, client: WebRecruitmentSDK) -> None:
        response = client.external.carequality.documents.with_raw_response.generate_upload_url(
            carequality_patient_id="carequalityPatientId",
            content_type="contentType",
            file_md5_hash="2e/xAv1b/zE+/N+eC1+0f+==",
            file_name="fileName",
            file_size_bytes=1,
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentGenerateUploadURLResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_generate_upload_url(self, client: WebRecruitmentSDK) -> None:
        with client.external.carequality.documents.with_streaming_response.generate_upload_url(
            carequality_patient_id="carequalityPatientId",
            content_type="contentType",
            file_md5_hash="2e/xAv1b/zE+/N+eC1+0f+==",
            file_name="fileName",
            file_size_bytes=1,
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentGenerateUploadURLResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDocuments:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_upload_url(self, async_client: AsyncWebRecruitmentSDK) -> None:
        document = await async_client.external.carequality.documents.generate_upload_url(
            carequality_patient_id="carequalityPatientId",
            content_type="contentType",
            file_md5_hash="2e/xAv1b/zE+/N+eC1+0f+==",
            file_name="fileName",
            file_size_bytes=1,
            x_api_key="X-API-Key",
        )
        assert_matches_type(DocumentGenerateUploadURLResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_generate_upload_url(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.external.carequality.documents.with_raw_response.generate_upload_url(
            carequality_patient_id="carequalityPatientId",
            content_type="contentType",
            file_md5_hash="2e/xAv1b/zE+/N+eC1+0f+==",
            file_name="fileName",
            file_size_bytes=1,
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentGenerateUploadURLResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_generate_upload_url(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.external.carequality.documents.with_streaming_response.generate_upload_url(
            carequality_patient_id="carequalityPatientId",
            content_type="contentType",
            file_md5_hash="2e/xAv1b/zE+/N+eC1+0f+==",
            file_name="fileName",
            file_size_bytes=1,
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentGenerateUploadURLResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True
