# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable, Optional
from typing_extensions import Literal

import httpx

from .bulk import (
    BulkResource,
    AsyncBulkResource,
    BulkResourceWithRawResponse,
    AsyncBulkResourceWithRawResponse,
    BulkResourceWithStreamingResponse,
    AsyncBulkResourceWithStreamingResponse,
)
from .upload import (
    UploadResource,
    AsyncUploadResource,
    UploadResourceWithRawResponse,
    AsyncUploadResourceWithRawResponse,
    UploadResourceWithStreamingResponse,
    AsyncUploadResourceWithStreamingResponse,
)
from ...._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ....types.v1 import (
    material_list_params,
    material_move_params,
    material_create_params,
    material_rename_params,
    material_search_params,
    material_generate_params,
    material_get_download_url_params,
    material_create_and_process_params,
    material_generate_and_process_params,
    material_create_batch_upload_urls_params,
)
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v1.content_param import ContentParam
from ....types.v1.material_response import MaterialResponse
from ....types.v1.material_list_response import MaterialListResponse
from ....types.v1.material_search_response import MaterialSearchResponse
from ....types.v1.generated_material_response import GeneratedMaterialResponse
from ....types.v1.material_get_debug_info_response import MaterialGetDebugInfoResponse
from ....types.v1.material_get_download_url_response import MaterialGetDownloadURLResponse
from ....types.v1.material_create_batch_upload_urls_response import MaterialCreateBatchUploadURLsResponse

__all__ = ["MaterialsResource", "AsyncMaterialsResource"]


