# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ....types.v1 import assignment_grader_create_params
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from .rubric_templates import (
    RubricTemplatesResource,
    AsyncRubricTemplatesResource,
    RubricTemplatesResourceWithRawResponse,
    AsyncRubricTemplatesResourceWithRawResponse,
    RubricTemplatesResourceWithStreamingResponse,
    AsyncRubricTemplatesResourceWithStreamingResponse,
)
from ....types.v1.assignment_grader_create_response import AssignmentGraderCreateResponse
from ....types.v1.assignment_grader_get_all_response import AssignmentGraderGetAllResponse
from ....types.v1.assignment_grader_get_by_id_response import AssignmentGraderGetByIDResponse

__all__ = ["AssignmentGraderResource", "AsyncAssignmentGraderResource"]


class AssignmentGraderResource(SyncAPIResource):
    @cached_property
    def rubric_templates(self) -> RubricTemplatesResource:
        return RubricTemplatesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AssignmentGraderResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AssignmentGraderResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AssignmentGraderResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AssignmentGraderResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        title: str,
        assignment_id: str | NotGiven = NOT_GIVEN,
        material_id: str | NotGiven = NOT_GIVEN,
        model: str | NotGiven = NOT_GIVEN,
        rubric: assignment_grader_create_params.Rubric | NotGiven = NOT_GIVEN,
        rubric_template_id: str | NotGiven = NOT_GIVEN,
        student_identifier: str | NotGiven = NOT_GIVEN,
        text_to_grade: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssignmentGraderCreateResponse:
        """
        Grade a new assignment

        Args:
          title: Title of the assignment

          assignment_id: Assignment ID for grouping submissions

          material_id: Material ID to grade

          model: AI model to use

          rubric: Grading rubric

          rubric_template_id: Rubric template ID to use

          student_identifier: Student identifier (email or ID)

          text_to_grade: Text content to grade

          user_id: User ID for tracking

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/assignment-grader/create",
            body=maybe_transform(
                {
                    "title": title,
                    "assignment_id": assignment_id,
                    "material_id": material_id,
                    "model": model,
                    "rubric": rubric,
                    "rubric_template_id": rubric_template_id,
                    "student_identifier": student_identifier,
                    "text_to_grade": text_to_grade,
                    "user_id": user_id,
                },
                assignment_grader_create_params.AssignmentGraderCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssignmentGraderCreateResponse,
        )

    def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete an assignment grader by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/api/v1/assignment-grader/delete/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def generate_report(
        self,
        assignment_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Generate educator report for an assignment

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not assignment_id:
            raise ValueError(f"Expected a non-empty value for `assignment_id` but received {assignment_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/api/v1/assignment-grader/educator-report/{assignment_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get_all(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssignmentGraderGetAllResponse:
        """Get all assignment graders"""
        return self._get(
            "/api/v1/assignment-grader/get",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssignmentGraderGetAllResponse,
        )

    def get_by_id(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssignmentGraderGetByIDResponse:
        """
        Get an assignment grader by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/api/v1/assignment-grader/get/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssignmentGraderGetByIDResponse,
        )


class AsyncAssignmentGraderResource(AsyncAPIResource):
    @cached_property
    def rubric_templates(self) -> AsyncRubricTemplatesResource:
        return AsyncRubricTemplatesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAssignmentGraderResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAssignmentGraderResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAssignmentGraderResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncAssignmentGraderResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        title: str,
        assignment_id: str | NotGiven = NOT_GIVEN,
        material_id: str | NotGiven = NOT_GIVEN,
        model: str | NotGiven = NOT_GIVEN,
        rubric: assignment_grader_create_params.Rubric | NotGiven = NOT_GIVEN,
        rubric_template_id: str | NotGiven = NOT_GIVEN,
        student_identifier: str | NotGiven = NOT_GIVEN,
        text_to_grade: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssignmentGraderCreateResponse:
        """
        Grade a new assignment

        Args:
          title: Title of the assignment

          assignment_id: Assignment ID for grouping submissions

          material_id: Material ID to grade

          model: AI model to use

          rubric: Grading rubric

          rubric_template_id: Rubric template ID to use

          student_identifier: Student identifier (email or ID)

          text_to_grade: Text content to grade

          user_id: User ID for tracking

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/assignment-grader/create",
            body=await async_maybe_transform(
                {
                    "title": title,
                    "assignment_id": assignment_id,
                    "material_id": material_id,
                    "model": model,
                    "rubric": rubric,
                    "rubric_template_id": rubric_template_id,
                    "student_identifier": student_identifier,
                    "text_to_grade": text_to_grade,
                    "user_id": user_id,
                },
                assignment_grader_create_params.AssignmentGraderCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssignmentGraderCreateResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete an assignment grader by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/api/v1/assignment-grader/delete/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def generate_report(
        self,
        assignment_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Generate educator report for an assignment

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not assignment_id:
            raise ValueError(f"Expected a non-empty value for `assignment_id` but received {assignment_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/api/v1/assignment-grader/educator-report/{assignment_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get_all(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssignmentGraderGetAllResponse:
        """Get all assignment graders"""
        return await self._get(
            "/api/v1/assignment-grader/get",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssignmentGraderGetAllResponse,
        )

    async def get_by_id(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssignmentGraderGetByIDResponse:
        """
        Get an assignment grader by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/api/v1/assignment-grader/get/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssignmentGraderGetByIDResponse,
        )


