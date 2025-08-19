# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .chat import (
    ChatResource,
    AsyncChatResource,
    ChatResourceWithRawResponse,
    AsyncChatResourceWithRawResponse,
    ChatResourceWithStreamingResponse,
    AsyncChatResourceWithStreamingResponse,
)
from .usage import (
    UsageResource,
    AsyncUsageResource,
    UsageResourceWithRawResponse,
    AsyncUsageResourceWithRawResponse,
    UsageResourceWithStreamingResponse,
    AsyncUsageResourceWithStreamingResponse,
)
from .folders import (
    FoldersResource,
    AsyncFoldersResource,
    FoldersResourceWithRawResponse,
    AsyncFoldersResourceWithRawResponse,
    FoldersResourceWithStreamingResponse,
    AsyncFoldersResourceWithStreamingResponse,
)
from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._compat import cached_property
from .components import (
    ComponentsResource,
    AsyncComponentsResource,
    ComponentsResourceWithRawResponse,
    AsyncComponentsResourceWithRawResponse,
    ComponentsResourceWithStreamingResponse,
    AsyncComponentsResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .embed.embed import (
    EmbedResource,
    AsyncEmbedResource,
    EmbedResourceWithRawResponse,
    AsyncEmbedResourceWithRawResponse,
    EmbedResourceWithStreamingResponse,
    AsyncEmbedResourceWithStreamingResponse,
)
from .usage_analyst import (
    UsageAnalystResource,
    AsyncUsageAnalystResource,
    UsageAnalystResourceWithRawResponse,
    AsyncUsageAnalystResourceWithRawResponse,
    UsageAnalystResourceWithStreamingResponse,
    AsyncUsageAnalystResourceWithStreamingResponse,
)
from ..._base_client import make_request_options
from .chat_analytics import (
    ChatAnalyticsResource,
    AsyncChatAnalyticsResource,
    ChatAnalyticsResourceWithRawResponse,
    AsyncChatAnalyticsResourceWithRawResponse,
    ChatAnalyticsResourceWithStreamingResponse,
    AsyncChatAnalyticsResourceWithStreamingResponse,
)
from .materials.materials import (
    MaterialsResource,
    AsyncMaterialsResource,
    MaterialsResourceWithRawResponse,
    AsyncMaterialsResourceWithRawResponse,
    MaterialsResourceWithStreamingResponse,
    AsyncMaterialsResourceWithStreamingResponse,
)
from .assignment_grader.assignment_grader import (
    AssignmentGraderResource,
    AsyncAssignmentGraderResource,
    AssignmentGraderResourceWithRawResponse,
    AsyncAssignmentGraderResourceWithRawResponse,
    AssignmentGraderResourceWithStreamingResponse,
    AsyncAssignmentGraderResourceWithStreamingResponse,
)

__all__ = ["V1Resource", "AsyncV1Resource"]


class V1Resource(SyncAPIResource):
    @cached_property
    def materials(self) -> MaterialsResource:
        return MaterialsResource(self._client)

    @cached_property
    def folders(self) -> FoldersResource:
        return FoldersResource(self._client)

    @cached_property
    def components(self) -> ComponentsResource:
        return ComponentsResource(self._client)

    @cached_property
    def usage(self) -> UsageResource:
        return UsageResource(self._client)

    @cached_property
    def usage_analyst(self) -> UsageAnalystResource:
        return UsageAnalystResource(self._client)

    @cached_property
    def embed(self) -> EmbedResource:
        return EmbedResource(self._client)

    @cached_property
    def chat(self) -> ChatResource:
        return ChatResource(self._client)

    @cached_property
    def chat_analytics(self) -> ChatAnalyticsResource:
        return ChatAnalyticsResource(self._client)

    @cached_property
    def assignment_grader(self) -> AssignmentGraderResource:
        return AssignmentGraderResource(self._client)

    @cached_property
    def with_raw_response(self) -> V1ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return V1ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> V1ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return V1ResourceWithStreamingResponse(self)

    def test_mongodb(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Test MongoDB connection and get outbound IP"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/api/v1/test-mongodb",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncV1Resource(AsyncAPIResource):
    @cached_property
    def materials(self) -> AsyncMaterialsResource:
        return AsyncMaterialsResource(self._client)

    @cached_property
    def folders(self) -> AsyncFoldersResource:
        return AsyncFoldersResource(self._client)

    @cached_property
    def components(self) -> AsyncComponentsResource:
        return AsyncComponentsResource(self._client)

    @cached_property
    def usage(self) -> AsyncUsageResource:
        return AsyncUsageResource(self._client)

    @cached_property
    def usage_analyst(self) -> AsyncUsageAnalystResource:
        return AsyncUsageAnalystResource(self._client)

    @cached_property
    def embed(self) -> AsyncEmbedResource:
        return AsyncEmbedResource(self._client)

    @cached_property
    def chat(self) -> AsyncChatResource:
        return AsyncChatResource(self._client)

    @cached_property
    def chat_analytics(self) -> AsyncChatAnalyticsResource:
        return AsyncChatAnalyticsResource(self._client)

    @cached_property
    def assignment_grader(self) -> AsyncAssignmentGraderResource:
        return AsyncAssignmentGraderResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncV1ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncV1ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncV1ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncV1ResourceWithStreamingResponse(self)

    async def test_mongodb(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Test MongoDB connection and get outbound IP"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/api/v1/test-mongodb",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class V1ResourceWithRawResponse:
    def __init__(self, v1: V1Resource) -> None:
        self._v1 = v1

        self.test_mongodb = to_raw_response_wrapper(
            v1.test_mongodb,
        )

    @cached_property
    def materials(self) -> MaterialsResourceWithRawResponse:
        return MaterialsResourceWithRawResponse(self._v1.materials)

    @cached_property
    def folders(self) -> FoldersResourceWithRawResponse:
        return FoldersResourceWithRawResponse(self._v1.folders)

    @cached_property
    def components(self) -> ComponentsResourceWithRawResponse:
        return ComponentsResourceWithRawResponse(self._v1.components)

    @cached_property
    def usage(self) -> UsageResourceWithRawResponse:
        return UsageResourceWithRawResponse(self._v1.usage)

    @cached_property
    def usage_analyst(self) -> UsageAnalystResourceWithRawResponse:
        return UsageAnalystResourceWithRawResponse(self._v1.usage_analyst)

    @cached_property
    def embed(self) -> EmbedResourceWithRawResponse:
        return EmbedResourceWithRawResponse(self._v1.embed)

    @cached_property
    def chat(self) -> ChatResourceWithRawResponse:
        return ChatResourceWithRawResponse(self._v1.chat)

    @cached_property
    def chat_analytics(self) -> ChatAnalyticsResourceWithRawResponse:
        return ChatAnalyticsResourceWithRawResponse(self._v1.chat_analytics)

    @cached_property
    def assignment_grader(self) -> AssignmentGraderResourceWithRawResponse:
        return AssignmentGraderResourceWithRawResponse(self._v1.assignment_grader)


class AsyncV1ResourceWithRawResponse:
    def __init__(self, v1: AsyncV1Resource) -> None:
        self._v1 = v1

        self.test_mongodb = async_to_raw_response_wrapper(
            v1.test_mongodb,
        )

    @cached_property
    def materials(self) -> AsyncMaterialsResourceWithRawResponse:
        return AsyncMaterialsResourceWithRawResponse(self._v1.materials)

    @cached_property
    def folders(self) -> AsyncFoldersResourceWithRawResponse:
        return AsyncFoldersResourceWithRawResponse(self._v1.folders)

    @cached_property
    def components(self) -> AsyncComponentsResourceWithRawResponse:
        return AsyncComponentsResourceWithRawResponse(self._v1.components)

    @cached_property
    def usage(self) -> AsyncUsageResourceWithRawResponse:
        return AsyncUsageResourceWithRawResponse(self._v1.usage)

    @cached_property
    def usage_analyst(self) -> AsyncUsageAnalystResourceWithRawResponse:
        return AsyncUsageAnalystResourceWithRawResponse(self._v1.usage_analyst)

    @cached_property
    def embed(self) -> AsyncEmbedResourceWithRawResponse:
        return AsyncEmbedResourceWithRawResponse(self._v1.embed)

    @cached_property
    def chat(self) -> AsyncChatResourceWithRawResponse:
        return AsyncChatResourceWithRawResponse(self._v1.chat)

    @cached_property
    def chat_analytics(self) -> AsyncChatAnalyticsResourceWithRawResponse:
        return AsyncChatAnalyticsResourceWithRawResponse(self._v1.chat_analytics)

    @cached_property
    def assignment_grader(self) -> AsyncAssignmentGraderResourceWithRawResponse:
        return AsyncAssignmentGraderResourceWithRawResponse(self._v1.assignment_grader)


class V1ResourceWithStreamingResponse:
    def __init__(self, v1: V1Resource) -> None:
        self._v1 = v1

        self.test_mongodb = to_streamed_response_wrapper(
            v1.test_mongodb,
        )

    @cached_property
    def materials(self) -> MaterialsResourceWithStreamingResponse:
        return MaterialsResourceWithStreamingResponse(self._v1.materials)

    @cached_property
    def folders(self) -> FoldersResourceWithStreamingResponse:
        return FoldersResourceWithStreamingResponse(self._v1.folders)

    @cached_property
    def components(self) -> ComponentsResourceWithStreamingResponse:
        return ComponentsResourceWithStreamingResponse(self._v1.components)

    @cached_property
    def usage(self) -> UsageResourceWithStreamingResponse:
        return UsageResourceWithStreamingResponse(self._v1.usage)

    @cached_property
    def usage_analyst(self) -> UsageAnalystResourceWithStreamingResponse:
        return UsageAnalystResourceWithStreamingResponse(self._v1.usage_analyst)

    @cached_property
    def embed(self) -> EmbedResourceWithStreamingResponse:
        return EmbedResourceWithStreamingResponse(self._v1.embed)

    @cached_property
    def chat(self) -> ChatResourceWithStreamingResponse:
        return ChatResourceWithStreamingResponse(self._v1.chat)

    @cached_property
    def chat_analytics(self) -> ChatAnalyticsResourceWithStreamingResponse:
        return ChatAnalyticsResourceWithStreamingResponse(self._v1.chat_analytics)

    @cached_property
    def assignment_grader(self) -> AssignmentGraderResourceWithStreamingResponse:
        return AssignmentGraderResourceWithStreamingResponse(self._v1.assignment_grader)


class AsyncV1ResourceWithStreamingResponse:
    def __init__(self, v1: AsyncV1Resource) -> None:
        self._v1 = v1

        self.test_mongodb = async_to_streamed_response_wrapper(
            v1.test_mongodb,
        )

    @cached_property
    def materials(self) -> AsyncMaterialsResourceWithStreamingResponse:
        return AsyncMaterialsResourceWithStreamingResponse(self._v1.materials)

    @cached_property
    def folders(self) -> AsyncFoldersResourceWithStreamingResponse:
        return AsyncFoldersResourceWithStreamingResponse(self._v1.folders)

    @cached_property
    def components(self) -> AsyncComponentsResourceWithStreamingResponse:
        return AsyncComponentsResourceWithStreamingResponse(self._v1.components)

    @cached_property
    def usage(self) -> AsyncUsageResourceWithStreamingResponse:
        return AsyncUsageResourceWithStreamingResponse(self._v1.usage)

    @cached_property
    def usage_analyst(self) -> AsyncUsageAnalystResourceWithStreamingResponse:
        return AsyncUsageAnalystResourceWithStreamingResponse(self._v1.usage_analyst)

    @cached_property
    def embed(self) -> AsyncEmbedResourceWithStreamingResponse:
        return AsyncEmbedResourceWithStreamingResponse(self._v1.embed)

    @cached_property
    def chat(self) -> AsyncChatResourceWithStreamingResponse:
        return AsyncChatResourceWithStreamingResponse(self._v1.chat)

    @cached_property
    def chat_analytics(self) -> AsyncChatAnalyticsResourceWithStreamingResponse:
        return AsyncChatAnalyticsResourceWithStreamingResponse(self._v1.chat_analytics)

    @cached_property
    def assignment_grader(self) -> AsyncAssignmentGraderResourceWithStreamingResponse:
        return AsyncAssignmentGraderResourceWithStreamingResponse(self._v1.assignment_grader)
