# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, strip_not_given, async_maybe_transform
from ..._compat import cached_property
from ...types.v1 import chat_stream_params
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options

__all__ = ["ChatResource", "AsyncChatResource"]


class ChatResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ChatResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ChatResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ChatResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return ChatResourceWithStreamingResponse(self)

    def stream(
        self,
        *,
        id: str | NotGiven = NOT_GIVEN,
        component_id: str | NotGiven = NOT_GIVEN,
        context: object | NotGiven = NOT_GIVEN,
        group_ids: List[str] | NotGiven = NOT_GIVEN,
        message: chat_stream_params.Message | NotGiven = NOT_GIVEN,
        messages: List[str] | NotGiven = NOT_GIVEN,
        session_id: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        x_component_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Streams a chat response in real-time using server-sent events (SSE).

        Supports
        both AI SDK format (with messages array) and custom format (with message
        object).

        Args:
          id: Session ID (AI SDK uses "id")

          component_id: Component ID

          context: Additional context

          group_ids: Group IDs for access control

          message: Single message for custom format - contains text and optional images

          messages: Messages array for AI SDK format - list of conversation messages with roles

          session_id: Session ID

          user_id: User ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {**strip_not_given({"x-component-id": x_component_id}), **(extra_headers or {})}
        return self._post(
            "/api/v1/chat/stream",
            body=maybe_transform(
                {
                    "id": id,
                    "component_id": component_id,
                    "context": context,
                    "group_ids": group_ids,
                    "message": message,
                    "messages": messages,
                    "session_id": session_id,
                    "user_id": user_id,
                },
                chat_stream_params.ChatStreamParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncChatResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncChatResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncChatResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncChatResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncChatResourceWithStreamingResponse(self)

    async def stream(
        self,
        *,
        id: str | NotGiven = NOT_GIVEN,
        component_id: str | NotGiven = NOT_GIVEN,
        context: object | NotGiven = NOT_GIVEN,
        group_ids: List[str] | NotGiven = NOT_GIVEN,
        message: chat_stream_params.Message | NotGiven = NOT_GIVEN,
        messages: List[str] | NotGiven = NOT_GIVEN,
        session_id: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        x_component_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Streams a chat response in real-time using server-sent events (SSE).

        Supports
        both AI SDK format (with messages array) and custom format (with message
        object).

        Args:
          id: Session ID (AI SDK uses "id")

          component_id: Component ID

          context: Additional context

          group_ids: Group IDs for access control

          message: Single message for custom format - contains text and optional images

          messages: Messages array for AI SDK format - list of conversation messages with roles

          session_id: Session ID

          user_id: User ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {**strip_not_given({"x-component-id": x_component_id}), **(extra_headers or {})}
        return await self._post(
            "/api/v1/chat/stream",
            body=await async_maybe_transform(
                {
                    "id": id,
                    "component_id": component_id,
                    "context": context,
                    "group_ids": group_ids,
                    "message": message,
                    "messages": messages,
                    "session_id": session_id,
                    "user_id": user_id,
                },
                chat_stream_params.ChatStreamParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class ChatResourceWithRawResponse:
    def __init__(self, chat: ChatResource) -> None:
        self._chat = chat

        self.stream = to_raw_response_wrapper(
            chat.stream,
        )


class AsyncChatResourceWithRawResponse:
    def __init__(self, chat: AsyncChatResource) -> None:
        self._chat = chat

        self.stream = async_to_raw_response_wrapper(
            chat.stream,
        )


class ChatResourceWithStreamingResponse:
    def __init__(self, chat: ChatResource) -> None:
        self._chat = chat

        self.stream = to_streamed_response_wrapper(
            chat.stream,
        )


class AsyncChatResourceWithStreamingResponse:
    def __init__(self, chat: AsyncChatResource) -> None:
        self._chat = chat

        self.stream = async_to_streamed_response_wrapper(
            chat.stream,
        )
