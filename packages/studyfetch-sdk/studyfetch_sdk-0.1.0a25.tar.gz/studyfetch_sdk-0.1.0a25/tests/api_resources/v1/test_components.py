# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK
from studyfetch_sdk.types.v1 import (
    ComponentResponse,
    ComponentListResponse,
    ComponentGenerateEmbedResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestComponents:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: StudyfetchSDK) -> None:
        component = client.v1.components.create(
            config={"model": "gpt-4o-mini-2024-07-18"},
            name="My Study Component",
            type="chat",
        )
        assert_matches_type(ComponentResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: StudyfetchSDK) -> None:
        component = client.v1.components.create(
            config={
                "model": "gpt-4o-mini-2024-07-18",
                "enable_component_creation": True,
                "enable_follow_ups": True,
                "enable_guardrails": True,
                "enable_history": True,
                "enable_rag_search": True,
                "enable_voice": True,
                "enable_web_search": True,
                "folders": ["string"],
                "guardrail_rules": [
                    {
                        "id": "rule-1",
                        "action": "block",
                        "condition": "The AI response provides direct answers to homework",
                        "description": "No direct homework answers",
                        "message": "I cannot provide direct answers to homework questions.",
                    }
                ],
                "materials": ["string"],
                "max_steps": 0,
                "max_tokens": 0,
                "system_prompt": "systemPrompt",
                "temperature": 0,
            },
            name="My Study Component",
            type="chat",
            description="A component for studying biology",
            metadata={},
        )
        assert_matches_type(ComponentResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: StudyfetchSDK) -> None:
        response = client.v1.components.with_raw_response.create(
            config={"model": "gpt-4o-mini-2024-07-18"},
            name="My Study Component",
            type="chat",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = response.parse()
        assert_matches_type(ComponentResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: StudyfetchSDK) -> None:
        with client.v1.components.with_streaming_response.create(
            config={"model": "gpt-4o-mini-2024-07-18"},
            name="My Study Component",
            type="chat",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = response.parse()
            assert_matches_type(ComponentResponse, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: StudyfetchSDK) -> None:
        component = client.v1.components.retrieve(
            "id",
        )
        assert_matches_type(ComponentResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: StudyfetchSDK) -> None:
        response = client.v1.components.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = response.parse()
        assert_matches_type(ComponentResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: StudyfetchSDK) -> None:
        with client.v1.components.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = response.parse()
            assert_matches_type(ComponentResponse, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.components.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: StudyfetchSDK) -> None:
        component = client.v1.components.update(
            id="id",
        )
        assert_matches_type(ComponentResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: StudyfetchSDK) -> None:
        component = client.v1.components.update(
            id="id",
            status="draft",
        )
        assert_matches_type(ComponentResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: StudyfetchSDK) -> None:
        response = client.v1.components.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = response.parse()
        assert_matches_type(ComponentResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: StudyfetchSDK) -> None:
        with client.v1.components.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = response.parse()
            assert_matches_type(ComponentResponse, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.components.with_raw_response.update(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: StudyfetchSDK) -> None:
        component = client.v1.components.list()
        assert_matches_type(ComponentListResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: StudyfetchSDK) -> None:
        component = client.v1.components.list(
            type="chat",
        )
        assert_matches_type(ComponentListResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: StudyfetchSDK) -> None:
        response = client.v1.components.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = response.parse()
        assert_matches_type(ComponentListResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: StudyfetchSDK) -> None:
        with client.v1.components.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = response.parse()
            assert_matches_type(ComponentListResponse, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: StudyfetchSDK) -> None:
        component = client.v1.components.delete(
            "id",
        )
        assert component is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: StudyfetchSDK) -> None:
        response = client.v1.components.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = response.parse()
        assert component is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: StudyfetchSDK) -> None:
        with client.v1.components.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = response.parse()
            assert component is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.components.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_activate(self, client: StudyfetchSDK) -> None:
        component = client.v1.components.activate(
            "id",
        )
        assert component is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_activate(self, client: StudyfetchSDK) -> None:
        response = client.v1.components.with_raw_response.activate(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = response.parse()
        assert component is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_activate(self, client: StudyfetchSDK) -> None:
        with client.v1.components.with_streaming_response.activate(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = response.parse()
            assert component is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_activate(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.components.with_raw_response.activate(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_deactivate(self, client: StudyfetchSDK) -> None:
        component = client.v1.components.deactivate(
            "id",
        )
        assert component is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_deactivate(self, client: StudyfetchSDK) -> None:
        response = client.v1.components.with_raw_response.deactivate(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = response.parse()
        assert component is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_deactivate(self, client: StudyfetchSDK) -> None:
        with client.v1.components.with_streaming_response.deactivate(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = response.parse()
            assert component is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_deactivate(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.components.with_raw_response.deactivate(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_embed(self, client: StudyfetchSDK) -> None:
        component = client.v1.components.generate_embed(
            id="id",
        )
        assert_matches_type(ComponentGenerateEmbedResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_embed_with_all_params(self, client: StudyfetchSDK) -> None:
        component = client.v1.components.generate_embed(
            id="id",
            expiry_hours=0,
            features={
                "enable_bad_words_filter": True,
                "enable_component_creation": True,
                "enable_follow_ups": True,
                "enable_guardrails": True,
                "enable_history": True,
                "enable_image_sources": True,
                "enable_outline": True,
                "enable_transcript": True,
                "enable_voice": True,
                "enable_web_search": True,
                "enable_web_search_sources": True,
                "placeholder_text": "placeholderText",
            },
            group_ids=["class-101", "class-102"],
            height="height",
            session_id="sessionId",
            theme={
                "background_color": "backgroundColor",
                "border_radius": "borderRadius",
                "font_family": "fontFamily",
                "font_size": "fontSize",
                "hide_branding": True,
                "logo_url": "logoUrl",
                "padding": "padding",
                "primary_color": "primaryColor",
                "secondary_color": "secondaryColor",
                "text_color": "textColor",
            },
            user_id="userId",
            width="width",
        )
        assert_matches_type(ComponentGenerateEmbedResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_generate_embed(self, client: StudyfetchSDK) -> None:
        response = client.v1.components.with_raw_response.generate_embed(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = response.parse()
        assert_matches_type(ComponentGenerateEmbedResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_generate_embed(self, client: StudyfetchSDK) -> None:
        with client.v1.components.with_streaming_response.generate_embed(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = response.parse()
            assert_matches_type(ComponentGenerateEmbedResponse, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_generate_embed(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.components.with_raw_response.generate_embed(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_interact(self, client: StudyfetchSDK) -> None:
        component = client.v1.components.interact(
            "id",
        )
        assert component is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_interact(self, client: StudyfetchSDK) -> None:
        response = client.v1.components.with_raw_response.interact(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = response.parse()
        assert component is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_interact(self, client: StudyfetchSDK) -> None:
        with client.v1.components.with_streaming_response.interact(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = response.parse()
            assert component is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_interact(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.components.with_raw_response.interact(
                "",
            )


class TestAsyncComponents:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.components.create(
            config={"model": "gpt-4o-mini-2024-07-18"},
            name="My Study Component",
            type="chat",
        )
        assert_matches_type(ComponentResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.components.create(
            config={
                "model": "gpt-4o-mini-2024-07-18",
                "enable_component_creation": True,
                "enable_follow_ups": True,
                "enable_guardrails": True,
                "enable_history": True,
                "enable_rag_search": True,
                "enable_voice": True,
                "enable_web_search": True,
                "folders": ["string"],
                "guardrail_rules": [
                    {
                        "id": "rule-1",
                        "action": "block",
                        "condition": "The AI response provides direct answers to homework",
                        "description": "No direct homework answers",
                        "message": "I cannot provide direct answers to homework questions.",
                    }
                ],
                "materials": ["string"],
                "max_steps": 0,
                "max_tokens": 0,
                "system_prompt": "systemPrompt",
                "temperature": 0,
            },
            name="My Study Component",
            type="chat",
            description="A component for studying biology",
            metadata={},
        )
        assert_matches_type(ComponentResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.components.with_raw_response.create(
            config={"model": "gpt-4o-mini-2024-07-18"},
            name="My Study Component",
            type="chat",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = await response.parse()
        assert_matches_type(ComponentResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.components.with_streaming_response.create(
            config={"model": "gpt-4o-mini-2024-07-18"},
            name="My Study Component",
            type="chat",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = await response.parse()
            assert_matches_type(ComponentResponse, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.components.retrieve(
            "id",
        )
        assert_matches_type(ComponentResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.components.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = await response.parse()
        assert_matches_type(ComponentResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.components.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = await response.parse()
            assert_matches_type(ComponentResponse, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.components.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.components.update(
            id="id",
        )
        assert_matches_type(ComponentResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.components.update(
            id="id",
            status="draft",
        )
        assert_matches_type(ComponentResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.components.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = await response.parse()
        assert_matches_type(ComponentResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.components.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = await response.parse()
            assert_matches_type(ComponentResponse, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.components.with_raw_response.update(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.components.list()
        assert_matches_type(ComponentListResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.components.list(
            type="chat",
        )
        assert_matches_type(ComponentListResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.components.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = await response.parse()
        assert_matches_type(ComponentListResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.components.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = await response.parse()
            assert_matches_type(ComponentListResponse, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.components.delete(
            "id",
        )
        assert component is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.components.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = await response.parse()
        assert component is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.components.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = await response.parse()
            assert component is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.components.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_activate(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.components.activate(
            "id",
        )
        assert component is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_activate(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.components.with_raw_response.activate(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = await response.parse()
        assert component is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_activate(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.components.with_streaming_response.activate(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = await response.parse()
            assert component is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_activate(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.components.with_raw_response.activate(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_deactivate(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.components.deactivate(
            "id",
        )
        assert component is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_deactivate(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.components.with_raw_response.deactivate(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = await response.parse()
        assert component is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_deactivate(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.components.with_streaming_response.deactivate(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = await response.parse()
            assert component is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_deactivate(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.components.with_raw_response.deactivate(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_embed(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.components.generate_embed(
            id="id",
        )
        assert_matches_type(ComponentGenerateEmbedResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_embed_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.components.generate_embed(
            id="id",
            expiry_hours=0,
            features={
                "enable_bad_words_filter": True,
                "enable_component_creation": True,
                "enable_follow_ups": True,
                "enable_guardrails": True,
                "enable_history": True,
                "enable_image_sources": True,
                "enable_outline": True,
                "enable_transcript": True,
                "enable_voice": True,
                "enable_web_search": True,
                "enable_web_search_sources": True,
                "placeholder_text": "placeholderText",
            },
            group_ids=["class-101", "class-102"],
            height="height",
            session_id="sessionId",
            theme={
                "background_color": "backgroundColor",
                "border_radius": "borderRadius",
                "font_family": "fontFamily",
                "font_size": "fontSize",
                "hide_branding": True,
                "logo_url": "logoUrl",
                "padding": "padding",
                "primary_color": "primaryColor",
                "secondary_color": "secondaryColor",
                "text_color": "textColor",
            },
            user_id="userId",
            width="width",
        )
        assert_matches_type(ComponentGenerateEmbedResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_generate_embed(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.components.with_raw_response.generate_embed(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = await response.parse()
        assert_matches_type(ComponentGenerateEmbedResponse, component, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_generate_embed(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.components.with_streaming_response.generate_embed(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = await response.parse()
            assert_matches_type(ComponentGenerateEmbedResponse, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_generate_embed(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.components.with_raw_response.generate_embed(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_interact(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.components.interact(
            "id",
        )
        assert component is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_interact(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.components.with_raw_response.interact(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = await response.parse()
        assert component is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_interact(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.components.with_streaming_response.interact(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = await response.parse()
            assert component is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_interact(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.components.with_raw_response.interact(
                "",
            )
