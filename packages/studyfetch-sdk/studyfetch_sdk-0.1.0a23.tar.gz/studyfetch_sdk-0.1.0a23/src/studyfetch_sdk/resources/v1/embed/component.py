# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

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
from ....types.v1.embed import component_interact_params, component_retrieve_params

__all__ = ["ComponentResource", "AsyncComponentResource"]


class ComponentResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ComponentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ComponentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ComponentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return ComponentResourceWithStreamingResponse(self)

    def retrieve(
        self,
        component_id: str,
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
        Get component data for embed

        Args:
          token: Embed token

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/api/v1/embed/component/{component_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"token": token}, component_retrieve_params.ComponentRetrieveParams),
            ),
            cast_to=NoneType,
        )

    def interact(
        self,
        component_id: str,
        *,
        token: str,
        body: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Process embed interaction

        Args:
          token: Embed token

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/api/v1/embed/component/{component_id}/interact",
            body=maybe_transform(body, component_interact_params.ComponentInteractParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"token": token}, component_interact_params.ComponentInteractParams),
            ),
            cast_to=NoneType,
        )


class AsyncComponentResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncComponentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncComponentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncComponentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncComponentResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        component_id: str,
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
        Get component data for embed

        Args:
          token: Embed token

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/api/v1/embed/component/{component_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"token": token}, component_retrieve_params.ComponentRetrieveParams),
            ),
            cast_to=NoneType,
        )

    async def interact(
        self,
        component_id: str,
        *,
        token: str,
        body: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Process embed interaction

        Args:
          token: Embed token

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/api/v1/embed/component/{component_id}/interact",
            body=await async_maybe_transform(body, component_interact_params.ComponentInteractParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"token": token}, component_interact_params.ComponentInteractParams),
            ),
            cast_to=NoneType,
        )


class ComponentResourceWithRawResponse:
    def __init__(self, component: ComponentResource) -> None:
        self._component = component

        self.retrieve = to_raw_response_wrapper(
            component.retrieve,
        )
        self.interact = to_raw_response_wrapper(
            component.interact,
        )


class AsyncComponentResourceWithRawResponse:
    def __init__(self, component: AsyncComponentResource) -> None:
        self._component = component

        self.retrieve = async_to_raw_response_wrapper(
            component.retrieve,
        )
        self.interact = async_to_raw_response_wrapper(
            component.interact,
        )


class ComponentResourceWithStreamingResponse:
    def __init__(self, component: ComponentResource) -> None:
        self._component = component

        self.retrieve = to_streamed_response_wrapper(
            component.retrieve,
        )
        self.interact = to_streamed_response_wrapper(
            component.interact,
        )


class AsyncComponentResourceWithStreamingResponse:
    def __init__(self, component: AsyncComponentResource) -> None:
        self._component = component

        self.retrieve = async_to_streamed_response_wrapper(
            component.retrieve,
        )
        self.interact = async_to_streamed_response_wrapper(
            component.interact,
        )
