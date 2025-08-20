# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v1.materials.test_test_ocr_response import TestTestOcrResponse
from ....types.v1.materials.test_test_epub_processing_response import TestTestEpubProcessingResponse
from ....types.v1.materials.test_test_image_processing_response import TestTestImageProcessingResponse
from ....types.v1.materials.test_test_video_processing_response import TestTestVideoProcessingResponse

__all__ = ["TestResource", "AsyncTestResource"]


class TestResource(SyncAPIResource):
    __test__ = False

    @cached_property
    def with_raw_response(self) -> TestResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return TestResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TestResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return TestResourceWithStreamingResponse(self)

    def test_epub_processing(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestTestEpubProcessingResponse:
        """Test EPUB processing functionality"""
        return self._post(
            "/api/v1/materials/test/epub-processing",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestTestEpubProcessingResponse,
        )

    def test_image_processing(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestTestImageProcessingResponse:
        """Test image processing with OCR and AI vision"""
        return self._post(
            "/api/v1/materials/test/image-processing",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestTestImageProcessingResponse,
        )

    def test_ocr(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestTestOcrResponse:
        """Test OCR functionality with a sample PDF"""
        return self._post(
            "/api/v1/materials/test/ocr",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestTestOcrResponse,
        )

    def test_video_processing(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestTestVideoProcessingResponse:
        """Test video processing setup and dependencies"""
        return self._post(
            "/api/v1/materials/test/video-processing",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestTestVideoProcessingResponse,
        )


class AsyncTestResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTestResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTestResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTestResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncTestResourceWithStreamingResponse(self)

    async def test_epub_processing(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestTestEpubProcessingResponse:
        """Test EPUB processing functionality"""
        return await self._post(
            "/api/v1/materials/test/epub-processing",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestTestEpubProcessingResponse,
        )

    async def test_image_processing(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestTestImageProcessingResponse:
        """Test image processing with OCR and AI vision"""
        return await self._post(
            "/api/v1/materials/test/image-processing",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestTestImageProcessingResponse,
        )

    async def test_ocr(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestTestOcrResponse:
        """Test OCR functionality with a sample PDF"""
        return await self._post(
            "/api/v1/materials/test/ocr",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestTestOcrResponse,
        )

    async def test_video_processing(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestTestVideoProcessingResponse:
        """Test video processing setup and dependencies"""
        return await self._post(
            "/api/v1/materials/test/video-processing",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestTestVideoProcessingResponse,
        )


class TestResourceWithRawResponse:
    __test__ = False

    def __init__(self, test: TestResource) -> None:
        self._test = test

        self.test_epub_processing = to_raw_response_wrapper(
            test.test_epub_processing,
        )
        self.test_image_processing = to_raw_response_wrapper(
            test.test_image_processing,
        )
        self.test_ocr = to_raw_response_wrapper(
            test.test_ocr,
        )
        self.test_video_processing = to_raw_response_wrapper(
            test.test_video_processing,
        )


class AsyncTestResourceWithRawResponse:
    def __init__(self, test: AsyncTestResource) -> None:
        self._test = test

        self.test_epub_processing = async_to_raw_response_wrapper(
            test.test_epub_processing,
        )
        self.test_image_processing = async_to_raw_response_wrapper(
            test.test_image_processing,
        )
        self.test_ocr = async_to_raw_response_wrapper(
            test.test_ocr,
        )
        self.test_video_processing = async_to_raw_response_wrapper(
            test.test_video_processing,
        )


class TestResourceWithStreamingResponse:
    __test__ = False

    def __init__(self, test: TestResource) -> None:
        self._test = test

        self.test_epub_processing = to_streamed_response_wrapper(
            test.test_epub_processing,
        )
        self.test_image_processing = to_streamed_response_wrapper(
            test.test_image_processing,
        )
        self.test_ocr = to_streamed_response_wrapper(
            test.test_ocr,
        )
        self.test_video_processing = to_streamed_response_wrapper(
            test.test_video_processing,
        )


class AsyncTestResourceWithStreamingResponse:
    def __init__(self, test: AsyncTestResource) -> None:
        self._test = test

        self.test_epub_processing = async_to_streamed_response_wrapper(
            test.test_epub_processing,
        )
        self.test_image_processing = async_to_streamed_response_wrapper(
            test.test_image_processing,
        )
        self.test_ocr = async_to_streamed_response_wrapper(
            test.test_ocr,
        )
        self.test_video_processing = async_to_streamed_response_wrapper(
            test.test_video_processing,
        )
