# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEmbed:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_theme(self, client: StudyfetchSDK) -> None:
        embed = client.v1.embed.get_theme(
            token="token",
        )
        assert embed is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_theme(self, client: StudyfetchSDK) -> None:
        response = client.v1.embed.with_raw_response.get_theme(
            token="token",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        embed = response.parse()
        assert embed is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_theme(self, client: StudyfetchSDK) -> None:
        with client.v1.embed.with_streaming_response.get_theme(
            token="token",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            embed = response.parse()
            assert embed is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_health_check(self, client: StudyfetchSDK) -> None:
        embed = client.v1.embed.health_check()
        assert embed is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_health_check(self, client: StudyfetchSDK) -> None:
        response = client.v1.embed.with_raw_response.health_check()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        embed = response.parse()
        assert embed is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_health_check(self, client: StudyfetchSDK) -> None:
        with client.v1.embed.with_streaming_response.health_check() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            embed = response.parse()
            assert embed is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_verify(self, client: StudyfetchSDK) -> None:
        embed = client.v1.embed.verify(
            token="token",
        )
        assert embed is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_verify(self, client: StudyfetchSDK) -> None:
        response = client.v1.embed.with_raw_response.verify(
            token="token",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        embed = response.parse()
        assert embed is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_verify(self, client: StudyfetchSDK) -> None:
        with client.v1.embed.with_streaming_response.verify(
            token="token",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            embed = response.parse()
            assert embed is None

        assert cast(Any, response.is_closed) is True


class TestAsyncEmbed:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_theme(self, async_client: AsyncStudyfetchSDK) -> None:
        embed = await async_client.v1.embed.get_theme(
            token="token",
        )
        assert embed is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_theme(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.embed.with_raw_response.get_theme(
            token="token",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        embed = await response.parse()
        assert embed is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_theme(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.embed.with_streaming_response.get_theme(
            token="token",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            embed = await response.parse()
            assert embed is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_health_check(self, async_client: AsyncStudyfetchSDK) -> None:
        embed = await async_client.v1.embed.health_check()
        assert embed is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_health_check(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.embed.with_raw_response.health_check()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        embed = await response.parse()
        assert embed is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_health_check(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.embed.with_streaming_response.health_check() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            embed = await response.parse()
            assert embed is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_verify(self, async_client: AsyncStudyfetchSDK) -> None:
        embed = await async_client.v1.embed.verify(
            token="token",
        )
        assert embed is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_verify(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.embed.with_raw_response.verify(
            token="token",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        embed = await response.parse()
        assert embed is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_verify(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.embed.with_streaming_response.verify(
            token="token",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            embed = await response.parse()
            assert embed is None

        assert cast(Any, response.is_closed) is True
