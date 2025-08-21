# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK
from studyfetch_sdk._utils import parse_datetime
from studyfetch_sdk.types.v1 import (
    ChatAnalyticsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestChatAnalytics:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_analyze(self, client: StudyfetchSDK) -> None:
        chat_analytic = client.v1.chat_analytics.analyze()
        assert_matches_type(ChatAnalyticsResponse, chat_analytic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_analyze_with_all_params(self, client: StudyfetchSDK) -> None:
        chat_analytic = client.v1.chat_analytics.analyze(
            component_id="componentId",
            end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            group_ids=["string"],
            model_key="gpt-4o-mini",
            organization_id="organizationId",
            start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            user_id="userId",
        )
        assert_matches_type(ChatAnalyticsResponse, chat_analytic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_analyze(self, client: StudyfetchSDK) -> None:
        response = client.v1.chat_analytics.with_raw_response.analyze()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat_analytic = response.parse()
        assert_matches_type(ChatAnalyticsResponse, chat_analytic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_analyze(self, client: StudyfetchSDK) -> None:
        with client.v1.chat_analytics.with_streaming_response.analyze() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat_analytic = response.parse()
            assert_matches_type(ChatAnalyticsResponse, chat_analytic, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_export(self, client: StudyfetchSDK) -> None:
        chat_analytic = client.v1.chat_analytics.export()
        assert_matches_type(str, chat_analytic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_export_with_all_params(self, client: StudyfetchSDK) -> None:
        chat_analytic = client.v1.chat_analytics.export(
            component_id="componentId",
            end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            group_ids=["string"],
            model_key="gpt-4o-mini",
            organization_id="organizationId",
            start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            user_id="userId",
        )
        assert_matches_type(str, chat_analytic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_export(self, client: StudyfetchSDK) -> None:
        response = client.v1.chat_analytics.with_raw_response.export()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat_analytic = response.parse()
        assert_matches_type(str, chat_analytic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_export(self, client: StudyfetchSDK) -> None:
        with client.v1.chat_analytics.with_streaming_response.export() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat_analytic = response.parse()
            assert_matches_type(str, chat_analytic, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_component(self, client: StudyfetchSDK) -> None:
        chat_analytic = client.v1.chat_analytics.get_component(
            component_id="componentId",
        )
        assert_matches_type(ChatAnalyticsResponse, chat_analytic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_component_with_all_params(self, client: StudyfetchSDK) -> None:
        chat_analytic = client.v1.chat_analytics.get_component(
            component_id="componentId",
            end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            group_ids=["string"],
            model_key="gpt-4o-mini",
            organization_id="organizationId",
            start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            user_id="userId",
        )
        assert_matches_type(ChatAnalyticsResponse, chat_analytic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_component(self, client: StudyfetchSDK) -> None:
        response = client.v1.chat_analytics.with_raw_response.get_component(
            component_id="componentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat_analytic = response.parse()
        assert_matches_type(ChatAnalyticsResponse, chat_analytic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_component(self, client: StudyfetchSDK) -> None:
        with client.v1.chat_analytics.with_streaming_response.get_component(
            component_id="componentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat_analytic = response.parse()
            assert_matches_type(ChatAnalyticsResponse, chat_analytic, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_component(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            client.v1.chat_analytics.with_raw_response.get_component(
                component_id="",
            )


class TestAsyncChatAnalytics:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_analyze(self, async_client: AsyncStudyfetchSDK) -> None:
        chat_analytic = await async_client.v1.chat_analytics.analyze()
        assert_matches_type(ChatAnalyticsResponse, chat_analytic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_analyze_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        chat_analytic = await async_client.v1.chat_analytics.analyze(
            component_id="componentId",
            end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            group_ids=["string"],
            model_key="gpt-4o-mini",
            organization_id="organizationId",
            start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            user_id="userId",
        )
        assert_matches_type(ChatAnalyticsResponse, chat_analytic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_analyze(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.chat_analytics.with_raw_response.analyze()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat_analytic = await response.parse()
        assert_matches_type(ChatAnalyticsResponse, chat_analytic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_analyze(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.chat_analytics.with_streaming_response.analyze() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat_analytic = await response.parse()
            assert_matches_type(ChatAnalyticsResponse, chat_analytic, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_export(self, async_client: AsyncStudyfetchSDK) -> None:
        chat_analytic = await async_client.v1.chat_analytics.export()
        assert_matches_type(str, chat_analytic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_export_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        chat_analytic = await async_client.v1.chat_analytics.export(
            component_id="componentId",
            end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            group_ids=["string"],
            model_key="gpt-4o-mini",
            organization_id="organizationId",
            start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            user_id="userId",
        )
        assert_matches_type(str, chat_analytic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_export(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.chat_analytics.with_raw_response.export()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat_analytic = await response.parse()
        assert_matches_type(str, chat_analytic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_export(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.chat_analytics.with_streaming_response.export() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat_analytic = await response.parse()
            assert_matches_type(str, chat_analytic, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_component(self, async_client: AsyncStudyfetchSDK) -> None:
        chat_analytic = await async_client.v1.chat_analytics.get_component(
            component_id="componentId",
        )
        assert_matches_type(ChatAnalyticsResponse, chat_analytic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_component_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        chat_analytic = await async_client.v1.chat_analytics.get_component(
            component_id="componentId",
            end_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            group_ids=["string"],
            model_key="gpt-4o-mini",
            organization_id="organizationId",
            start_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            user_id="userId",
        )
        assert_matches_type(ChatAnalyticsResponse, chat_analytic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_component(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.chat_analytics.with_raw_response.get_component(
            component_id="componentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat_analytic = await response.parse()
        assert_matches_type(ChatAnalyticsResponse, chat_analytic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_component(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.chat_analytics.with_streaming_response.get_component(
            component_id="componentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat_analytic = await response.parse()
            assert_matches_type(ChatAnalyticsResponse, chat_analytic, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_component(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            await async_client.v1.chat_analytics.with_raw_response.get_component(
                component_id="",
            )
