# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK
from studyfetch_sdk.types.v1 import MaterialResponse
from studyfetch_sdk.types.v1.materials import (
    UploadGetPresignedURLResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUpload:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_complete_upload(self, client: StudyfetchSDK) -> None:
        upload = client.v1.materials.upload.complete_upload(
            material_id="materialId",
            s3_key="s3Key",
        )
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_complete_upload(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.upload.with_raw_response.complete_upload(
            material_id="materialId",
            s3_key="s3Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_complete_upload(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.upload.with_streaming_response.complete_upload(
            material_id="materialId",
            s3_key="s3Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = response.parse()
            assert_matches_type(MaterialResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_presigned_url(self, client: StudyfetchSDK) -> None:
        upload = client.v1.materials.upload.get_presigned_url(
            content_type="application/pdf",
            filename="document.pdf",
            name="Chapter 1 Notes",
        )
        assert_matches_type(UploadGetPresignedURLResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_presigned_url_with_all_params(self, client: StudyfetchSDK) -> None:
        upload = client.v1.materials.upload.get_presigned_url(
            content_type="application/pdf",
            filename="document.pdf",
            name="Chapter 1 Notes",
            extract_images=True,
            folder_id="folderId",
        )
        assert_matches_type(UploadGetPresignedURLResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_presigned_url(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.upload.with_raw_response.get_presigned_url(
            content_type="application/pdf",
            filename="document.pdf",
            name="Chapter 1 Notes",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(UploadGetPresignedURLResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_presigned_url(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.upload.with_streaming_response.get_presigned_url(
            content_type="application/pdf",
            filename="document.pdf",
            name="Chapter 1 Notes",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = response.parse()
            assert_matches_type(UploadGetPresignedURLResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload_file(self, client: StudyfetchSDK) -> None:
        upload = client.v1.materials.upload.upload_file(
            file=b"raw file contents",
            name="name",
        )
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload_file_with_all_params(self, client: StudyfetchSDK) -> None:
        upload = client.v1.materials.upload.upload_file(
            file=b"raw file contents",
            name="name",
            extract_images="extractImages",
            folder_id="folderId",
        )
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_upload_file(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.upload.with_raw_response.upload_file(
            file=b"raw file contents",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_upload_file(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.upload.with_streaming_response.upload_file(
            file=b"raw file contents",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = response.parse()
            assert_matches_type(MaterialResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload_file_and_process(self, client: StudyfetchSDK) -> None:
        upload = client.v1.materials.upload.upload_file_and_process(
            file=b"raw file contents",
            name="name",
        )
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload_file_and_process_with_all_params(self, client: StudyfetchSDK) -> None:
        upload = client.v1.materials.upload.upload_file_and_process(
            file=b"raw file contents",
            name="name",
            extract_images="extractImages",
            folder_id="folderId",
            poll_interval_ms=0,
            timeout_ms=0,
        )
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_upload_file_and_process(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.upload.with_raw_response.upload_file_and_process(
            file=b"raw file contents",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_upload_file_and_process(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.upload.with_streaming_response.upload_file_and_process(
            file=b"raw file contents",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = response.parse()
            assert_matches_type(MaterialResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload_from_url(self, client: StudyfetchSDK) -> None:
        upload = client.v1.materials.upload.upload_from_url(
            name="name",
            url="url",
        )
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload_from_url_with_all_params(self, client: StudyfetchSDK) -> None:
        upload = client.v1.materials.upload.upload_from_url(
            name="name",
            url="url",
            folder_id="folderId",
        )
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_upload_from_url(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.upload.with_raw_response.upload_from_url(
            name="name",
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_upload_from_url(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.upload.with_streaming_response.upload_from_url(
            name="name",
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = response.parse()
            assert_matches_type(MaterialResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload_from_url_and_process(self, client: StudyfetchSDK) -> None:
        upload = client.v1.materials.upload.upload_from_url_and_process(
            name="My Document",
            url="https://example.com/document.pdf",
        )
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload_from_url_and_process_with_all_params(self, client: StudyfetchSDK) -> None:
        upload = client.v1.materials.upload.upload_from_url_and_process(
            name="My Document",
            url="https://example.com/document.pdf",
            folder_id="folderId",
            poll_interval_ms=0,
            timeout_ms=0,
        )
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_upload_from_url_and_process(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.upload.with_raw_response.upload_from_url_and_process(
            name="My Document",
            url="https://example.com/document.pdf",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_upload_from_url_and_process(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.upload.with_streaming_response.upload_from_url_and_process(
            name="My Document",
            url="https://example.com/document.pdf",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = response.parse()
            assert_matches_type(MaterialResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncUpload:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_complete_upload(self, async_client: AsyncStudyfetchSDK) -> None:
        upload = await async_client.v1.materials.upload.complete_upload(
            material_id="materialId",
            s3_key="s3Key",
        )
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_complete_upload(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.upload.with_raw_response.complete_upload(
            material_id="materialId",
            s3_key="s3Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = await response.parse()
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_complete_upload(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.upload.with_streaming_response.complete_upload(
            material_id="materialId",
            s3_key="s3Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = await response.parse()
            assert_matches_type(MaterialResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_presigned_url(self, async_client: AsyncStudyfetchSDK) -> None:
        upload = await async_client.v1.materials.upload.get_presigned_url(
            content_type="application/pdf",
            filename="document.pdf",
            name="Chapter 1 Notes",
        )
        assert_matches_type(UploadGetPresignedURLResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_presigned_url_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        upload = await async_client.v1.materials.upload.get_presigned_url(
            content_type="application/pdf",
            filename="document.pdf",
            name="Chapter 1 Notes",
            extract_images=True,
            folder_id="folderId",
        )
        assert_matches_type(UploadGetPresignedURLResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_presigned_url(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.upload.with_raw_response.get_presigned_url(
            content_type="application/pdf",
            filename="document.pdf",
            name="Chapter 1 Notes",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = await response.parse()
        assert_matches_type(UploadGetPresignedURLResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_presigned_url(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.upload.with_streaming_response.get_presigned_url(
            content_type="application/pdf",
            filename="document.pdf",
            name="Chapter 1 Notes",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = await response.parse()
            assert_matches_type(UploadGetPresignedURLResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload_file(self, async_client: AsyncStudyfetchSDK) -> None:
        upload = await async_client.v1.materials.upload.upload_file(
            file=b"raw file contents",
            name="name",
        )
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload_file_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        upload = await async_client.v1.materials.upload.upload_file(
            file=b"raw file contents",
            name="name",
            extract_images="extractImages",
            folder_id="folderId",
        )
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_upload_file(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.upload.with_raw_response.upload_file(
            file=b"raw file contents",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = await response.parse()
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_upload_file(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.upload.with_streaming_response.upload_file(
            file=b"raw file contents",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = await response.parse()
            assert_matches_type(MaterialResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload_file_and_process(self, async_client: AsyncStudyfetchSDK) -> None:
        upload = await async_client.v1.materials.upload.upload_file_and_process(
            file=b"raw file contents",
            name="name",
        )
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload_file_and_process_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        upload = await async_client.v1.materials.upload.upload_file_and_process(
            file=b"raw file contents",
            name="name",
            extract_images="extractImages",
            folder_id="folderId",
            poll_interval_ms=0,
            timeout_ms=0,
        )
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_upload_file_and_process(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.upload.with_raw_response.upload_file_and_process(
            file=b"raw file contents",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = await response.parse()
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_upload_file_and_process(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.upload.with_streaming_response.upload_file_and_process(
            file=b"raw file contents",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = await response.parse()
            assert_matches_type(MaterialResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload_from_url(self, async_client: AsyncStudyfetchSDK) -> None:
        upload = await async_client.v1.materials.upload.upload_from_url(
            name="name",
            url="url",
        )
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload_from_url_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        upload = await async_client.v1.materials.upload.upload_from_url(
            name="name",
            url="url",
            folder_id="folderId",
        )
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_upload_from_url(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.upload.with_raw_response.upload_from_url(
            name="name",
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = await response.parse()
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_upload_from_url(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.upload.with_streaming_response.upload_from_url(
            name="name",
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = await response.parse()
            assert_matches_type(MaterialResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload_from_url_and_process(self, async_client: AsyncStudyfetchSDK) -> None:
        upload = await async_client.v1.materials.upload.upload_from_url_and_process(
            name="My Document",
            url="https://example.com/document.pdf",
        )
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload_from_url_and_process_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        upload = await async_client.v1.materials.upload.upload_from_url_and_process(
            name="My Document",
            url="https://example.com/document.pdf",
            folder_id="folderId",
            poll_interval_ms=0,
            timeout_ms=0,
        )
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_upload_from_url_and_process(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.upload.with_raw_response.upload_from_url_and_process(
            name="My Document",
            url="https://example.com/document.pdf",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = await response.parse()
        assert_matches_type(MaterialResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_upload_from_url_and_process(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.upload.with_streaming_response.upload_from_url_and_process(
            name="My Document",
            url="https://example.com/document.pdf",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = await response.parse()
            assert_matches_type(MaterialResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True