class AssignmentGraderResourceWithRawResponse:
    def __init__(self, assignment_grader: AssignmentGraderResource) -> None:
        self._assignment_grader = assignment_grader

        self.create = to_raw_response_wrapper(
            assignment_grader.create,
        )
        self.delete = to_raw_response_wrapper(
            assignment_grader.delete,
        )
        self.generate_report = to_raw_response_wrapper(
            assignment_grader.generate_report,
        )
        self.get_all = to_raw_response_wrapper(
            assignment_grader.get_all,
        )
        self.get_by_id = to_raw_response_wrapper(
            assignment_grader.get_by_id,
        )

    @cached_property
    def rubric_templates(self) -> RubricTemplatesResourceWithRawResponse:
        return RubricTemplatesResourceWithRawResponse(self._assignment_grader.rubric_templates)


class AsyncAssignmentGraderResourceWithRawResponse:
    def __init__(self, assignment_grader: AsyncAssignmentGraderResource) -> None:
        self._assignment_grader = assignment_grader

        self.create = async_to_raw_response_wrapper(
            assignment_grader.create,
        )
        self.delete = async_to_raw_response_wrapper(
            assignment_grader.delete,
        )
        self.generate_report = async_to_raw_response_wrapper(
            assignment_grader.generate_report,
        )
        self.get_all = async_to_raw_response_wrapper(
            assignment_grader.get_all,
        )
        self.get_by_id = async_to_raw_response_wrapper(
            assignment_grader.get_by_id,
        )

    @cached_property
    def rubric_templates(self) -> AsyncRubricTemplatesResourceWithRawResponse:
        return AsyncRubricTemplatesResourceWithRawResponse(self._assignment_grader.rubric_templates)


class AssignmentGraderResourceWithStreamingResponse:
    def __init__(self, assignment_grader: AssignmentGraderResource) -> None:
        self._assignment_grader = assignment_grader

        self.create = to_streamed_response_wrapper(
            assignment_grader.create,
        )
        self.delete = to_streamed_response_wrapper(
            assignment_grader.delete,
        )
        self.generate_report = to_streamed_response_wrapper(
            assignment_grader.generate_report,
        )
        self.get_all = to_streamed_response_wrapper(
            assignment_grader.get_all,
        )
        self.get_by_id = to_streamed_response_wrapper(
            assignment_grader.get_by_id,
        )

    @cached_property
    def rubric_templates(self) -> RubricTemplatesResourceWithStreamingResponse:
        return RubricTemplatesResourceWithStreamingResponse(self._assignment_grader.rubric_templates)


class AsyncAssignmentGraderResourceWithStreamingResponse:
    def __init__(self, assignment_grader: AsyncAssignmentGraderResource) -> None:
        self._assignment_grader = assignment_grader

        self.create = async_to_streamed_response_wrapper(
            assignment_grader.create,
        )
        self.delete = async_to_streamed_response_wrapper(
            assignment_grader.delete,
        )
        self.generate_report = async_to_streamed_response_wrapper(
            assignment_grader.generate_report,
        )
        self.get_all = async_to_streamed_response_wrapper(
            assignment_grader.get_all,
        )
        self.get_by_id = async_to_streamed_response_wrapper(
            assignment_grader.get_by_id,
        )

    @cached_property
    def rubric_templates(self) -> AsyncRubricTemplatesResourceWithStreamingResponse:
        return AsyncRubricTemplatesResourceWithStreamingResponse(self._assignment_grader.rubric_templates)
