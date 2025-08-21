# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v1.assignment_grader import rubric_template_create_params
from ....types.v1.assignment_grader.rubric_criterion_param import RubricCriterionParam
from ....types.v1.assignment_grader.rubric_template_response import RubricTemplateResponse
from ....types.v1.assignment_grader.rubric_template_list_response import RubricTemplateListResponse

__all__ = ["RubricTemplatesResource", "AsyncRubricTemplatesResource"]


class RubricTemplatesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RubricTemplatesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return RubricTemplatesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RubricTemplatesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return RubricTemplatesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        criteria: Iterable[RubricCriterionParam],
        name: str,
        description: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RubricTemplateResponse:
        """
        Create a new rubric template

        Args:
          criteria: Grading criteria

          name: Name of the rubric template

          description: Description of the rubric template

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/assignment-grader/rubric-templates",
            body=maybe_transform(
                {
                    "criteria": criteria,
                    "name": name,
                    "description": description,
                },
                rubric_template_create_params.RubricTemplateCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RubricTemplateResponse,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RubricTemplateListResponse:
        """Get all rubric templates"""
        return self._get(
            "/api/v1/assignment-grader/rubric-templates",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RubricTemplateListResponse,
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
        Delete a rubric template by ID

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
            f"/api/v1/assignment-grader/rubric-templates/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
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
    ) -> RubricTemplateResponse:
        """
        Get a rubric template by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/api/v1/assignment-grader/rubric-templates/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RubricTemplateResponse,
        )


class AsyncRubricTemplatesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRubricTemplatesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRubricTemplatesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRubricTemplatesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncRubricTemplatesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        criteria: Iterable[RubricCriterionParam],
        name: str,
        description: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RubricTemplateResponse:
        """
        Create a new rubric template

        Args:
          criteria: Grading criteria

          name: Name of the rubric template

          description: Description of the rubric template

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/assignment-grader/rubric-templates",
            body=await async_maybe_transform(
                {
                    "criteria": criteria,
                    "name": name,
                    "description": description,
                },
                rubric_template_create_params.RubricTemplateCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RubricTemplateResponse,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RubricTemplateListResponse:
        """Get all rubric templates"""
        return await self._get(
            "/api/v1/assignment-grader/rubric-templates",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RubricTemplateListResponse,
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
        Delete a rubric template by ID

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
            f"/api/v1/assignment-grader/rubric-templates/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
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
    ) -> RubricTemplateResponse:
        """
        Get a rubric template by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/api/v1/assignment-grader/rubric-templates/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RubricTemplateResponse,
        )


class RubricTemplatesResourceWithRawResponse:
    def __init__(self, rubric_templates: RubricTemplatesResource) -> None:
        self._rubric_templates = rubric_templates

        self.create = to_raw_response_wrapper(
            rubric_templates.create,
        )
        self.list = to_raw_response_wrapper(
            rubric_templates.list,
        )
        self.delete = to_raw_response_wrapper(
            rubric_templates.delete,
        )
        self.get_by_id = to_raw_response_wrapper(
            rubric_templates.get_by_id,
        )


class AsyncRubricTemplatesResourceWithRawResponse:
    def __init__(self, rubric_templates: AsyncRubricTemplatesResource) -> None:
        self._rubric_templates = rubric_templates

        self.create = async_to_raw_response_wrapper(
            rubric_templates.create,
        )
        self.list = async_to_raw_response_wrapper(
            rubric_templates.list,
        )
        self.delete = async_to_raw_response_wrapper(
            rubric_templates.delete,
        )
        self.get_by_id = async_to_raw_response_wrapper(
            rubric_templates.get_by_id,
        )


class RubricTemplatesResourceWithStreamingResponse:
    def __init__(self, rubric_templates: RubricTemplatesResource) -> None:
        self._rubric_templates = rubric_templates

        self.create = to_streamed_response_wrapper(
            rubric_templates.create,
        )
        self.list = to_streamed_response_wrapper(
            rubric_templates.list,
        )
        self.delete = to_streamed_response_wrapper(
            rubric_templates.delete,
        )
        self.get_by_id = to_streamed_response_wrapper(
            rubric_templates.get_by_id,
        )


class AsyncRubricTemplatesResourceWithStreamingResponse:
    def __init__(self, rubric_templates: AsyncRubricTemplatesResource) -> None:
        self._rubric_templates = rubric_templates

        self.create = async_to_streamed_response_wrapper(
            rubric_templates.create,
        )
        self.list = async_to_streamed_response_wrapper(
            rubric_templates.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            rubric_templates.delete,
        )
        self.get_by_id = async_to_streamed_response_wrapper(
            rubric_templates.get_by_id,
        )
