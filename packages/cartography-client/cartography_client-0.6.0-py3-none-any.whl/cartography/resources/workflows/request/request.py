# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List

import httpx

from .crawl import (
    CrawlResource,
    AsyncCrawlResource,
    CrawlResourceWithRawResponse,
    AsyncCrawlResourceWithRawResponse,
    CrawlResourceWithStreamingResponse,
    AsyncCrawlResourceWithStreamingResponse,
)
from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
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
from ....types.workflows import request_create_download_params
from ....types.workflows.request_create_download_response import RequestCreateDownloadResponse

__all__ = ["RequestResource", "AsyncRequestResource"]


class RequestResource(SyncAPIResource):
    @cached_property
    def crawl(self) -> CrawlResource:
        return CrawlResource(self._client)

    @cached_property
    def with_raw_response(self) -> RequestResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/cartography-client#accessing-raw-response-data-eg-headers
        """
        return RequestResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RequestResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/cartography-client#with_streaming_response
        """
        return RequestResourceWithStreamingResponse(self)

    def create_download(
        self,
        *,
        bucket_name: str,
        crawl_id: str,
        downloader_type: str,
        urls: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RequestCreateDownloadResponse:
        """
        Make a request to temporal worker :param request: crawl request data :param
        token_data: api token :return: response

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/workflows/request/download",
            body=maybe_transform(
                {
                    "bucket_name": bucket_name,
                    "crawl_id": crawl_id,
                    "downloader_type": downloader_type,
                    "urls": urls,
                },
                request_create_download_params.RequestCreateDownloadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RequestCreateDownloadResponse,
        )


class AsyncRequestResource(AsyncAPIResource):
    @cached_property
    def crawl(self) -> AsyncCrawlResource:
        return AsyncCrawlResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncRequestResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/cartography-client#accessing-raw-response-data-eg-headers
        """
        return AsyncRequestResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRequestResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/cartography-client#with_streaming_response
        """
        return AsyncRequestResourceWithStreamingResponse(self)

    async def create_download(
        self,
        *,
        bucket_name: str,
        crawl_id: str,
        downloader_type: str,
        urls: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RequestCreateDownloadResponse:
        """
        Make a request to temporal worker :param request: crawl request data :param
        token_data: api token :return: response

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/workflows/request/download",
            body=await async_maybe_transform(
                {
                    "bucket_name": bucket_name,
                    "crawl_id": crawl_id,
                    "downloader_type": downloader_type,
                    "urls": urls,
                },
                request_create_download_params.RequestCreateDownloadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RequestCreateDownloadResponse,
        )


class RequestResourceWithRawResponse:
    def __init__(self, request: RequestResource) -> None:
        self._request = request

        self.create_download = to_raw_response_wrapper(
            request.create_download,
        )

    @cached_property
    def crawl(self) -> CrawlResourceWithRawResponse:
        return CrawlResourceWithRawResponse(self._request.crawl)


class AsyncRequestResourceWithRawResponse:
    def __init__(self, request: AsyncRequestResource) -> None:
        self._request = request

        self.create_download = async_to_raw_response_wrapper(
            request.create_download,
        )

    @cached_property
    def crawl(self) -> AsyncCrawlResourceWithRawResponse:
        return AsyncCrawlResourceWithRawResponse(self._request.crawl)


class RequestResourceWithStreamingResponse:
    def __init__(self, request: RequestResource) -> None:
        self._request = request

        self.create_download = to_streamed_response_wrapper(
            request.create_download,
        )

    @cached_property
    def crawl(self) -> CrawlResourceWithStreamingResponse:
        return CrawlResourceWithStreamingResponse(self._request.crawl)


class AsyncRequestResourceWithStreamingResponse:
    def __init__(self, request: AsyncRequestResource) -> None:
        self._request = request

        self.create_download = async_to_streamed_response_wrapper(
            request.create_download,
        )

    @cached_property
    def crawl(self) -> AsyncCrawlResourceWithStreamingResponse:
        return AsyncCrawlResourceWithStreamingResponse(self._request.crawl)
