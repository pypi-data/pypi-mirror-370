# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestChat:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_stream(self, client: StudyfetchSDK) -> None:
        chat = client.v1.chat.stream()
        assert chat is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_stream_with_all_params(self, client: StudyfetchSDK) -> None:
        chat = client.v1.chat.stream(
            id="id",
            component_id="componentId",
            context={},
            group_ids=["string"],
            message={
                "images": [
                    {
                        "base64": "base64",
                        "caption": "caption",
                        "mime_type": "mimeType",
                        "url": "url",
                    }
                ],
                "text": "text",
            },
            messages=["string", "string", "string"],
            session_id="sessionId",
            user_id="userId",
            x_component_id="x-component-id",
        )
        assert chat is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_stream(self, client: StudyfetchSDK) -> None:
        response = client.v1.chat.with_raw_response.stream()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat = response.parse()
        assert chat is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_stream(self, client: StudyfetchSDK) -> None:
        with client.v1.chat.with_streaming_response.stream() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat = response.parse()
            assert chat is None

        assert cast(Any, response.is_closed) is True


class TestAsyncChat:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_stream(self, async_client: AsyncStudyfetchSDK) -> None:
        chat = await async_client.v1.chat.stream()
        assert chat is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_stream_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        chat = await async_client.v1.chat.stream(
            id="id",
            component_id="componentId",
            context={},
            group_ids=["string"],
            message={
                "images": [
                    {
                        "base64": "base64",
                        "caption": "caption",
                        "mime_type": "mimeType",
                        "url": "url",
                    }
                ],
                "text": "text",
            },
            messages=["string", "string", "string"],
            session_id="sessionId",
            user_id="userId",
            x_component_id="x-component-id",
        )
        assert chat is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_stream(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.chat.with_raw_response.stream()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat = await response.parse()
        assert chat is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_stream(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.chat.with_streaming_response.stream() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat = await response.parse()
            assert chat is None

        assert cast(Any, response.is_closed) is True
