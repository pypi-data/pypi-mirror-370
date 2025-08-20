# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ...types.v1 import usage_get_stats_params, usage_get_summary_params, usage_list_events_params
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options

__all__ = ["UsageResource", "AsyncUsageResource"]


class UsageResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UsageResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return UsageResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UsageResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return UsageResourceWithStreamingResponse(self)

    def get_stats(
        self,
        *,
        end_date: str | NotGiven = NOT_GIVEN,
        group_id: str | NotGiven = NOT_GIVEN,
        start_date: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get usage statistics

        Args:
          end_date: End date for stats (ISO 8601)

          group_id: Filter by group ID

          start_date: Start date for stats (ISO 8601)

          user_id: Filter by user ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/api/v1/usage/stats",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end_date": end_date,
                        "group_id": group_id,
                        "start_date": start_date,
                        "user_id": user_id,
                    },
                    usage_get_stats_params.UsageGetStatsParams,
                ),
            ),
            cast_to=NoneType,
        )

    def get_summary(
        self,
        *,
        end_date: str,
        period: Literal["hourly", "daily", "monthly"],
        start_date: str,
        group_by: Literal["user", "group", "model", "endpoint"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get usage summary

        Args:
          end_date: End date for summary (ISO 8601)

          period: Summary period

          start_date: Start date for summary (ISO 8601)

          group_by: Group results by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/api/v1/usage/summary",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end_date": end_date,
                        "period": period,
                        "start_date": start_date,
                        "group_by": group_by,
                    },
                    usage_get_summary_params.UsageGetSummaryParams,
                ),
            ),
            cast_to=NoneType,
        )

    def list_events(
        self,
        *,
        end_date: str | NotGiven = NOT_GIVEN,
        event_type: Literal[
            "material_created",
            "material_uploaded",
            "material_processed",
            "material_deleted",
            "component_created",
            "component_accessed",
            "component_deleted",
            "component_usage",
            "chat_message_sent",
            "chat_session_started",
            "chat_session_ended",
            "chat_feedback",
            "test_created",
            "test_started",
            "test_completed",
            "test_question_answered",
            "test_retaken",
            "audio_recap_create",
            "assignment_grader_create",
            "api_call",
            "cache_hit",
            "sso_login",
            "sso_logout",
            "student_performance",
        ]
        | NotGiven = NOT_GIVEN,
        group_id: str | NotGiven = NOT_GIVEN,
        limit: float | NotGiven = NOT_GIVEN,
        offset: float | NotGiven = NOT_GIVEN,
        resource_id: str | NotGiven = NOT_GIVEN,
        start_date: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get usage events

        Args:
          end_date: End date for filtering (ISO 8601)

          event_type: Filter by event type

          group_id: Filter by group ID

          limit: Number of results to return

          offset: Offset for pagination

          resource_id: Filter by resource ID

          start_date: Start date for filtering (ISO 8601)

          user_id: Filter by user ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/api/v1/usage/events",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end_date": end_date,
                        "event_type": event_type,
                        "group_id": group_id,
                        "limit": limit,
                        "offset": offset,
                        "resource_id": resource_id,
                        "start_date": start_date,
                        "user_id": user_id,
                    },
                    usage_list_events_params.UsageListEventsParams,
                ),
            ),
            cast_to=NoneType,
        )


class AsyncUsageResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUsageResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncUsageResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUsageResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncUsageResourceWithStreamingResponse(self)

    async def get_stats(
        self,
        *,
        end_date: str | NotGiven = NOT_GIVEN,
        group_id: str | NotGiven = NOT_GIVEN,
        start_date: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get usage statistics

        Args:
          end_date: End date for stats (ISO 8601)

          group_id: Filter by group ID

          start_date: Start date for stats (ISO 8601)

          user_id: Filter by user ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/api/v1/usage/stats",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "end_date": end_date,
                        "group_id": group_id,
                        "start_date": start_date,
                        "user_id": user_id,
                    },
                    usage_get_stats_params.UsageGetStatsParams,
                ),
            ),
            cast_to=NoneType,
        )

    async def get_summary(
        self,
        *,
        end_date: str,
        period: Literal["hourly", "daily", "monthly"],
        start_date: str,
        group_by: Literal["user", "group", "model", "endpoint"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get usage summary

        Args:
          end_date: End date for summary (ISO 8601)

          period: Summary period

          start_date: Start date for summary (ISO 8601)

          group_by: Group results by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/api/v1/usage/summary",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "end_date": end_date,
                        "period": period,
                        "start_date": start_date,
                        "group_by": group_by,
                    },
                    usage_get_summary_params.UsageGetSummaryParams,
                ),
            ),
            cast_to=NoneType,
        )

    async def list_events(
        self,
        *,
        end_date: str | NotGiven = NOT_GIVEN,
        event_type: Literal[
            "material_created",
            "material_uploaded",
            "material_processed",
            "material_deleted",
            "component_created",
            "component_accessed",
            "component_deleted",
            "component_usage",
            "chat_message_sent",
            "chat_session_started",
            "chat_session_ended",
            "chat_feedback",
            "test_created",
            "test_started",
            "test_completed",
            "test_question_answered",
            "test_retaken",
            "audio_recap_create",
            "assignment_grader_create",
            "api_call",
            "cache_hit",
            "sso_login",
            "sso_logout",
            "student_performance",
        ]
        | NotGiven = NOT_GIVEN,
        group_id: str | NotGiven = NOT_GIVEN,
        limit: float | NotGiven = NOT_GIVEN,
        offset: float | NotGiven = NOT_GIVEN,
        resource_id: str | NotGiven = NOT_GIVEN,
        start_date: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get usage events

        Args:
          end_date: End date for filtering (ISO 8601)

          event_type: Filter by event type

          group_id: Filter by group ID

          limit: Number of results to return

          offset: Offset for pagination

          resource_id: Filter by resource ID

          start_date: Start date for filtering (ISO 8601)

          user_id: Filter by user ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/api/v1/usage/events",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "end_date": end_date,
                        "event_type": event_type,
                        "group_id": group_id,
                        "limit": limit,
                        "offset": offset,
                        "resource_id": resource_id,
                        "start_date": start_date,
                        "user_id": user_id,
                    },
                    usage_list_events_params.UsageListEventsParams,
                ),
            ),
            cast_to=NoneType,
        )


class UsageResourceWithRawResponse:
    def __init__(self, usage: UsageResource) -> None:
        self._usage = usage

        self.get_stats = to_raw_response_wrapper(
            usage.get_stats,
        )
        self.get_summary = to_raw_response_wrapper(
            usage.get_summary,
        )
        self.list_events = to_raw_response_wrapper(
            usage.list_events,
        )


class AsyncUsageResourceWithRawResponse:
    def __init__(self, usage: AsyncUsageResource) -> None:
        self._usage = usage

        self.get_stats = async_to_raw_response_wrapper(
            usage.get_stats,
        )
        self.get_summary = async_to_raw_response_wrapper(
            usage.get_summary,
        )
        self.list_events = async_to_raw_response_wrapper(
            usage.list_events,
        )


class UsageResourceWithStreamingResponse:
    def __init__(self, usage: UsageResource) -> None:
        self._usage = usage

        self.get_stats = to_streamed_response_wrapper(
            usage.get_stats,
        )
        self.get_summary = to_streamed_response_wrapper(
            usage.get_summary,
        )
        self.list_events = to_streamed_response_wrapper(
            usage.list_events,
        )


class AsyncUsageResourceWithStreamingResponse:
    def __init__(self, usage: AsyncUsageResource) -> None:
        self._usage = usage

        self.get_stats = async_to_streamed_response_wrapper(
            usage.get_stats,
        )
        self.get_summary = async_to_streamed_response_wrapper(
            usage.get_summary,
        )
        self.list_events = async_to_streamed_response_wrapper(
            usage.list_events,
        )
