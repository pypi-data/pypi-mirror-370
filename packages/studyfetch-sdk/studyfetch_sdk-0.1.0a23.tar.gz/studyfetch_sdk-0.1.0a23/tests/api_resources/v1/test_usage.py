# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUsage:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_stats(self, client: StudyfetchSDK) -> None:
        usage = client.v1.usage.get_stats()
        assert usage is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_stats_with_all_params(self, client: StudyfetchSDK) -> None:
        usage = client.v1.usage.get_stats(
            end_date="endDate",
            group_id="groupId",
            start_date="startDate",
            user_id="userId",
        )
        assert usage is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_stats(self, client: StudyfetchSDK) -> None:
        response = client.v1.usage.with_raw_response.get_stats()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        usage = response.parse()
        assert usage is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_stats(self, client: StudyfetchSDK) -> None:
        with client.v1.usage.with_streaming_response.get_stats() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            usage = response.parse()
            assert usage is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_summary(self, client: StudyfetchSDK) -> None:
        usage = client.v1.usage.get_summary(
            end_date="endDate",
            period="hourly",
            start_date="startDate",
        )
        assert usage is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_summary_with_all_params(self, client: StudyfetchSDK) -> None:
        usage = client.v1.usage.get_summary(
            end_date="endDate",
            period="hourly",
            start_date="startDate",
            group_by="user",
        )
        assert usage is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_summary(self, client: StudyfetchSDK) -> None:
        response = client.v1.usage.with_raw_response.get_summary(
            end_date="endDate",
            period="hourly",
            start_date="startDate",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        usage = response.parse()
        assert usage is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_summary(self, client: StudyfetchSDK) -> None:
        with client.v1.usage.with_streaming_response.get_summary(
            end_date="endDate",
            period="hourly",
            start_date="startDate",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            usage = response.parse()
            assert usage is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_events(self, client: StudyfetchSDK) -> None:
        usage = client.v1.usage.list_events()
        assert usage is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_events_with_all_params(self, client: StudyfetchSDK) -> None:
        usage = client.v1.usage.list_events(
            end_date="endDate",
            event_type="material_created",
            group_id="groupId",
            limit=1,
            offset=0,
            resource_id="resourceId",
            start_date="startDate",
            user_id="userId",
        )
        assert usage is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_events(self, client: StudyfetchSDK) -> None:
        response = client.v1.usage.with_raw_response.list_events()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        usage = response.parse()
        assert usage is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_events(self, client: StudyfetchSDK) -> None:
        with client.v1.usage.with_streaming_response.list_events() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            usage = response.parse()
            assert usage is None

        assert cast(Any, response.is_closed) is True


class TestAsyncUsage:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_stats(self, async_client: AsyncStudyfetchSDK) -> None:
        usage = await async_client.v1.usage.get_stats()
        assert usage is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_stats_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        usage = await async_client.v1.usage.get_stats(
            end_date="endDate",
            group_id="groupId",
            start_date="startDate",
            user_id="userId",
        )
        assert usage is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_stats(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.usage.with_raw_response.get_stats()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        usage = await response.parse()
        assert usage is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_stats(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.usage.with_streaming_response.get_stats() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            usage = await response.parse()
            assert usage is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_summary(self, async_client: AsyncStudyfetchSDK) -> None:
        usage = await async_client.v1.usage.get_summary(
            end_date="endDate",
            period="hourly",
            start_date="startDate",
        )
        assert usage is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_summary_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        usage = await async_client.v1.usage.get_summary(
            end_date="endDate",
            period="hourly",
            start_date="startDate",
            group_by="user",
        )
        assert usage is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_summary(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.usage.with_raw_response.get_summary(
            end_date="endDate",
            period="hourly",
            start_date="startDate",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        usage = await response.parse()
        assert usage is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_summary(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.usage.with_streaming_response.get_summary(
            end_date="endDate",
            period="hourly",
            start_date="startDate",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            usage = await response.parse()
            assert usage is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_events(self, async_client: AsyncStudyfetchSDK) -> None:
        usage = await async_client.v1.usage.list_events()
        assert usage is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_events_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        usage = await async_client.v1.usage.list_events(
            end_date="endDate",
            event_type="material_created",
            group_id="groupId",
            limit=1,
            offset=0,
            resource_id="resourceId",
            start_date="startDate",
            user_id="userId",
        )
        assert usage is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_events(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.usage.with_raw_response.list_events()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        usage = await response.parse()
        assert usage is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_events(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.usage.with_streaming_response.list_events() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            usage = await response.parse()
            assert usage is None

        assert cast(Any, response.is_closed) is True
