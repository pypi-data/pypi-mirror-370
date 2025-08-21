# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK
from studyfetch_sdk.types.v1.assignment_grader import (
    RubricTemplateResponse,
    RubricTemplateListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRubricTemplates:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: StudyfetchSDK) -> None:
        rubric_template = client.v1.assignment_grader.rubric_templates.create(
            criteria=[
                {
                    "points_possible": 0,
                    "title": "title",
                }
            ],
            name="name",
        )
        assert_matches_type(RubricTemplateResponse, rubric_template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: StudyfetchSDK) -> None:
        rubric_template = client.v1.assignment_grader.rubric_templates.create(
            criteria=[
                {
                    "points_possible": 0,
                    "title": "title",
                    "description": "description",
                }
            ],
            name="name",
            description="description",
        )
        assert_matches_type(RubricTemplateResponse, rubric_template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: StudyfetchSDK) -> None:
        response = client.v1.assignment_grader.rubric_templates.with_raw_response.create(
            criteria=[
                {
                    "points_possible": 0,
                    "title": "title",
                }
            ],
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rubric_template = response.parse()
        assert_matches_type(RubricTemplateResponse, rubric_template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: StudyfetchSDK) -> None:
        with client.v1.assignment_grader.rubric_templates.with_streaming_response.create(
            criteria=[
                {
                    "points_possible": 0,
                    "title": "title",
                }
            ],
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rubric_template = response.parse()
            assert_matches_type(RubricTemplateResponse, rubric_template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: StudyfetchSDK) -> None:
        rubric_template = client.v1.assignment_grader.rubric_templates.list()
        assert_matches_type(RubricTemplateListResponse, rubric_template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: StudyfetchSDK) -> None:
        response = client.v1.assignment_grader.rubric_templates.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rubric_template = response.parse()
        assert_matches_type(RubricTemplateListResponse, rubric_template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: StudyfetchSDK) -> None:
        with client.v1.assignment_grader.rubric_templates.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rubric_template = response.parse()
            assert_matches_type(RubricTemplateListResponse, rubric_template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: StudyfetchSDK) -> None:
        rubric_template = client.v1.assignment_grader.rubric_templates.delete(
            "id",
        )
        assert rubric_template is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: StudyfetchSDK) -> None:
        response = client.v1.assignment_grader.rubric_templates.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rubric_template = response.parse()
        assert rubric_template is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: StudyfetchSDK) -> None:
        with client.v1.assignment_grader.rubric_templates.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rubric_template = response.parse()
            assert rubric_template is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.assignment_grader.rubric_templates.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_by_id(self, client: StudyfetchSDK) -> None:
        rubric_template = client.v1.assignment_grader.rubric_templates.get_by_id(
            "id",
        )
        assert_matches_type(RubricTemplateResponse, rubric_template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_by_id(self, client: StudyfetchSDK) -> None:
        response = client.v1.assignment_grader.rubric_templates.with_raw_response.get_by_id(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rubric_template = response.parse()
        assert_matches_type(RubricTemplateResponse, rubric_template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_by_id(self, client: StudyfetchSDK) -> None:
        with client.v1.assignment_grader.rubric_templates.with_streaming_response.get_by_id(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rubric_template = response.parse()
            assert_matches_type(RubricTemplateResponse, rubric_template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_by_id(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.assignment_grader.rubric_templates.with_raw_response.get_by_id(
                "",
            )


class TestAsyncRubricTemplates:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncStudyfetchSDK) -> None:
        rubric_template = await async_client.v1.assignment_grader.rubric_templates.create(
            criteria=[
                {
                    "points_possible": 0,
                    "title": "title",
                }
            ],
            name="name",
        )
        assert_matches_type(RubricTemplateResponse, rubric_template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        rubric_template = await async_client.v1.assignment_grader.rubric_templates.create(
            criteria=[
                {
                    "points_possible": 0,
                    "title": "title",
                    "description": "description",
                }
            ],
            name="name",
            description="description",
        )
        assert_matches_type(RubricTemplateResponse, rubric_template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.assignment_grader.rubric_templates.with_raw_response.create(
            criteria=[
                {
                    "points_possible": 0,
                    "title": "title",
                }
            ],
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rubric_template = await response.parse()
        assert_matches_type(RubricTemplateResponse, rubric_template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.assignment_grader.rubric_templates.with_streaming_response.create(
            criteria=[
                {
                    "points_possible": 0,
                    "title": "title",
                }
            ],
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rubric_template = await response.parse()
            assert_matches_type(RubricTemplateResponse, rubric_template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncStudyfetchSDK) -> None:
        rubric_template = await async_client.v1.assignment_grader.rubric_templates.list()
        assert_matches_type(RubricTemplateListResponse, rubric_template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.assignment_grader.rubric_templates.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rubric_template = await response.parse()
        assert_matches_type(RubricTemplateListResponse, rubric_template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.assignment_grader.rubric_templates.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rubric_template = await response.parse()
            assert_matches_type(RubricTemplateListResponse, rubric_template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        rubric_template = await async_client.v1.assignment_grader.rubric_templates.delete(
            "id",
        )
        assert rubric_template is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.assignment_grader.rubric_templates.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rubric_template = await response.parse()
        assert rubric_template is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.assignment_grader.rubric_templates.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rubric_template = await response.parse()
            assert rubric_template is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.assignment_grader.rubric_templates.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_by_id(self, async_client: AsyncStudyfetchSDK) -> None:
        rubric_template = await async_client.v1.assignment_grader.rubric_templates.get_by_id(
            "id",
        )
        assert_matches_type(RubricTemplateResponse, rubric_template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_by_id(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.assignment_grader.rubric_templates.with_raw_response.get_by_id(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rubric_template = await response.parse()
        assert_matches_type(RubricTemplateResponse, rubric_template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_by_id(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.assignment_grader.rubric_templates.with_streaming_response.get_by_id(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rubric_template = await response.parse()
            assert_matches_type(RubricTemplateResponse, rubric_template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_by_id(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.assignment_grader.rubric_templates.with_raw_response.get_by_id(
                "",
            )
