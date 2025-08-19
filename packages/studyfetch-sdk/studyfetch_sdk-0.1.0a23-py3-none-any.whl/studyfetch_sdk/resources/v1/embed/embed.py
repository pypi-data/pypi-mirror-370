# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from .component import (
    ComponentResource,
    AsyncComponentResource,
    ComponentResourceWithRawResponse,
    AsyncComponentResourceWithRawResponse,
    ComponentResourceWithStreamingResponse,
    AsyncComponentResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ....types.v1 import embed_verify_params, embed_get_theme_params
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options

__all__ = ["EmbedResource", "AsyncEmbedResource"]


class EmbedResource(SyncAPIResource):
    @cached_property
    def component(self) -> ComponentResource:
        return ComponentResource(self._client)

    @cached_property
    def with_raw_response(self) -> EmbedResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return EmbedResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EmbedResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return EmbedResourceWithStreamingResponse(self)

    def get_theme(
        self,
        *,
        token: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get theme CSS for embed

        Args:
          token: Embed token

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/api/v1/embed/theme",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"token": token}, embed_get_theme_params.EmbedGetThemeParams),
            ),
            cast_to=NoneType,
        )

    def health_check(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Health check endpoint"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/api/v1/embed/health",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def verify(
        self,
        *,
        token: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Verify embed token

        Args:
          token: Embed token to verify

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/api/v1/embed/verify",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"token": token}, embed_verify_params.EmbedVerifyParams),
            ),
            cast_to=NoneType,
        )


class AsyncEmbedResource(AsyncAPIResource):
    @cached_property
    def component(self) -> AsyncComponentResource:
        return AsyncComponentResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncEmbedResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncEmbedResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEmbedResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncEmbedResourceWithStreamingResponse(self)

    async def get_theme(
        self,
        *,
        token: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get theme CSS for embed

        Args:
          token: Embed token

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/api/v1/embed/theme",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"token": token}, embed_get_theme_params.EmbedGetThemeParams),
            ),
            cast_to=NoneType,
        )

    async def health_check(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Health check endpoint"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/api/v1/embed/health",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def verify(
        self,
        *,
        token: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Verify embed token

        Args:
          token: Embed token to verify

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/api/v1/embed/verify",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"token": token}, embed_verify_params.EmbedVerifyParams),
            ),
            cast_to=NoneType,
        )


class EmbedResourceWithRawResponse:
    def __init__(self, embed: EmbedResource) -> None:
        self._embed = embed

        self.get_theme = to_raw_response_wrapper(
            embed.get_theme,
        )
        self.health_check = to_raw_response_wrapper(
            embed.health_check,
        )
        self.verify = to_raw_response_wrapper(
            embed.verify,
        )

    @cached_property
    def component(self) -> ComponentResourceWithRawResponse:
        return ComponentResourceWithRawResponse(self._embed.component)


class AsyncEmbedResourceWithRawResponse:
    def __init__(self, embed: AsyncEmbedResource) -> None:
        self._embed = embed

        self.get_theme = async_to_raw_response_wrapper(
            embed.get_theme,
        )
        self.health_check = async_to_raw_response_wrapper(
            embed.health_check,
        )
        self.verify = async_to_raw_response_wrapper(
            embed.verify,
        )

    @cached_property
    def component(self) -> AsyncComponentResourceWithRawResponse:
        return AsyncComponentResourceWithRawResponse(self._embed.component)


class EmbedResourceWithStreamingResponse:
    def __init__(self, embed: EmbedResource) -> None:
        self._embed = embed

        self.get_theme = to_streamed_response_wrapper(
            embed.get_theme,
        )
        self.health_check = to_streamed_response_wrapper(
            embed.health_check,
        )
        self.verify = to_streamed_response_wrapper(
            embed.verify,
        )

    @cached_property
    def component(self) -> ComponentResourceWithStreamingResponse:
        return ComponentResourceWithStreamingResponse(self._embed.component)


class AsyncEmbedResourceWithStreamingResponse:
    def __init__(self, embed: AsyncEmbedResource) -> None:
        self._embed = embed

        self.get_theme = async_to_streamed_response_wrapper(
            embed.get_theme,
        )
        self.health_check = async_to_streamed_response_wrapper(
            embed.health_check,
        )
        self.verify = async_to_streamed_response_wrapper(
            embed.verify,
        )

    @cached_property
    def component(self) -> AsyncComponentResourceWithStreamingResponse:
        return AsyncComponentResourceWithStreamingResponse(self._embed.component)
