# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK
from studyfetch_sdk.types.v1.materials import (
    TestTestOcrResponse,
    TestTestEpubProcessingResponse,
    TestTestImageProcessingResponse,
    TestTestVideoProcessingResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTest:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_test_epub_processing(self, client: StudyfetchSDK) -> None:
        test = client.v1.materials.test.test_epub_processing()
        assert_matches_type(TestTestEpubProcessingResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_test_epub_processing(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.test.with_raw_response.test_epub_processing()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert_matches_type(TestTestEpubProcessingResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_test_epub_processing(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.test.with_streaming_response.test_epub_processing() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert_matches_type(TestTestEpubProcessingResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_test_image_processing(self, client: StudyfetchSDK) -> None:
        test = client.v1.materials.test.test_image_processing()
        assert_matches_type(TestTestImageProcessingResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_test_image_processing(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.test.with_raw_response.test_image_processing()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert_matches_type(TestTestImageProcessingResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_test_image_processing(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.test.with_streaming_response.test_image_processing() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert_matches_type(TestTestImageProcessingResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_test_ocr(self, client: StudyfetchSDK) -> None:
        test = client.v1.materials.test.test_ocr()
        assert_matches_type(TestTestOcrResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_test_ocr(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.test.with_raw_response.test_ocr()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert_matches_type(TestTestOcrResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_test_ocr(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.test.with_streaming_response.test_ocr() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert_matches_type(TestTestOcrResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_test_video_processing(self, client: StudyfetchSDK) -> None:
        test = client.v1.materials.test.test_video_processing()
        assert_matches_type(TestTestVideoProcessingResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_test_video_processing(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.test.with_raw_response.test_video_processing()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert_matches_type(TestTestVideoProcessingResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_test_video_processing(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.test.with_streaming_response.test_video_processing() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert_matches_type(TestTestVideoProcessingResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTest:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_test_epub_processing(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.materials.test.test_epub_processing()
        assert_matches_type(TestTestEpubProcessingResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_test_epub_processing(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.test.with_raw_response.test_epub_processing()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert_matches_type(TestTestEpubProcessingResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_test_epub_processing(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.test.with_streaming_response.test_epub_processing() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert_matches_type(TestTestEpubProcessingResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_test_image_processing(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.materials.test.test_image_processing()
        assert_matches_type(TestTestImageProcessingResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_test_image_processing(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.test.with_raw_response.test_image_processing()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert_matches_type(TestTestImageProcessingResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_test_image_processing(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.test.with_streaming_response.test_image_processing() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert_matches_type(TestTestImageProcessingResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_test_ocr(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.materials.test.test_ocr()
        assert_matches_type(TestTestOcrResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_test_ocr(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.test.with_raw_response.test_ocr()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert_matches_type(TestTestOcrResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_test_ocr(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.test.with_streaming_response.test_ocr() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert_matches_type(TestTestOcrResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_test_video_processing(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.materials.test.test_video_processing()
        assert_matches_type(TestTestVideoProcessingResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_test_video_processing(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.test.with_raw_response.test_video_processing()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert_matches_type(TestTestVideoProcessingResponse, test, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_test_video_processing(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.test.with_streaming_response.test_video_processing() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert_matches_type(TestTestVideoProcessingResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True
