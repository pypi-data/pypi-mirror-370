# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ...types.v1 import (
    component_list_params,
    component_create_params,
    component_update_params,
    component_generate_embed_params,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.v1.component_response import ComponentResponse
from ...types.v1.component_list_response import ComponentListResponse
from ...types.v1.component_generate_embed_response import ComponentGenerateEmbedResponse

__all__ = ["ComponentsResource", "AsyncComponentsResource"]


class ComponentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ComponentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ComponentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ComponentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return ComponentsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        config: component_create_params.Config,
        name: str,
        type: Literal[
            "chat",
            "data_analyst",
            "flashcards",
            "scenarios",
            "practice_test",
            "audio_recap",
            "tutor_me",
            "explainers",
            "uploads",
            "chat_analytics",
        ],
        description: str | NotGiven = NOT_GIVEN,
        metadata: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ComponentResponse:
        """
        Create a new component

        Args:
          config: Component-specific configuration

          name: Name of the component

          type: Type of component to create

          description: Component description

          metadata: Additional metadata

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/components",
            body=maybe_transform(
                {
                    "config": config,
                    "name": name,
                    "type": type,
                    "description": description,
                    "metadata": metadata,
                },
                component_create_params.ComponentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComponentResponse,
        )

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ComponentResponse:
        """
        Get component by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/api/v1/components/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComponentResponse,
        )

    def update(
        self,
        id: str,
        *,
        status: Literal["draft", "active", "inactive", "processing", "error"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ComponentResponse:
        """
        Update component

        Args:
          status: Component status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/api/v1/components/{id}",
            body=maybe_transform({"status": status}, component_update_params.ComponentUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComponentResponse,
        )

    def list(
        self,
        *,
        type: Literal[
            "chat",
            "data_analyst",
            "flashcards",
            "scenarios",
            "practice_test",
            "audio_recap",
            "tutor_me",
            "explainers",
            "uploads",
            "chat_analytics",
        ]
        | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ComponentListResponse:
        """
        Get all components

        Args:
          type: Filter by component type

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/components",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"type": type}, component_list_params.ComponentListParams),
            ),
            cast_to=ComponentListResponse,
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
        Delete component

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
            f"/api/v1/components/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def activate(
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
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/api/v1/components/{id}/activate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def deactivate(
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
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/api/v1/components/{id}/deactivate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def generate_embed(
        self,
        id: str,
        *,
        expiry_hours: float | NotGiven = NOT_GIVEN,
        features: component_generate_embed_params.Features | NotGiven = NOT_GIVEN,
        group_ids: List[str] | NotGiven = NOT_GIVEN,
        height: str | NotGiven = NOT_GIVEN,
        session_id: str | NotGiven = NOT_GIVEN,
        theme: component_generate_embed_params.Theme | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        width: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ComponentGenerateEmbedResponse:
        """
        Generate embed code for component

        Args:
          expiry_hours: Token expiry time in hours

          features: Feature toggles

          group_ids: Group IDs for collaboration

          height: Embed height (e.g., "400px", "100vh")

          session_id: Session ID for continuity

          theme: Theme customization

          user_id: User ID for tracking

          width: Embed width (e.g., "100%", "600px")

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/api/v1/components/{id}/embed",
            body=maybe_transform(
                {
                    "expiry_hours": expiry_hours,
                    "features": features,
                    "group_ids": group_ids,
                    "height": height,
                    "session_id": session_id,
                    "theme": theme,
                    "user_id": user_id,
                    "width": width,
                },
                component_generate_embed_params.ComponentGenerateEmbedParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComponentGenerateEmbedResponse,
        )

    def interact(
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
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/api/v1/components/{id}/interact",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncComponentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncComponentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncComponentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncComponentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncComponentsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        config: component_create_params.Config,
        name: str,
        type: Literal[
            "chat",
            "data_analyst",
            "flashcards",
            "scenarios",
            "practice_test",
            "audio_recap",
            "tutor_me",
            "explainers",
            "uploads",
            "chat_analytics",
        ],
        description: str | NotGiven = NOT_GIVEN,
        metadata: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ComponentResponse:
        """
        Create a new component

        Args:
          config: Component-specific configuration

          name: Name of the component

          type: Type of component to create

          description: Component description

          metadata: Additional metadata

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/components",
            body=await async_maybe_transform(
                {
                    "config": config,
                    "name": name,
                    "type": type,
                    "description": description,
                    "metadata": metadata,
                },
                component_create_params.ComponentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComponentResponse,
        )

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ComponentResponse:
        """
        Get component by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/api/v1/components/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComponentResponse,
        )

    async def update(
        self,
        id: str,
        *,
        status: Literal["draft", "active", "inactive", "processing", "error"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ComponentResponse:
        """
        Update component

        Args:
          status: Component status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/api/v1/components/{id}",
            body=await async_maybe_transform({"status": status}, component_update_params.ComponentUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComponentResponse,
        )

    async def list(
        self,
        *,
        type: Literal[
            "chat",
            "data_analyst",
            "flashcards",
            "scenarios",
            "practice_test",
            "audio_recap",
            "tutor_me",
            "explainers",
            "uploads",
            "chat_analytics",
        ]
        | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ComponentListResponse:
        """
        Get all components

        Args:
          type: Filter by component type

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/components",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"type": type}, component_list_params.ComponentListParams),
            ),
            cast_to=ComponentListResponse,
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
        Delete component

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
            f"/api/v1/components/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def activate(
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
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/api/v1/components/{id}/activate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def deactivate(
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
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/api/v1/components/{id}/deactivate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def generate_embed(
        self,
        id: str,
        *,
        expiry_hours: float | NotGiven = NOT_GIVEN,
        features: component_generate_embed_params.Features | NotGiven = NOT_GIVEN,
        group_ids: List[str] | NotGiven = NOT_GIVEN,
        height: str | NotGiven = NOT_GIVEN,
        session_id: str | NotGiven = NOT_GIVEN,
        theme: component_generate_embed_params.Theme | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        width: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ComponentGenerateEmbedResponse:
        """
        Generate embed code for component

        Args:
          expiry_hours: Token expiry time in hours

          features: Feature toggles

          group_ids: Group IDs for collaboration

          height: Embed height (e.g., "400px", "100vh")

          session_id: Session ID for continuity

          theme: Theme customization

          user_id: User ID for tracking

          width: Embed width (e.g., "100%", "600px")

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/api/v1/components/{id}/embed",
            body=await async_maybe_transform(
                {
                    "expiry_hours": expiry_hours,
                    "features": features,
                    "group_ids": group_ids,
                    "height": height,
                    "session_id": session_id,
                    "theme": theme,
                    "user_id": user_id,
                    "width": width,
                },
                component_generate_embed_params.ComponentGenerateEmbedParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComponentGenerateEmbedResponse,
        )

    async def interact(
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
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/api/v1/components/{id}/interact",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class ComponentsResourceWithRawResponse:
    def __init__(self, components: ComponentsResource) -> None:
        self._components = components

        self.create = to_raw_response_wrapper(
            components.create,
        )
        self.retrieve = to_raw_response_wrapper(
            components.retrieve,
        )
        self.update = to_raw_response_wrapper(
            components.update,
        )
        self.list = to_raw_response_wrapper(
            components.list,
        )
        self.delete = to_raw_response_wrapper(
            components.delete,
        )
        self.activate = to_raw_response_wrapper(
            components.activate,
        )
        self.deactivate = to_raw_response_wrapper(
            components.deactivate,
        )
        self.generate_embed = to_raw_response_wrapper(
            components.generate_embed,
        )
        self.interact = to_raw_response_wrapper(
            components.interact,
        )


class AsyncComponentsResourceWithRawResponse:
    def __init__(self, components: AsyncComponentsResource) -> None:
        self._components = components

        self.create = async_to_raw_response_wrapper(
            components.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            components.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            components.update,
        )
        self.list = async_to_raw_response_wrapper(
            components.list,
        )
        self.delete = async_to_raw_response_wrapper(
            components.delete,
        )
        self.activate = async_to_raw_response_wrapper(
            components.activate,
        )
        self.deactivate = async_to_raw_response_wrapper(
            components.deactivate,
        )
        self.generate_embed = async_to_raw_response_wrapper(
            components.generate_embed,
        )
        self.interact = async_to_raw_response_wrapper(
            components.interact,
        )


class ComponentsResourceWithStreamingResponse:
    def __init__(self, components: ComponentsResource) -> None:
        self._components = components

        self.create = to_streamed_response_wrapper(
            components.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            components.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            components.update,
        )
        self.list = to_streamed_response_wrapper(
            components.list,
        )
        self.delete = to_streamed_response_wrapper(
            components.delete,
        )
        self.activate = to_streamed_response_wrapper(
            components.activate,
        )
        self.deactivate = to_streamed_response_wrapper(
            components.deactivate,
        )
        self.generate_embed = to_streamed_response_wrapper(
            components.generate_embed,
        )
        self.interact = to_streamed_response_wrapper(
            components.interact,
        )


class AsyncComponentsResourceWithStreamingResponse:
    def __init__(self, components: AsyncComponentsResource) -> None:
        self._components = components

        self.create = async_to_streamed_response_wrapper(
            components.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            components.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            components.update,
        )
        self.list = async_to_streamed_response_wrapper(
            components.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            components.delete,
        )
        self.activate = async_to_streamed_response_wrapper(
            components.activate,
        )
        self.deactivate = async_to_streamed_response_wrapper(
            components.deactivate,
        )
        self.generate_embed = async_to_streamed_response_wrapper(
            components.generate_embed,
        )
        self.interact = async_to_streamed_response_wrapper(
            components.interact,
        )
