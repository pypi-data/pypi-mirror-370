# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK
from studyfetch_sdk.types.v1 import (
    MaterialResponse,
    MaterialListResponse,
    MaterialSearchResponse,
    GeneratedMaterialResponse,
    MaterialGetDebugInfoResponse,
    MaterialGetDownloadURLResponse,
    MaterialCreateBatchUploadURLsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMaterials:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.create(
            content={"type": "text"},
            name="Chapter 1 - Introduction",
        )
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.create(
            content={
                "type": "text",
                "source_url": "sourceUrl",
                "text": "text",
                "url": "url",
            },
            name="Chapter 1 - Introduction",
            folder_id="folderId",
        )
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.with_raw_response.create(
            content={"type": "text"},
            name="Chapter 1 - Introduction",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = response.parse()
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.with_streaming_response.create(
            content={"type": "text"},
            name="Chapter 1 - Introduction",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = response.parse()
            assert_matches_type(MaterialResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.retrieve(
            "id",
        )
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = response.parse()
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = response.parse()
            assert_matches_type(MaterialResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.materials.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.list()
        assert_matches_type(MaterialListResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.list(
            folder_id="folderId",
            limit="limit",
            page="page",
            search="search",
        )
        assert_matches_type(MaterialListResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = response.parse()
        assert_matches_type(MaterialListResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = response.parse()
            assert_matches_type(MaterialListResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.delete(
            "id",
        )
        assert material is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = response.parse()
        assert material is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = response.parse()
            assert material is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.materials.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_and_process(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.create_and_process(
            content={"type": "text"},
            name="Chapter 1 - Introduction",
        )
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_and_process_with_all_params(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.create_and_process(
            content={
                "type": "text",
                "source_url": "sourceUrl",
                "text": "text",
                "url": "url",
            },
            name="Chapter 1 - Introduction",
            folder_id="folderId",
            poll_interval_ms=0,
            timeout_ms=0,
        )
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_and_process(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.with_raw_response.create_and_process(
            content={"type": "text"},
            name="Chapter 1 - Introduction",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = response.parse()
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_and_process(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.with_streaming_response.create_and_process(
            content={"type": "text"},
            name="Chapter 1 - Introduction",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = response.parse()
            assert_matches_type(MaterialResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_batch_upload_urls(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.create_batch_upload_urls(
            materials=[
                {
                    "content_type": "application/pdf",
                    "filename": "document.pdf",
                    "name": "Chapter 1",
                }
            ],
        )
        assert_matches_type(MaterialCreateBatchUploadURLsResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_batch_upload_urls(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.with_raw_response.create_batch_upload_urls(
            materials=[
                {
                    "content_type": "application/pdf",
                    "filename": "document.pdf",
                    "name": "Chapter 1",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = response.parse()
        assert_matches_type(MaterialCreateBatchUploadURLsResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_batch_upload_urls(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.with_streaming_response.create_batch_upload_urls(
            materials=[
                {
                    "content_type": "application/pdf",
                    "filename": "document.pdf",
                    "name": "Chapter 1",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = response.parse()
            assert_matches_type(MaterialCreateBatchUploadURLsResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.generate(
            name="Photosynthesis Study Plan",
            topic="Photosynthesis in plants",
            type="notes",
        )
        assert_matches_type(GeneratedMaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_with_all_params(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.generate(
            name="Photosynthesis Study Plan",
            topic="Photosynthesis in plants",
            type="notes",
            context="Focus on light-dependent and light-independent reactions",
            folder_id="folderId",
            length="short",
            level="college",
        )
        assert_matches_type(GeneratedMaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_generate(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.with_raw_response.generate(
            name="Photosynthesis Study Plan",
            topic="Photosynthesis in plants",
            type="notes",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = response.parse()
        assert_matches_type(GeneratedMaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_generate(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.with_streaming_response.generate(
            name="Photosynthesis Study Plan",
            topic="Photosynthesis in plants",
            type="notes",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = response.parse()
            assert_matches_type(GeneratedMaterialResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_and_process(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.generate_and_process(
            name="Photosynthesis Study Plan",
            topic="Photosynthesis in plants",
            type="notes",
        )
        assert_matches_type(GeneratedMaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_and_process_with_all_params(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.generate_and_process(
            name="Photosynthesis Study Plan",
            topic="Photosynthesis in plants",
            type="notes",
            context="Focus on light-dependent and light-independent reactions",
            folder_id="folderId",
            length="short",
            level="college",
            poll_interval_ms=0,
            timeout_ms=0,
        )
        assert_matches_type(GeneratedMaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_generate_and_process(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.with_raw_response.generate_and_process(
            name="Photosynthesis Study Plan",
            topic="Photosynthesis in plants",
            type="notes",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = response.parse()
        assert_matches_type(GeneratedMaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_generate_and_process(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.with_streaming_response.generate_and_process(
            name="Photosynthesis Study Plan",
            topic="Photosynthesis in plants",
            type="notes",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = response.parse()
            assert_matches_type(GeneratedMaterialResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_debug_info(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.get_debug_info(
            "id",
        )
        assert_matches_type(MaterialGetDebugInfoResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_debug_info(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.with_raw_response.get_debug_info(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = response.parse()
        assert_matches_type(MaterialGetDebugInfoResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_debug_info(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.with_streaming_response.get_debug_info(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = response.parse()
            assert_matches_type(MaterialGetDebugInfoResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_debug_info(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.materials.with_raw_response.get_debug_info(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_download_url(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.get_download_url(
            id="id",
        )
        assert_matches_type(MaterialGetDownloadURLResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_download_url_with_all_params(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.get_download_url(
            id="id",
            expires_in=0,
        )
        assert_matches_type(MaterialGetDownloadURLResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_download_url(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.with_raw_response.get_download_url(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = response.parse()
        assert_matches_type(MaterialGetDownloadURLResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_download_url(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.with_streaming_response.get_download_url(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = response.parse()
            assert_matches_type(MaterialGetDownloadURLResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_download_url(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.materials.with_raw_response.get_download_url(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_move(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.move(
            id="id",
            folder_id="folderId",
        )
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_move(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.with_raw_response.move(
            id="id",
            folder_id="folderId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = response.parse()
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_move(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.with_streaming_response.move(
            id="id",
            folder_id="folderId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = response.parse()
            assert_matches_type(MaterialResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_move(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.materials.with_raw_response.move(
                id="",
                folder_id="folderId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_rename(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.rename(
            id="id",
            name="New Material Name",
        )
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_rename(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.with_raw_response.rename(
            id="id",
            name="New Material Name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = response.parse()
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_rename(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.with_streaming_response.rename(
            id="id",
            name="New Material Name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = response.parse()
            assert_matches_type(MaterialResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_rename(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.materials.with_raw_response.rename(
                id="",
                name="New Material Name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reprocess(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.reprocess(
            "id",
        )
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_reprocess(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.with_raw_response.reprocess(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = response.parse()
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_reprocess(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.with_streaming_response.reprocess(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = response.parse()
            assert_matches_type(MaterialResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_reprocess(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.materials.with_raw_response.reprocess(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_search(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.search(
            query="What is photosynthesis?",
        )
        assert_matches_type(MaterialSearchResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_search_with_all_params(self, client: StudyfetchSDK) -> None:
        material = client.v1.materials.search(
            query="What is photosynthesis?",
            folder_ids=["string"],
            material_ids=["string"],
            top_k=0,
        )
        assert_matches_type(MaterialSearchResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_search(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.with_raw_response.search(
            query="What is photosynthesis?",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = response.parse()
        assert_matches_type(MaterialSearchResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_search(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.with_streaming_response.search(
            query="What is photosynthesis?",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = response.parse()
            assert_matches_type(MaterialSearchResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncMaterials:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.create(
            content={"type": "text"},
            name="Chapter 1 - Introduction",
        )
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.create(
            content={
                "type": "text",
                "source_url": "sourceUrl",
                "text": "text",
                "url": "url",
            },
            name="Chapter 1 - Introduction",
            folder_id="folderId",
        )
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.with_raw_response.create(
            content={"type": "text"},
            name="Chapter 1 - Introduction",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = await response.parse()
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.with_streaming_response.create(
            content={"type": "text"},
            name="Chapter 1 - Introduction",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = await response.parse()
            assert_matches_type(MaterialResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.retrieve(
            "id",
        )
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = await response.parse()
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = await response.parse()
            assert_matches_type(MaterialResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.materials.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.list()
        assert_matches_type(MaterialListResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.list(
            folder_id="folderId",
            limit="limit",
            page="page",
            search="search",
        )
        assert_matches_type(MaterialListResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = await response.parse()
        assert_matches_type(MaterialListResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = await response.parse()
            assert_matches_type(MaterialListResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.delete(
            "id",
        )
        assert material is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = await response.parse()
        assert material is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = await response.parse()
            assert material is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.materials.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_and_process(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.create_and_process(
            content={"type": "text"},
            name="Chapter 1 - Introduction",
        )
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_and_process_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.create_and_process(
            content={
                "type": "text",
                "source_url": "sourceUrl",
                "text": "text",
                "url": "url",
            },
            name="Chapter 1 - Introduction",
            folder_id="folderId",
            poll_interval_ms=0,
            timeout_ms=0,
        )
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_and_process(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.with_raw_response.create_and_process(
            content={"type": "text"},
            name="Chapter 1 - Introduction",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = await response.parse()
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_and_process(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.with_streaming_response.create_and_process(
            content={"type": "text"},
            name="Chapter 1 - Introduction",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = await response.parse()
            assert_matches_type(MaterialResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_batch_upload_urls(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.create_batch_upload_urls(
            materials=[
                {
                    "content_type": "application/pdf",
                    "filename": "document.pdf",
                    "name": "Chapter 1",
                }
            ],
        )
        assert_matches_type(MaterialCreateBatchUploadURLsResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_batch_upload_urls(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.with_raw_response.create_batch_upload_urls(
            materials=[
                {
                    "content_type": "application/pdf",
                    "filename": "document.pdf",
                    "name": "Chapter 1",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = await response.parse()
        assert_matches_type(MaterialCreateBatchUploadURLsResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_batch_upload_urls(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.with_streaming_response.create_batch_upload_urls(
            materials=[
                {
                    "content_type": "application/pdf",
                    "filename": "document.pdf",
                    "name": "Chapter 1",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = await response.parse()
            assert_matches_type(MaterialCreateBatchUploadURLsResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.generate(
            name="Photosynthesis Study Plan",
            topic="Photosynthesis in plants",
            type="notes",
        )
        assert_matches_type(GeneratedMaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.generate(
            name="Photosynthesis Study Plan",
            topic="Photosynthesis in plants",
            type="notes",
            context="Focus on light-dependent and light-independent reactions",
            folder_id="folderId",
            length="short",
            level="college",
        )
        assert_matches_type(GeneratedMaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_generate(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.with_raw_response.generate(
            name="Photosynthesis Study Plan",
            topic="Photosynthesis in plants",
            type="notes",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = await response.parse()
        assert_matches_type(GeneratedMaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_generate(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.with_streaming_response.generate(
            name="Photosynthesis Study Plan",
            topic="Photosynthesis in plants",
            type="notes",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = await response.parse()
            assert_matches_type(GeneratedMaterialResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_and_process(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.generate_and_process(
            name="Photosynthesis Study Plan",
            topic="Photosynthesis in plants",
            type="notes",
        )
        assert_matches_type(GeneratedMaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_and_process_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.generate_and_process(
            name="Photosynthesis Study Plan",
            topic="Photosynthesis in plants",
            type="notes",
            context="Focus on light-dependent and light-independent reactions",
            folder_id="folderId",
            length="short",
            level="college",
            poll_interval_ms=0,
            timeout_ms=0,
        )
        assert_matches_type(GeneratedMaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_generate_and_process(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.with_raw_response.generate_and_process(
            name="Photosynthesis Study Plan",
            topic="Photosynthesis in plants",
            type="notes",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = await response.parse()
        assert_matches_type(GeneratedMaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_generate_and_process(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.with_streaming_response.generate_and_process(
            name="Photosynthesis Study Plan",
            topic="Photosynthesis in plants",
            type="notes",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = await response.parse()
            assert_matches_type(GeneratedMaterialResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_debug_info(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.get_debug_info(
            "id",
        )
        assert_matches_type(MaterialGetDebugInfoResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_debug_info(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.with_raw_response.get_debug_info(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = await response.parse()
        assert_matches_type(MaterialGetDebugInfoResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_debug_info(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.with_streaming_response.get_debug_info(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = await response.parse()
            assert_matches_type(MaterialGetDebugInfoResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_debug_info(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.materials.with_raw_response.get_debug_info(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_download_url(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.get_download_url(
            id="id",
        )
        assert_matches_type(MaterialGetDownloadURLResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_download_url_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.get_download_url(
            id="id",
            expires_in=0,
        )
        assert_matches_type(MaterialGetDownloadURLResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_download_url(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.with_raw_response.get_download_url(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = await response.parse()
        assert_matches_type(MaterialGetDownloadURLResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_download_url(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.with_streaming_response.get_download_url(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = await response.parse()
            assert_matches_type(MaterialGetDownloadURLResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_download_url(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.materials.with_raw_response.get_download_url(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_move(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.move(
            id="id",
            folder_id="folderId",
        )
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_move(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.with_raw_response.move(
            id="id",
            folder_id="folderId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = await response.parse()
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_move(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.with_streaming_response.move(
            id="id",
            folder_id="folderId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = await response.parse()
            assert_matches_type(MaterialResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_move(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.materials.with_raw_response.move(
                id="",
                folder_id="folderId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_rename(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.rename(
            id="id",
            name="New Material Name",
        )
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_rename(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.with_raw_response.rename(
            id="id",
            name="New Material Name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = await response.parse()
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_rename(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.with_streaming_response.rename(
            id="id",
            name="New Material Name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = await response.parse()
            assert_matches_type(MaterialResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_rename(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.materials.with_raw_response.rename(
                id="",
                name="New Material Name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reprocess(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.reprocess(
            "id",
        )
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_reprocess(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.with_raw_response.reprocess(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = await response.parse()
        assert_matches_type(MaterialResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_reprocess(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.with_streaming_response.reprocess(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = await response.parse()
            assert_matches_type(MaterialResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_reprocess(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.materials.with_raw_response.reprocess(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_search(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.search(
            query="What is photosynthesis?",
        )
        assert_matches_type(MaterialSearchResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_search_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        material = await async_client.v1.materials.search(
            query="What is photosynthesis?",
            folder_ids=["string"],
            material_ids=["string"],
            top_k=0,
        )
        assert_matches_type(MaterialSearchResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_search(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.with_raw_response.search(
            query="What is photosynthesis?",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        material = await response.parse()
        assert_matches_type(MaterialSearchResponse, material, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.with_streaming_response.search(
            query="What is photosynthesis?",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            material = await response.parse()
            assert_matches_type(MaterialSearchResponse, material, path=["response"])

        assert cast(Any, response.is_closed) is True
