# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ...types.v1 import (
    usage_analyst_list_events_params,
    usage_analyst_get_test_questions_params,
    usage_analyst_list_chat_messages_params,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.v1.usage_analyst_list_chat_messages_response import UsageAnalystListChatMessagesResponse

__all__ = ["UsageAnalystResource", "AsyncUsageAnalystResource"]


class UsageAnalystResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UsageAnalystResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return UsageAnalystResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UsageAnalystResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return UsageAnalystResourceWithStreamingResponse(self)

    def get_test_questions(
        self,
        *,
        group_ids: List[str] | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get test results with full question data for user or group

        Args:
          group_ids: Array of group IDs to filter

          user_id: User ID to get test results for

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/api/v1/usage-analyst/test-questions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "group_ids": group_ids,
                        "user_id": user_id,
                    },
                    usage_analyst_get_test_questions_params.UsageAnalystGetTestQuestionsParams,
                ),
            ),
            cast_to=NoneType,
        )

    def list_chat_messages(
        self,
        *,
        group_ids: List[str] | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UsageAnalystListChatMessagesResponse:
        """
        Get all chat messages from sessions for user or group

        Args:
          group_ids: Array of group IDs to filter

          user_id: User ID to get chat messages for

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/usage-analyst/chat-messages",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "group_ids": group_ids,
                        "user_id": user_id,
                    },
                    usage_analyst_list_chat_messages_params.UsageAnalystListChatMessagesParams,
                ),
            ),
            cast_to=UsageAnalystListChatMessagesResponse,
        )

    def list_events(
        self,
        *,
        end_date: str,
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
        ],
        start_date: str,
        group_ids: List[str] | NotGiven = NOT_GIVEN,
        user_ids: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get all events based on filters

        Args:
          end_date: End date for filtering (ISO 8601)

          event_type: Type of usage event to filter

          start_date: Start date for filtering (ISO 8601)

          group_ids: Array of group IDs to filter

          user_ids: Array of user IDs to filter

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/api/v1/usage-analyst/events",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end_date": end_date,
                        "event_type": event_type,
                        "start_date": start_date,
                        "group_ids": group_ids,
                        "user_ids": user_ids,
                    },
                    usage_analyst_list_events_params.UsageAnalystListEventsParams,
                ),
            ),
            cast_to=NoneType,
        )


class AsyncUsageAnalystResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUsageAnalystResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncUsageAnalystResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUsageAnalystResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncUsageAnalystResourceWithStreamingResponse(self)

    async def get_test_questions(
        self,
        *,
        group_ids: List[str] | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get test results with full question data for user or group

        Args:
          group_ids: Array of group IDs to filter

          user_id: User ID to get test results for

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/api/v1/usage-analyst/test-questions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "group_ids": group_ids,
                        "user_id": user_id,
                    },
                    usage_analyst_get_test_questions_params.UsageAnalystGetTestQuestionsParams,
                ),
            ),
            cast_to=NoneType,
        )

    async def list_chat_messages(
        self,
        *,
        group_ids: List[str] | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UsageAnalystListChatMessagesResponse:
        """
        Get all chat messages from sessions for user or group

        Args:
          group_ids: Array of group IDs to filter

          user_id: User ID to get chat messages for

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/usage-analyst/chat-messages",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "group_ids": group_ids,
                        "user_id": user_id,
                    },
                    usage_analyst_list_chat_messages_params.UsageAnalystListChatMessagesParams,
                ),
            ),
            cast_to=UsageAnalystListChatMessagesResponse,
        )

    async def list_events(
        self,
        *,
        end_date: str,
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
        ],
        start_date: str,
        group_ids: List[str] | NotGiven = NOT_GIVEN,
        user_ids: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get all events based on filters

        Args:
          end_date: End date for filtering (ISO 8601)

          event_type: Type of usage event to filter

          start_date: Start date for filtering (ISO 8601)

          group_ids: Array of group IDs to filter

          user_ids: Array of user IDs to filter

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/api/v1/usage-analyst/events",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "end_date": end_date,
                        "event_type": event_type,
                        "start_date": start_date,
                        "group_ids": group_ids,
                        "user_ids": user_ids,
                    },
                    usage_analyst_list_events_params.UsageAnalystListEventsParams,
                ),
            ),
            cast_to=NoneType,
        )


class UsageAnalystResourceWithRawResponse:
    def __init__(self, usage_analyst: UsageAnalystResource) -> None:
        self._usage_analyst = usage_analyst

        self.get_test_questions = to_raw_response_wrapper(
            usage_analyst.get_test_questions,
        )
        self.list_chat_messages = to_raw_response_wrapper(
            usage_analyst.list_chat_messages,
        )
        self.list_events = to_raw_response_wrapper(
            usage_analyst.list_events,
        )


class AsyncUsageAnalystResourceWithRawResponse:
    def __init__(self, usage_analyst: AsyncUsageAnalystResource) -> None:
        self._usage_analyst = usage_analyst

        self.get_test_questions = async_to_raw_response_wrapper(
            usage_analyst.get_test_questions,
        )
        self.list_chat_messages = async_to_raw_response_wrapper(
            usage_analyst.list_chat_messages,
        )
        self.list_events = async_to_raw_response_wrapper(
            usage_analyst.list_events,
        )


class UsageAnalystResourceWithStreamingResponse:
    def __init__(self, usage_analyst: UsageAnalystResource) -> None:
        self._usage_analyst = usage_analyst

        self.get_test_questions = to_streamed_response_wrapper(
            usage_analyst.get_test_questions,
        )
        self.list_chat_messages = to_streamed_response_wrapper(
            usage_analyst.list_chat_messages,
        )
        self.list_events = to_streamed_response_wrapper(
            usage_analyst.list_events,
        )


class AsyncUsageAnalystResourceWithStreamingResponse:
    def __init__(self, usage_analyst: AsyncUsageAnalystResource) -> None:
        self._usage_analyst = usage_analyst

        self.get_test_questions = async_to_streamed_response_wrapper(
            usage_analyst.get_test_questions,
        )
        self.list_chat_messages = async_to_streamed_response_wrapper(
            usage_analyst.list_chat_messages,
        )
        self.list_events = async_to_streamed_response_wrapper(
            usage_analyst.list_events,
        )
