# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from datetime import datetime

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ...types.v1 import chat_analytic_export_params, chat_analytic_analyze_params, chat_analytic_get_component_params
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.v1.chat_analytics_response import ChatAnalyticsResponse

__all__ = ["ChatAnalyticsResource", "AsyncChatAnalyticsResource"]


class ChatAnalyticsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ChatAnalyticsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ChatAnalyticsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ChatAnalyticsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return ChatAnalyticsResourceWithStreamingResponse(self)

    def analyze(
        self,
        *,
        component_id: str | NotGiven = NOT_GIVEN,
        end_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        group_ids: List[str] | NotGiven = NOT_GIVEN,
        model_key: str | NotGiven = NOT_GIVEN,
        organization_id: str | NotGiven = NOT_GIVEN,
        start_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatAnalyticsResponse:
        """
        Get chat analytics and user statistics

        Args:
          component_id: Component ID to analyze

          end_date: End date for analysis

          group_ids: Group IDs to filter by

          model_key: AI model to use for analysis

          organization_id: Organization ID to filter by

          start_date: Start date for analysis

          user_id: User ID to filter by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/chat-analytics/analyze",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "component_id": component_id,
                        "end_date": end_date,
                        "group_ids": group_ids,
                        "model_key": model_key,
                        "organization_id": organization_id,
                        "start_date": start_date,
                        "user_id": user_id,
                    },
                    chat_analytic_analyze_params.ChatAnalyticAnalyzeParams,
                ),
            ),
            cast_to=ChatAnalyticsResponse,
        )

    def export(
        self,
        *,
        component_id: str | NotGiven = NOT_GIVEN,
        end_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        group_ids: List[str] | NotGiven = NOT_GIVEN,
        model_key: str | NotGiven = NOT_GIVEN,
        organization_id: str | NotGiven = NOT_GIVEN,
        start_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Export chat analytics data as CSV

        Args:
          component_id: Component ID to analyze

          end_date: End date for analysis

          group_ids: Group IDs to filter by

          model_key: AI model to use for analysis

          organization_id: Organization ID to filter by

          start_date: Start date for analysis

          user_id: User ID to filter by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "text/csv", **(extra_headers or {})}
        return self._get(
            "/api/v1/chat-analytics/export",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "component_id": component_id,
                        "end_date": end_date,
                        "group_ids": group_ids,
                        "model_key": model_key,
                        "organization_id": organization_id,
                        "start_date": start_date,
                        "user_id": user_id,
                    },
                    chat_analytic_export_params.ChatAnalyticExportParams,
                ),
            ),
            cast_to=str,
        )

    def get_component(
        self,
        component_id: str,
        *,
        end_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        group_ids: List[str] | NotGiven = NOT_GIVEN,
        model_key: str | NotGiven = NOT_GIVEN,
        organization_id: str | NotGiven = NOT_GIVEN,
        start_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatAnalyticsResponse:
        """
        Get chat analytics for a specific component

        Args:
          end_date: End date for analysis

          group_ids: Group IDs to filter by

          model_key: AI model to use for analysis

          organization_id: Organization ID to filter by

          start_date: Start date for analysis

          user_id: User ID to filter by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        return self._get(
            f"/api/v1/chat-analytics/component/{component_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end_date": end_date,
                        "group_ids": group_ids,
                        "model_key": model_key,
                        "organization_id": organization_id,
                        "start_date": start_date,
                        "user_id": user_id,
                    },
                    chat_analytic_get_component_params.ChatAnalyticGetComponentParams,
                ),
            ),
            cast_to=ChatAnalyticsResponse,
        )


class AsyncChatAnalyticsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncChatAnalyticsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncChatAnalyticsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncChatAnalyticsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncChatAnalyticsResourceWithStreamingResponse(self)

    async def analyze(
        self,
        *,
        component_id: str | NotGiven = NOT_GIVEN,
        end_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        group_ids: List[str] | NotGiven = NOT_GIVEN,
        model_key: str | NotGiven = NOT_GIVEN,
        organization_id: str | NotGiven = NOT_GIVEN,
        start_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatAnalyticsResponse:
        """
        Get chat analytics and user statistics

        Args:
          component_id: Component ID to analyze

          end_date: End date for analysis

          group_ids: Group IDs to filter by

          model_key: AI model to use for analysis

          organization_id: Organization ID to filter by

          start_date: Start date for analysis

          user_id: User ID to filter by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/chat-analytics/analyze",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "component_id": component_id,
                        "end_date": end_date,
                        "group_ids": group_ids,
                        "model_key": model_key,
                        "organization_id": organization_id,
                        "start_date": start_date,
                        "user_id": user_id,
                    },
                    chat_analytic_analyze_params.ChatAnalyticAnalyzeParams,
                ),
            ),
            cast_to=ChatAnalyticsResponse,
        )

    async def export(
        self,
        *,
        component_id: str | NotGiven = NOT_GIVEN,
        end_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        group_ids: List[str] | NotGiven = NOT_GIVEN,
        model_key: str | NotGiven = NOT_GIVEN,
        organization_id: str | NotGiven = NOT_GIVEN,
        start_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Export chat analytics data as CSV

        Args:
          component_id: Component ID to analyze

          end_date: End date for analysis

          group_ids: Group IDs to filter by

          model_key: AI model to use for analysis

          organization_id: Organization ID to filter by

          start_date: Start date for analysis

          user_id: User ID to filter by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "text/csv", **(extra_headers or {})}
        return await self._get(
            "/api/v1/chat-analytics/export",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "component_id": component_id,
                        "end_date": end_date,
                        "group_ids": group_ids,
                        "model_key": model_key,
                        "organization_id": organization_id,
                        "start_date": start_date,
                        "user_id": user_id,
                    },
                    chat_analytic_export_params.ChatAnalyticExportParams,
                ),
            ),
            cast_to=str,
        )

    async def get_component(
        self,
        component_id: str,
        *,
        end_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        group_ids: List[str] | NotGiven = NOT_GIVEN,
        model_key: str | NotGiven = NOT_GIVEN,
        organization_id: str | NotGiven = NOT_GIVEN,
        start_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatAnalyticsResponse:
        """
        Get chat analytics for a specific component

        Args:
          end_date: End date for analysis

          group_ids: Group IDs to filter by

          model_key: AI model to use for analysis

          organization_id: Organization ID to filter by

          start_date: Start date for analysis

          user_id: User ID to filter by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        return await self._get(
            f"/api/v1/chat-analytics/component/{component_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "end_date": end_date,
                        "group_ids": group_ids,
                        "model_key": model_key,
                        "organization_id": organization_id,
                        "start_date": start_date,
                        "user_id": user_id,
                    },
                    chat_analytic_get_component_params.ChatAnalyticGetComponentParams,
                ),
            ),
            cast_to=ChatAnalyticsResponse,
        )


class ChatAnalyticsResourceWithRawResponse:
    def __init__(self, chat_analytics: ChatAnalyticsResource) -> None:
        self._chat_analytics = chat_analytics

        self.analyze = to_raw_response_wrapper(
            chat_analytics.analyze,
        )
        self.export = to_raw_response_wrapper(
            chat_analytics.export,
        )
        self.get_component = to_raw_response_wrapper(
            chat_analytics.get_component,
        )


class AsyncChatAnalyticsResourceWithRawResponse:
    def __init__(self, chat_analytics: AsyncChatAnalyticsResource) -> None:
        self._chat_analytics = chat_analytics

        self.analyze = async_to_raw_response_wrapper(
            chat_analytics.analyze,
        )
        self.export = async_to_raw_response_wrapper(
            chat_analytics.export,
        )
        self.get_component = async_to_raw_response_wrapper(
            chat_analytics.get_component,
        )


class ChatAnalyticsResourceWithStreamingResponse:
    def __init__(self, chat_analytics: ChatAnalyticsResource) -> None:
        self._chat_analytics = chat_analytics

        self.analyze = to_streamed_response_wrapper(
            chat_analytics.analyze,
        )
        self.export = to_streamed_response_wrapper(
            chat_analytics.export,
        )
        self.get_component = to_streamed_response_wrapper(
            chat_analytics.get_component,
        )


class AsyncChatAnalyticsResourceWithStreamingResponse:
    def __init__(self, chat_analytics: AsyncChatAnalyticsResource) -> None:
        self._chat_analytics = chat_analytics

        self.analyze = async_to_streamed_response_wrapper(
            chat_analytics.analyze,
        )
        self.export = async_to_streamed_response_wrapper(
            chat_analytics.export,
        )
        self.get_component = async_to_streamed_response_wrapper(
            chat_analytics.get_component,
        )
