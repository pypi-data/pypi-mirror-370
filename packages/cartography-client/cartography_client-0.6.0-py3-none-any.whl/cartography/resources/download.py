# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional

import httpx

from ..types import WaitUntil, DownloaderType, download_create_bulk_params, download_create_single_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.wait_until import WaitUntil
from ..types.downloader_type import DownloaderType
from ..types.download_create_bulk_response import DownloadCreateBulkResponse
from ..types.download_create_single_response import DownloadCreateSingleResponse

__all__ = ["DownloadResource", "AsyncDownloadResource"]


class DownloadResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DownloadResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/cartography-client#accessing-raw-response-data-eg-headers
        """
        return DownloadResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DownloadResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/cartography-client#with_streaming_response
        """
        return DownloadResourceWithStreamingResponse(self)

    def create_bulk(
        self,
        *,
        crawl_id: str,
        s3_bucket: str,
        urls: List[str],
        batch_size: int | NotGiven = NOT_GIVEN,
        debug: bool | NotGiven = NOT_GIVEN,
        downloader_type: DownloaderType | NotGiven = NOT_GIVEN,
        max_workers: int | NotGiven = NOT_GIVEN,
        wait_until: WaitUntil | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DownloadCreateBulkResponse:
        """
        Bulk download multiple files with checkpointing to S3

        Requires permission: download:write

        Args:
          crawl_id: Unique identifier for this crawl

          s3_bucket: S3 bucket for storage and checkpoints

          urls: List of URLs to download

          batch_size: URLs per batch

          debug: Enable debug information

          downloader_type: Available downloader types

          max_workers: Maximum concurrent workers

          wait_until: When to consider downloads complete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/download/bulk",
            body=maybe_transform(
                {
                    "crawl_id": crawl_id,
                    "s3_bucket": s3_bucket,
                    "urls": urls,
                    "batch_size": batch_size,
                    "debug": debug,
                    "downloader_type": downloader_type,
                    "max_workers": max_workers,
                    "wait_until": wait_until,
                },
                download_create_bulk_params.DownloadCreateBulkParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DownloadCreateBulkResponse,
        )

    def create_single(
        self,
        *,
        s3_bucket: str,
        url: str,
        downloader_type: DownloaderType | NotGiven = NOT_GIVEN,
        s3_key: Optional[str] | NotGiven = NOT_GIVEN,
        api_timeout: int | NotGiven = NOT_GIVEN,
        wait_until: WaitUntil | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DownloadCreateSingleResponse:
        """
        Download a single file to S3

        Requires permission: download:write

        Args:
          s3_bucket: S3 bucket for storage

          url: URL to download

          downloader_type: Available downloader types

          s3_key: S3 key for the file

          api_timeout: Timeout in milliseconds

          wait_until: When to consider download complete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/download/single",
            body=maybe_transform(
                {
                    "s3_bucket": s3_bucket,
                    "url": url,
                    "downloader_type": downloader_type,
                    "s3_key": s3_key,
                    "api_timeout": api_timeout,
                    "wait_until": wait_until,
                },
                download_create_single_params.DownloadCreateSingleParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DownloadCreateSingleResponse,
        )


class AsyncDownloadResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDownloadResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/cartography-client#accessing-raw-response-data-eg-headers
        """
        return AsyncDownloadResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDownloadResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/cartography-client#with_streaming_response
        """
        return AsyncDownloadResourceWithStreamingResponse(self)

    async def create_bulk(
        self,
        *,
        crawl_id: str,
        s3_bucket: str,
        urls: List[str],
        batch_size: int | NotGiven = NOT_GIVEN,
        debug: bool | NotGiven = NOT_GIVEN,
        downloader_type: DownloaderType | NotGiven = NOT_GIVEN,
        max_workers: int | NotGiven = NOT_GIVEN,
        wait_until: WaitUntil | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DownloadCreateBulkResponse:
        """
        Bulk download multiple files with checkpointing to S3

        Requires permission: download:write

        Args:
          crawl_id: Unique identifier for this crawl

          s3_bucket: S3 bucket for storage and checkpoints

          urls: List of URLs to download

          batch_size: URLs per batch

          debug: Enable debug information

          downloader_type: Available downloader types

          max_workers: Maximum concurrent workers

          wait_until: When to consider downloads complete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/download/bulk",
            body=await async_maybe_transform(
                {
                    "crawl_id": crawl_id,
                    "s3_bucket": s3_bucket,
                    "urls": urls,
                    "batch_size": batch_size,
                    "debug": debug,
                    "downloader_type": downloader_type,
                    "max_workers": max_workers,
                    "wait_until": wait_until,
                },
                download_create_bulk_params.DownloadCreateBulkParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DownloadCreateBulkResponse,
        )

    async def create_single(
        self,
        *,
        s3_bucket: str,
        url: str,
        downloader_type: DownloaderType | NotGiven = NOT_GIVEN,
        s3_key: Optional[str] | NotGiven = NOT_GIVEN,
        api_timeout: int | NotGiven = NOT_GIVEN,
        wait_until: WaitUntil | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DownloadCreateSingleResponse:
        """
        Download a single file to S3

        Requires permission: download:write

        Args:
          s3_bucket: S3 bucket for storage

          url: URL to download

          downloader_type: Available downloader types

          s3_key: S3 key for the file

          api_timeout: Timeout in milliseconds

          wait_until: When to consider download complete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/download/single",
            body=await async_maybe_transform(
                {
                    "s3_bucket": s3_bucket,
                    "url": url,
                    "downloader_type": downloader_type,
                    "s3_key": s3_key,
                    "api_timeout": api_timeout,
                    "wait_until": wait_until,
                },
                download_create_single_params.DownloadCreateSingleParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DownloadCreateSingleResponse,
        )


class DownloadResourceWithRawResponse:
    def __init__(self, download: DownloadResource) -> None:
        self._download = download

        self.create_bulk = to_raw_response_wrapper(
            download.create_bulk,
        )
        self.create_single = to_raw_response_wrapper(
            download.create_single,
        )


class AsyncDownloadResourceWithRawResponse:
    def __init__(self, download: AsyncDownloadResource) -> None:
        self._download = download

        self.create_bulk = async_to_raw_response_wrapper(
            download.create_bulk,
        )
        self.create_single = async_to_raw_response_wrapper(
            download.create_single,
        )


class DownloadResourceWithStreamingResponse:
    def __init__(self, download: DownloadResource) -> None:
        self._download = download

        self.create_bulk = to_streamed_response_wrapper(
            download.create_bulk,
        )
        self.create_single = to_streamed_response_wrapper(
            download.create_single,
        )


class AsyncDownloadResourceWithStreamingResponse:
    def __init__(self, download: AsyncDownloadResource) -> None:
        self._download = download

        self.create_bulk = async_to_streamed_response_wrapper(
            download.create_bulk,
        )
        self.create_single = async_to_streamed_response_wrapper(
            download.create_single,
        )
