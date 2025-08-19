# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK
from studyfetch_sdk.types.v1 import (
    UsageAnalystListChatMessagesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUsageAnalyst:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_test_questions(self, client: StudyfetchSDK) -> None:
        usage_analyst = client.v1.usage_analyst.get_test_questions()
        assert usage_analyst is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_test_questions_with_all_params(self, client: StudyfetchSDK) -> None:
        usage_analyst = client.v1.usage_analyst.get_test_questions(
            group_ids=["class-101", "class-102"],
            user_id="userId",
        )
        assert usage_analyst is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_test_questions(self, client: StudyfetchSDK) -> None:
        response = client.v1.usage_analyst.with_raw_response.get_test_questions()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        usage_analyst = response.parse()
        assert usage_analyst is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_test_questions(self, client: StudyfetchSDK) -> None:
        with client.v1.usage_analyst.with_streaming_response.get_test_questions() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            usage_analyst = response.parse()
            assert usage_analyst is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_chat_messages(self, client: StudyfetchSDK) -> None:
        usage_analyst = client.v1.usage_analyst.list_chat_messages()
        assert_matches_type(UsageAnalystListChatMessagesResponse, usage_analyst, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_chat_messages_with_all_params(self, client: StudyfetchSDK) -> None:
        usage_analyst = client.v1.usage_analyst.list_chat_messages(
            group_ids=["class-101", "class-102"],
            user_id="userId",
        )
        assert_matches_type(UsageAnalystListChatMessagesResponse, usage_analyst, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_chat_messages(self, client: StudyfetchSDK) -> None:
        response = client.v1.usage_analyst.with_raw_response.list_chat_messages()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        usage_analyst = response.parse()
        assert_matches_type(UsageAnalystListChatMessagesResponse, usage_analyst, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_chat_messages(self, client: StudyfetchSDK) -> None:
        with client.v1.usage_analyst.with_streaming_response.list_chat_messages() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            usage_analyst = response.parse()
            assert_matches_type(UsageAnalystListChatMessagesResponse, usage_analyst, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_events(self, client: StudyfetchSDK) -> None:
        usage_analyst = client.v1.usage_analyst.list_events(
            end_date="endDate",
            event_type="material_created",
            start_date="startDate",
        )
        assert usage_analyst is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_events_with_all_params(self, client: StudyfetchSDK) -> None:
        usage_analyst = client.v1.usage_analyst.list_events(
            end_date="endDate",
            event_type="material_created",
            start_date="startDate",
            group_ids=["class-101", "class-102"],
            user_ids=["user123", "user456"],
        )
        assert usage_analyst is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_events(self, client: StudyfetchSDK) -> None:
        response = client.v1.usage_analyst.with_raw_response.list_events(
            end_date="endDate",
            event_type="material_created",
            start_date="startDate",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        usage_analyst = response.parse()
        assert usage_analyst is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_events(self, client: StudyfetchSDK) -> None:
        with client.v1.usage_analyst.with_streaming_response.list_events(
            end_date="endDate",
            event_type="material_created",
            start_date="startDate",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            usage_analyst = response.parse()
            assert usage_analyst is None

        assert cast(Any, response.is_closed) is True


class TestAsyncUsageAnalyst:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_test_questions(self, async_client: AsyncStudyfetchSDK) -> None:
        usage_analyst = await async_client.v1.usage_analyst.get_test_questions()
        assert usage_analyst is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_test_questions_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        usage_analyst = await async_client.v1.usage_analyst.get_test_questions(
            group_ids=["class-101", "class-102"],
            user_id="userId",
        )
        assert usage_analyst is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_test_questions(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.usage_analyst.with_raw_response.get_test_questions()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        usage_analyst = await response.parse()
        assert usage_analyst is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_test_questions(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.usage_analyst.with_streaming_response.get_test_questions() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            usage_analyst = await response.parse()
            assert usage_analyst is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_chat_messages(self, async_client: AsyncStudyfetchSDK) -> None:
        usage_analyst = await async_client.v1.usage_analyst.list_chat_messages()
        assert_matches_type(UsageAnalystListChatMessagesResponse, usage_analyst, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_chat_messages_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        usage_analyst = await async_client.v1.usage_analyst.list_chat_messages(
            group_ids=["class-101", "class-102"],
            user_id="userId",
        )
        assert_matches_type(UsageAnalystListChatMessagesResponse, usage_analyst, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_chat_messages(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.usage_analyst.with_raw_response.list_chat_messages()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        usage_analyst = await response.parse()
        assert_matches_type(UsageAnalystListChatMessagesResponse, usage_analyst, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_chat_messages(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.usage_analyst.with_streaming_response.list_chat_messages() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            usage_analyst = await response.parse()
            assert_matches_type(UsageAnalystListChatMessagesResponse, usage_analyst, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_events(self, async_client: AsyncStudyfetchSDK) -> None:
        usage_analyst = await async_client.v1.usage_analyst.list_events(
            end_date="endDate",
            event_type="material_created",
            start_date="startDate",
        )
        assert usage_analyst is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_events_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        usage_analyst = await async_client.v1.usage_analyst.list_events(
            end_date="endDate",
            event_type="material_created",
            start_date="startDate",
            group_ids=["class-101", "class-102"],
            user_ids=["user123", "user456"],
        )
        assert usage_analyst is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_events(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.usage_analyst.with_raw_response.list_events(
            end_date="endDate",
            event_type="material_created",
            start_date="startDate",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        usage_analyst = await response.parse()
        assert usage_analyst is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_events(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.usage_analyst.with_streaming_response.list_events(
            end_date="endDate",
            event_type="material_created",
            start_date="startDate",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            usage_analyst = await response.parse()
            assert usage_analyst is None

        assert cast(Any, response.is_closed) is True
