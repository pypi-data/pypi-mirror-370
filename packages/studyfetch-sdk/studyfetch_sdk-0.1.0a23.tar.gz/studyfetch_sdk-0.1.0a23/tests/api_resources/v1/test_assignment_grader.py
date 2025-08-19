# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK
from studyfetch_sdk.types.v1 import (
    AssignmentGraderCreateResponse,
    AssignmentGraderGetAllResponse,
    AssignmentGraderGetByIDResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAssignmentGrader:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: StudyfetchSDK) -> None:
        assignment_grader = client.v1.assignment_grader.create(
            title="title",
        )
        assert_matches_type(AssignmentGraderCreateResponse, assignment_grader, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: StudyfetchSDK) -> None:
        assignment_grader = client.v1.assignment_grader.create(
            title="title",
            assignment_id="assignmentId",
            material_id="materialId",
            model="model",
            rubric={
                "criteria": [
                    {
                        "points_possible": 0,
                        "title": "title",
                        "description": "description",
                    }
                ]
            },
            rubric_template_id="rubricTemplateId",
            student_identifier="studentIdentifier",
            text_to_grade="textToGrade",
            user_id="userId",
        )
        assert_matches_type(AssignmentGraderCreateResponse, assignment_grader, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: StudyfetchSDK) -> None:
        response = client.v1.assignment_grader.with_raw_response.create(
            title="title",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assignment_grader = response.parse()
        assert_matches_type(AssignmentGraderCreateResponse, assignment_grader, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: StudyfetchSDK) -> None:
        with client.v1.assignment_grader.with_streaming_response.create(
            title="title",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assignment_grader = response.parse()
            assert_matches_type(AssignmentGraderCreateResponse, assignment_grader, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: StudyfetchSDK) -> None:
        assignment_grader = client.v1.assignment_grader.delete(
            "id",
        )
        assert assignment_grader is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: StudyfetchSDK) -> None:
        response = client.v1.assignment_grader.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assignment_grader = response.parse()
        assert assignment_grader is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: StudyfetchSDK) -> None:
        with client.v1.assignment_grader.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assignment_grader = response.parse()
            assert assignment_grader is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.assignment_grader.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_report(self, client: StudyfetchSDK) -> None:
        assignment_grader = client.v1.assignment_grader.generate_report(
            "assignmentId",
        )
        assert assignment_grader is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_generate_report(self, client: StudyfetchSDK) -> None:
        response = client.v1.assignment_grader.with_raw_response.generate_report(
            "assignmentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assignment_grader = response.parse()
        assert assignment_grader is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_generate_report(self, client: StudyfetchSDK) -> None:
        with client.v1.assignment_grader.with_streaming_response.generate_report(
            "assignmentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assignment_grader = response.parse()
            assert assignment_grader is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_generate_report(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assignment_id` but received ''"):
            client.v1.assignment_grader.with_raw_response.generate_report(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_all(self, client: StudyfetchSDK) -> None:
        assignment_grader = client.v1.assignment_grader.get_all()
        assert_matches_type(AssignmentGraderGetAllResponse, assignment_grader, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_all(self, client: StudyfetchSDK) -> None:
        response = client.v1.assignment_grader.with_raw_response.get_all()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assignment_grader = response.parse()
        assert_matches_type(AssignmentGraderGetAllResponse, assignment_grader, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_all(self, client: StudyfetchSDK) -> None:
        with client.v1.assignment_grader.with_streaming_response.get_all() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assignment_grader = response.parse()
            assert_matches_type(AssignmentGraderGetAllResponse, assignment_grader, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_by_id(self, client: StudyfetchSDK) -> None:
        assignment_grader = client.v1.assignment_grader.get_by_id(
            "id",
        )
        assert_matches_type(AssignmentGraderGetByIDResponse, assignment_grader, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_by_id(self, client: StudyfetchSDK) -> None:
        response = client.v1.assignment_grader.with_raw_response.get_by_id(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assignment_grader = response.parse()
        assert_matches_type(AssignmentGraderGetByIDResponse, assignment_grader, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_by_id(self, client: StudyfetchSDK) -> None:
        with client.v1.assignment_grader.with_streaming_response.get_by_id(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assignment_grader = response.parse()
            assert_matches_type(AssignmentGraderGetByIDResponse, assignment_grader, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_by_id(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.assignment_grader.with_raw_response.get_by_id(
                "",
            )


class TestAsyncAssignmentGrader:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncStudyfetchSDK) -> None:
        assignment_grader = await async_client.v1.assignment_grader.create(
            title="title",
        )
        assert_matches_type(AssignmentGraderCreateResponse, assignment_grader, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        assignment_grader = await async_client.v1.assignment_grader.create(
            title="title",
            assignment_id="assignmentId",
            material_id="materialId",
            model="model",
            rubric={
                "criteria": [
                    {
                        "points_possible": 0,
                        "title": "title",
                        "description": "description",
                    }
                ]
            },
            rubric_template_id="rubricTemplateId",
            student_identifier="studentIdentifier",
            text_to_grade="textToGrade",
            user_id="userId",
        )
        assert_matches_type(AssignmentGraderCreateResponse, assignment_grader, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.assignment_grader.with_raw_response.create(
            title="title",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assignment_grader = await response.parse()
        assert_matches_type(AssignmentGraderCreateResponse, assignment_grader, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.assignment_grader.with_streaming_response.create(
            title="title",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assignment_grader = await response.parse()
            assert_matches_type(AssignmentGraderCreateResponse, assignment_grader, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        assignment_grader = await async_client.v1.assignment_grader.delete(
            "id",
        )
        assert assignment_grader is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.assignment_grader.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assignment_grader = await response.parse()
        assert assignment_grader is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.assignment_grader.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assignment_grader = await response.parse()
            assert assignment_grader is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.assignment_grader.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_report(self, async_client: AsyncStudyfetchSDK) -> None:
        assignment_grader = await async_client.v1.assignment_grader.generate_report(
            "assignmentId",
        )
        assert assignment_grader is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_generate_report(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.assignment_grader.with_raw_response.generate_report(
            "assignmentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assignment_grader = await response.parse()
        assert assignment_grader is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_generate_report(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.assignment_grader.with_streaming_response.generate_report(
            "assignmentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assignment_grader = await response.parse()
            assert assignment_grader is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_generate_report(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assignment_id` but received ''"):
            await async_client.v1.assignment_grader.with_raw_response.generate_report(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_all(self, async_client: AsyncStudyfetchSDK) -> None:
        assignment_grader = await async_client.v1.assignment_grader.get_all()
        assert_matches_type(AssignmentGraderGetAllResponse, assignment_grader, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_all(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.assignment_grader.with_raw_response.get_all()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assignment_grader = await response.parse()
        assert_matches_type(AssignmentGraderGetAllResponse, assignment_grader, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_all(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.assignment_grader.with_streaming_response.get_all() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assignment_grader = await response.parse()
            assert_matches_type(AssignmentGraderGetAllResponse, assignment_grader, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_by_id(self, async_client: AsyncStudyfetchSDK) -> None:
        assignment_grader = await async_client.v1.assignment_grader.get_by_id(
            "id",
        )
        assert_matches_type(AssignmentGraderGetByIDResponse, assignment_grader, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_by_id(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.assignment_grader.with_raw_response.get_by_id(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assignment_grader = await response.parse()
        assert_matches_type(AssignmentGraderGetByIDResponse, assignment_grader, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_by_id(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.assignment_grader.with_streaming_response.get_by_id(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assignment_grader = await response.parse()
            assert_matches_type(AssignmentGraderGetByIDResponse, assignment_grader, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_by_id(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.assignment_grader.with_raw_response.get_by_id(
                "",
            )