class MaterialsResource(SyncAPIResource):
    @cached_property
    def upload(self) -> UploadResource:
        return UploadResource(self._client)

    @cached_property
    def bulk(self) -> BulkResource:
        return BulkResource(self._client)

    @cached_property
    def with_raw_response(self) -> MaterialsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return MaterialsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MaterialsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return MaterialsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        content: ContentParam,
        name: str,
        folder_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialResponse:
        """
        Create a new material

        Args:
          content: Content details

          name: Name of the material

          folder_id: Folder ID to place the material in

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/materials",
            body=maybe_transform(
                {
                    "content": content,
                    "name": name,
                    "folder_id": folder_id,
                },
                material_create_params.MaterialCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MaterialResponse,
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
    ) -> MaterialResponse:
        """
        Get material by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/api/v1/materials/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MaterialResponse,
        )

    def list(
        self,
        *,
        folder_id: str | NotGiven = NOT_GIVEN,
        limit: str | NotGiven = NOT_GIVEN,
        page: str | NotGiven = NOT_GIVEN,
        search: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialListResponse:
        """
        Get all materials for organization

        Args:
          folder_id: Filter by folder ID

          limit: Number of items per page (default: 20, max: 200)

          page: Page number (default: 1)

          search: Search materials by name

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/materials",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "folder_id": folder_id,
                        "limit": limit,
                        "page": page,
                        "search": search,
                    },
                    material_list_params.MaterialListParams,
                ),
            ),
            cast_to=MaterialListResponse,
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
        Delete material

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
            f"/api/v1/materials/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def create_and_process(
        self,
        *,
        content: ContentParam,
        name: str,
        folder_id: str | NotGiven = NOT_GIVEN,
        poll_interval_ms: float | NotGiven = NOT_GIVEN,
        timeout_ms: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialResponse:
        """Creates a material and waits for processing to finish before returning.

        Useful
        for synchronous API usage.

        Args:
          content: Content details

          name: Name of the material

          folder_id: Folder ID to place the material in

          poll_interval_ms: Polling interval in milliseconds (default: 2 seconds)

          timeout_ms: Maximum time to wait for processing in milliseconds (default: 5 minutes)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/materials/upload-and-process",
            body=maybe_transform(
                {
                    "content": content,
                    "name": name,
                    "folder_id": folder_id,
                    "poll_interval_ms": poll_interval_ms,
                    "timeout_ms": timeout_ms,
                },
                material_create_and_process_params.MaterialCreateAndProcessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MaterialResponse,
        )

    def create_batch_upload_urls(
        self,
        *,
        materials: Iterable[material_create_batch_upload_urls_params.Material],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialCreateBatchUploadURLsResponse:
        """
        Create batch upload URLs for multiple materials

        Args:
          materials: Array of materials to create

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/materials/batch",
            body=maybe_transform(
                {"materials": materials}, material_create_batch_upload_urls_params.MaterialCreateBatchUploadURLsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MaterialCreateBatchUploadURLsResponse,
        )

    def generate(
        self,
        *,
        name: str,
        topic: str,
        type: Literal["outline", "overview", "notes", "summary"],
        context: str | NotGiven = NOT_GIVEN,
        folder_id: str | NotGiven = NOT_GIVEN,
        length: Literal["short", "medium", "long"] | NotGiven = NOT_GIVEN,
        level: Literal["high_school", "college", "professional"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GeneratedMaterialResponse:
        """Uses AI to generate study materials like outlines, notes, summaries, etc.

        from a
        given topic. Returns immediately without waiting for processing.

        Args:
          name: Name for the generated material

          topic: Topic or context to generate material from

          type: Type of material to generate

          context: Additional context or details about the topic

          folder_id: Target folder ID

          length: Length of the generated content

          level: Target education level

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/materials/generate",
            body=maybe_transform(
                {
                    "name": name,
                    "topic": topic,
                    "type": type,
                    "context": context,
                    "folder_id": folder_id,
                    "length": length,
                    "level": level,
                },
                material_generate_params.MaterialGenerateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GeneratedMaterialResponse,
        )

    def generate_and_process(
        self,
        *,
        name: str,
        topic: str,
        type: Literal["outline", "overview", "notes", "summary"],
        context: str | NotGiven = NOT_GIVEN,
        folder_id: str | NotGiven = NOT_GIVEN,
        length: Literal["short", "medium", "long"] | NotGiven = NOT_GIVEN,
        level: Literal["high_school", "college", "professional"] | NotGiven = NOT_GIVEN,
        poll_interval_ms: float | NotGiven = NOT_GIVEN,
        timeout_ms: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GeneratedMaterialResponse:
        """Uses AI to generate study materials like outlines, notes, summaries, etc.

        from a
        given topic and waits for processing to complete

        Args:
          name: Name for the generated material

          topic: Topic or context to generate material from

          type: Type of material to generate

          context: Additional context or details about the topic

          folder_id: Target folder ID

          length: Length of the generated content

          level: Target education level

          poll_interval_ms: Polling interval in milliseconds (default: 2 seconds)

          timeout_ms: Maximum time to wait for processing in milliseconds (default: 5 minutes)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/materials/generate-and-process",
            body=maybe_transform(
                {
                    "name": name,
                    "topic": topic,
                    "type": type,
                    "context": context,
                    "folder_id": folder_id,
                    "length": length,
                    "level": level,
                    "poll_interval_ms": poll_interval_ms,
                    "timeout_ms": timeout_ms,
                },
                material_generate_and_process_params.MaterialGenerateAndProcessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GeneratedMaterialResponse,
        )

    def get_debug_info(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialGetDebugInfoResponse:
        """
        Get debug information for a material including extracted content

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/api/v1/materials/{id}/debug",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MaterialGetDebugInfoResponse,
        )

    def get_download_url(
        self,
        id: str,
        *,
        expires_in: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialGetDownloadURLResponse:
        """
        Get temporary download URL for material

        Args:
          expires_in: URL expiration time in seconds (default: 3600)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/api/v1/materials/{id}/download-url",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"expires_in": expires_in}, material_get_download_url_params.MaterialGetDownloadURLParams
                ),
            ),
            cast_to=MaterialGetDownloadURLResponse,
        )

    def move(
        self,
        id: str,
        *,
        folder_id: Optional[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialResponse:
        """
        Move material to a different folder

        Args:
          folder_id: Target folder ID (null for root)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/api/v1/materials/{id}/move",
            body=maybe_transform({"folder_id": folder_id}, material_move_params.MaterialMoveParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MaterialResponse,
        )

    def rename(
        self,
        id: str,
        *,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialResponse:
        """
        Rename a material

        Args:
          name: New name for the material

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/api/v1/materials/{id}/rename",
            body=maybe_transform({"name": name}, material_rename_params.MaterialRenameParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MaterialResponse,
        )

    def reprocess(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialResponse:
        """
        Reprocess material to regenerate embeddings and extract content

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/api/v1/materials/{id}/reprocess",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MaterialResponse,
        )

    def search(
        self,
        *,
        query: str,
        folder_ids: List[str] | NotGiven = NOT_GIVEN,
        material_ids: List[str] | NotGiven = NOT_GIVEN,
        top_k: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialSearchResponse:
        """
        Search materials using RAG (Retrieval-Augmented Generation)

        Args:
          query: Search query

          folder_ids: Limit search to materials within specific folders (includes subfolders)

          material_ids: Limit search to specific material IDs

          top_k: Number of results to return

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/materials/search",
            body=maybe_transform(
                {
                    "query": query,
                    "folder_ids": folder_ids,
                    "material_ids": material_ids,
                    "top_k": top_k,
                },
                material_search_params.MaterialSearchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MaterialSearchResponse,
        )


class AsyncMaterialsResource(AsyncAPIResource):
    @cached_property
    def upload(self) -> AsyncUploadResource:
        return AsyncUploadResource(self._client)

    @cached_property
    def bulk(self) -> AsyncBulkResource:
        return AsyncBulkResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncMaterialsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncMaterialsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMaterialsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncMaterialsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        content: ContentParam,
        name: str,
        folder_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialResponse:
        """
        Create a new material

        Args:
          content: Content details

          name: Name of the material

          folder_id: Folder ID to place the material in

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/materials",
            body=await async_maybe_transform(
                {
                    "content": content,
                    "name": name,
                    "folder_id": folder_id,
                },
                material_create_params.MaterialCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MaterialResponse,
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
    ) -> MaterialResponse:
        """
        Get material by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/api/v1/materials/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MaterialResponse,
        )

    async def list(
        self,
        *,
        folder_id: str | NotGiven = NOT_GIVEN,
        limit: str | NotGiven = NOT_GIVEN,
        page: str | NotGiven = NOT_GIVEN,
        search: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialListResponse:
        """
        Get all materials for organization

        Args:
          folder_id: Filter by folder ID

          limit: Number of items per page (default: 20, max: 200)

          page: Page number (default: 1)

          search: Search materials by name

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/materials",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "folder_id": folder_id,
                        "limit": limit,
                        "page": page,
                        "search": search,
                    },
                    material_list_params.MaterialListParams,
                ),
            ),
            cast_to=MaterialListResponse,
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
        Delete material

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
            f"/api/v1/materials/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def create_and_process(
        self,
        *,
        content: ContentParam,
        name: str,
        folder_id: str | NotGiven = NOT_GIVEN,
        poll_interval_ms: float | NotGiven = NOT_GIVEN,
        timeout_ms: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialResponse:
        """Creates a material and waits for processing to finish before returning.

        Useful
        for synchronous API usage.

        Args:
          content: Content details

          name: Name of the material

          folder_id: Folder ID to place the material in

          poll_interval_ms: Polling interval in milliseconds (default: 2 seconds)

          timeout_ms: Maximum time to wait for processing in milliseconds (default: 5 minutes)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/materials/upload-and-process",
            body=await async_maybe_transform(
                {
                    "content": content,
                    "name": name,
                    "folder_id": folder_id,
                    "poll_interval_ms": poll_interval_ms,
                    "timeout_ms": timeout_ms,
                },
                material_create_and_process_params.MaterialCreateAndProcessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MaterialResponse,
        )

    async def create_batch_upload_urls(
        self,
        *,
        materials: Iterable[material_create_batch_upload_urls_params.Material],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialCreateBatchUploadURLsResponse:
        """
        Create batch upload URLs for multiple materials

        Args:
          materials: Array of materials to create

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/materials/batch",
            body=await async_maybe_transform(
                {"materials": materials}, material_create_batch_upload_urls_params.MaterialCreateBatchUploadURLsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MaterialCreateBatchUploadURLsResponse,
        )

    async def generate(
        self,
        *,
        name: str,
        topic: str,
        type: Literal["outline", "overview", "notes", "summary"],
        context: str | NotGiven = NOT_GIVEN,
        folder_id: str | NotGiven = NOT_GIVEN,
        length: Literal["short", "medium", "long"] | NotGiven = NOT_GIVEN,
        level: Literal["high_school", "college", "professional"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GeneratedMaterialResponse:
        """Uses AI to generate study materials like outlines, notes, summaries, etc.

        from a
        given topic. Returns immediately without waiting for processing.

        Args:
          name: Name for the generated material

          topic: Topic or context to generate material from

          type: Type of material to generate

          context: Additional context or details about the topic

          folder_id: Target folder ID

          length: Length of the generated content

          level: Target education level

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/materials/generate",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "topic": topic,
                    "type": type,
                    "context": context,
                    "folder_id": folder_id,
                    "length": length,
                    "level": level,
                },
                material_generate_params.MaterialGenerateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GeneratedMaterialResponse,
        )

    async def generate_and_process(
        self,
        *,
        name: str,
        topic: str,
        type: Literal["outline", "overview", "notes", "summary"],
        context: str | NotGiven = NOT_GIVEN,
        folder_id: str | NotGiven = NOT_GIVEN,
        length: Literal["short", "medium", "long"] | NotGiven = NOT_GIVEN,
        level: Literal["high_school", "college", "professional"] | NotGiven = NOT_GIVEN,
        poll_interval_ms: float | NotGiven = NOT_GIVEN,
        timeout_ms: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GeneratedMaterialResponse:
        """Uses AI to generate study materials like outlines, notes, summaries, etc.

        from a
        given topic and waits for processing to complete

        Args:
          name: Name for the generated material

          topic: Topic or context to generate material from

          type: Type of material to generate

          context: Additional context or details about the topic

          folder_id: Target folder ID

          length: Length of the generated content

          level: Target education level

          poll_interval_ms: Polling interval in milliseconds (default: 2 seconds)

          timeout_ms: Maximum time to wait for processing in milliseconds (default: 5 minutes)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/materials/generate-and-process",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "topic": topic,
                    "type": type,
                    "context": context,
                    "folder_id": folder_id,
                    "length": length,
                    "level": level,
                    "poll_interval_ms": poll_interval_ms,
                    "timeout_ms": timeout_ms,
                },
                material_generate_and_process_params.MaterialGenerateAndProcessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GeneratedMaterialResponse,
        )

    async def get_debug_info(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialGetDebugInfoResponse:
        """
        Get debug information for a material including extracted content

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/api/v1/materials/{id}/debug",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MaterialGetDebugInfoResponse,
        )

    async def get_download_url(
        self,
        id: str,
        *,
        expires_in: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialGetDownloadURLResponse:
        """
        Get temporary download URL for material

        Args:
          expires_in: URL expiration time in seconds (default: 3600)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/api/v1/materials/{id}/download-url",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"expires_in": expires_in}, material_get_download_url_params.MaterialGetDownloadURLParams
                ),
            ),
            cast_to=MaterialGetDownloadURLResponse,
        )

    async def move(
        self,
        id: str,
        *,
        folder_id: Optional[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialResponse:
        """
        Move material to a different folder

        Args:
          folder_id: Target folder ID (null for root)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/api/v1/materials/{id}/move",
            body=await async_maybe_transform({"folder_id": folder_id}, material_move_params.MaterialMoveParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MaterialResponse,
        )

    async def rename(
        self,
        id: str,
        *,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialResponse:
        """
        Rename a material

        Args:
          name: New name for the material

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/api/v1/materials/{id}/rename",
            body=await async_maybe_transform({"name": name}, material_rename_params.MaterialRenameParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MaterialResponse,
        )

    async def reprocess(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialResponse:
        """
        Reprocess material to regenerate embeddings and extract content

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/api/v1/materials/{id}/reprocess",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MaterialResponse,
        )

    async def search(
        self,
        *,
        query: str,
        folder_ids: List[str] | NotGiven = NOT_GIVEN,
        material_ids: List[str] | NotGiven = NOT_GIVEN,
        top_k: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MaterialSearchResponse:
        """
        Search materials using RAG (Retrieval-Augmented Generation)

        Args:
          query: Search query

          folder_ids: Limit search to materials within specific folders (includes subfolders)

          material_ids: Limit search to specific material IDs

          top_k: Number of results to return

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/materials/search",
            body=await async_maybe_transform(
                {
                    "query": query,
                    "folder_ids": folder_ids,
                    "material_ids": material_ids,
                    "top_k": top_k,
                },
                material_search_params.MaterialSearchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MaterialSearchResponse,
        )


class MaterialsResourceWithRawResponse:
    def __init__(self, materials: MaterialsResource) -> None:
        self._materials = materials

        self.create = to_raw_response_wrapper(
            materials.create,
        )
        self.retrieve = to_raw_response_wrapper(
            materials.retrieve,
        )
        self.list = to_raw_response_wrapper(
            materials.list,
        )
        self.delete = to_raw_response_wrapper(
            materials.delete,
        )
        self.create_and_process = to_raw_response_wrapper(
            materials.create_and_process,
        )
        self.create_batch_upload_urls = to_raw_response_wrapper(
            materials.create_batch_upload_urls,
        )
        self.generate = to_raw_response_wrapper(
            materials.generate,
        )
        self.generate_and_process = to_raw_response_wrapper(
            materials.generate_and_process,
        )
        self.get_debug_info = to_raw_response_wrapper(
            materials.get_debug_info,
        )
        self.get_download_url = to_raw_response_wrapper(
            materials.get_download_url,
        )
        self.move = to_raw_response_wrapper(
            materials.move,
        )
        self.rename = to_raw_response_wrapper(
            materials.rename,
        )
        self.reprocess = to_raw_response_wrapper(
            materials.reprocess,
        )
        self.search = to_raw_response_wrapper(
            materials.search,
        )

    @cached_property
    def upload(self) -> UploadResourceWithRawResponse:
        return UploadResourceWithRawResponse(self._materials.upload)

    @cached_property
    def bulk(self) -> BulkResourceWithRawResponse:
        return BulkResourceWithRawResponse(self._materials.bulk)


class AsyncMaterialsResourceWithRawResponse:
    def __init__(self, materials: AsyncMaterialsResource) -> None:
        self._materials = materials

        self.create = async_to_raw_response_wrapper(
            materials.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            materials.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            materials.list,
        )
        self.delete = async_to_raw_response_wrapper(
            materials.delete,
        )
        self.create_and_process = async_to_raw_response_wrapper(
            materials.create_and_process,
        )
        self.create_batch_upload_urls = async_to_raw_response_wrapper(
            materials.create_batch_upload_urls,
        )
        self.generate = async_to_raw_response_wrapper(
            materials.generate,
        )
        self.generate_and_process = async_to_raw_response_wrapper(
            materials.generate_and_process,
        )
        self.get_debug_info = async_to_raw_response_wrapper(
            materials.get_debug_info,
        )
        self.get_download_url = async_to_raw_response_wrapper(
            materials.get_download_url,
        )
        self.move = async_to_raw_response_wrapper(
            materials.move,
        )
        self.rename = async_to_raw_response_wrapper(
            materials.rename,
        )
        self.reprocess = async_to_raw_response_wrapper(
            materials.reprocess,
        )
        self.search = async_to_raw_response_wrapper(
            materials.search,
        )

    @cached_property
    def upload(self) -> AsyncUploadResourceWithRawResponse:
        return AsyncUploadResourceWithRawResponse(self._materials.upload)

    @cached_property
    def bulk(self) -> AsyncBulkResourceWithRawResponse:
        return AsyncBulkResourceWithRawResponse(self._materials.bulk)


class MaterialsResourceWithStreamingResponse:
    def __init__(self, materials: MaterialsResource) -> None:
        self._materials = materials

        self.create = to_streamed_response_wrapper(
            materials.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            materials.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            materials.list,
        )
        self.delete = to_streamed_response_wrapper(
            materials.delete,
        )
        self.create_and_process = to_streamed_response_wrapper(
            materials.create_and_process,
        )
        self.create_batch_upload_urls = to_streamed_response_wrapper(
            materials.create_batch_upload_urls,
        )
        self.generate = to_streamed_response_wrapper(
            materials.generate,
        )
        self.generate_and_process = to_streamed_response_wrapper(
            materials.generate_and_process,
        )
        self.get_debug_info = to_streamed_response_wrapper(
            materials.get_debug_info,
        )
        self.get_download_url = to_streamed_response_wrapper(
            materials.get_download_url,
        )
        self.move = to_streamed_response_wrapper(
            materials.move,
        )
        self.rename = to_streamed_response_wrapper(
            materials.rename,
        )
        self.reprocess = to_streamed_response_wrapper(
            materials.reprocess,
        )
        self.search = to_streamed_response_wrapper(
            materials.search,
        )

    @cached_property
    def upload(self) -> UploadResourceWithStreamingResponse:
        return UploadResourceWithStreamingResponse(self._materials.upload)

    @cached_property
    def bulk(self) -> BulkResourceWithStreamingResponse:
        return BulkResourceWithStreamingResponse(self._materials.bulk)


class AsyncMaterialsResourceWithStreamingResponse:
    def __init__(self, materials: AsyncMaterialsResource) -> None:
        self._materials = materials

        self.create = async_to_streamed_response_wrapper(
            materials.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            materials.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            materials.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            materials.delete,
        )
        self.create_and_process = async_to_streamed_response_wrapper(
            materials.create_and_process,
        )
        self.create_batch_upload_urls = async_to_streamed_response_wrapper(
            materials.create_batch_upload_urls,
        )
        self.generate = async_to_streamed_response_wrapper(
            materials.generate,
        )
        self.generate_and_process = async_to_streamed_response_wrapper(
            materials.generate_and_process,
        )
        self.get_debug_info = async_to_streamed_response_wrapper(
            materials.get_debug_info,
        )
        self.get_download_url = async_to_streamed_response_wrapper(
            materials.get_download_url,
        )
        self.move = async_to_streamed_response_wrapper(
            materials.move,
        )
        self.rename = async_to_streamed_response_wrapper(
            materials.rename,
        )
        self.reprocess = async_to_streamed_response_wrapper(
            materials.reprocess,
        )
        self.search = async_to_streamed_response_wrapper(
            materials.search,
        )

    @cached_property
    def upload(self) -> AsyncUploadResourceWithStreamingResponse:
        return AsyncUploadResourceWithStreamingResponse(self._materials.upload)

    @cached_property
    def bulk(self) -> AsyncBulkResourceWithStreamingResponse:
        return AsyncBulkResourceWithStreamingResponse(self._materials.bulk)
