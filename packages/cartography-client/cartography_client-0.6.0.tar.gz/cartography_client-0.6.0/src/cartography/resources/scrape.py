# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable

import httpx

from ..types import scrape_scrape_bulk_params, scrape_scrape_single_params
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
from ..types.scrape_engine_param import ScrapeEngineParam
from ..types.scrape_scrape_bulk_response import ScrapeScrapeBulkResponse
from ..types.scrape_scrape_single_response import ScrapeScrapeSingleResponse

__all__ = ["ScrapeResource", "AsyncScrapeResource"]


class ScrapeResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ScrapeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/cartography-client#accessing-raw-response-data-eg-headers
        """
        return ScrapeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ScrapeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/cartography-client#with_streaming_response
        """
        return ScrapeResourceWithStreamingResponse(self)

    def scrape_bulk(
        self,
        *,
        crawl_id: str,
        engines: Iterable[ScrapeEngineParam],
        s3_bucket: str,
        urls: List[str],
        batch_size: int | NotGiven = NOT_GIVEN,
        debug: bool | NotGiven = NOT_GIVEN,
        max_workers: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ScrapeScrapeBulkResponse:
        """
        Bulk scrape multiple URLs with checkpointing to S3

        Requires permission: scrape:write

        Args:
          crawl_id: Unique identifier for this crawl

          engines: List of engines to use

          s3_bucket: S3 bucket for checkpointing

          urls: List of URLs to scrape

          batch_size: URLs per batch

          debug: Enable debug information

          max_workers: Maximum concurrent workers

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/scrape/bulk",
            body=maybe_transform(
                {
                    "crawl_id": crawl_id,
                    "engines": engines,
                    "s3_bucket": s3_bucket,
                    "urls": urls,
                    "batch_size": batch_size,
                    "debug": debug,
                    "max_workers": max_workers,
                },
                scrape_scrape_bulk_params.ScrapeScrapeBulkParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ScrapeScrapeBulkResponse,
        )

    def scrape_single(
        self,
        *,
        engines: Iterable[ScrapeEngineParam],
        url: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ScrapeScrapeSingleResponse:
        """
        Scrape a single URL using the specified engines

        Requires permission: scrape:read

        Args:
          engines: List of engines to use

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/scrape/single",
            body=maybe_transform(
                {
                    "engines": engines,
                    "url": url,
                },
                scrape_scrape_single_params.ScrapeScrapeSingleParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ScrapeScrapeSingleResponse,
        )


class AsyncScrapeResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncScrapeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/cartography-client#accessing-raw-response-data-eg-headers
        """
        return AsyncScrapeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncScrapeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/cartography-client#with_streaming_response
        """
        return AsyncScrapeResourceWithStreamingResponse(self)

    async def scrape_bulk(
        self,
        *,
        crawl_id: str,
        engines: Iterable[ScrapeEngineParam],
        s3_bucket: str,
        urls: List[str],
        batch_size: int | NotGiven = NOT_GIVEN,
        debug: bool | NotGiven = NOT_GIVEN,
        max_workers: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ScrapeScrapeBulkResponse:
        """
        Bulk scrape multiple URLs with checkpointing to S3

        Requires permission: scrape:write

        Args:
          crawl_id: Unique identifier for this crawl

          engines: List of engines to use

          s3_bucket: S3 bucket for checkpointing

          urls: List of URLs to scrape

          batch_size: URLs per batch

          debug: Enable debug information

          max_workers: Maximum concurrent workers

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/scrape/bulk",
            body=await async_maybe_transform(
                {
                    "crawl_id": crawl_id,
                    "engines": engines,
                    "s3_bucket": s3_bucket,
                    "urls": urls,
                    "batch_size": batch_size,
                    "debug": debug,
                    "max_workers": max_workers,
                },
                scrape_scrape_bulk_params.ScrapeScrapeBulkParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ScrapeScrapeBulkResponse,
        )

    async def scrape_single(
        self,
        *,
        engines: Iterable[ScrapeEngineParam],
        url: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ScrapeScrapeSingleResponse:
        """
        Scrape a single URL using the specified engines

        Requires permission: scrape:read

        Args:
          engines: List of engines to use

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/scrape/single",
            body=await async_maybe_transform(
                {
                    "engines": engines,
                    "url": url,
                },
                scrape_scrape_single_params.ScrapeScrapeSingleParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ScrapeScrapeSingleResponse,
        )


class ScrapeResourceWithRawResponse:
    def __init__(self, scrape: ScrapeResource) -> None:
        self._scrape = scrape

        self.scrape_bulk = to_raw_response_wrapper(
            scrape.scrape_bulk,
        )
        self.scrape_single = to_raw_response_wrapper(
            scrape.scrape_single,
        )


class AsyncScrapeResourceWithRawResponse:
    def __init__(self, scrape: AsyncScrapeResource) -> None:
        self._scrape = scrape

        self.scrape_bulk = async_to_raw_response_wrapper(
            scrape.scrape_bulk,
        )
        self.scrape_single = async_to_raw_response_wrapper(
            scrape.scrape_single,
        )


class ScrapeResourceWithStreamingResponse:
    def __init__(self, scrape: ScrapeResource) -> None:
        self._scrape = scrape

        self.scrape_bulk = to_streamed_response_wrapper(
            scrape.scrape_bulk,
        )
        self.scrape_single = to_streamed_response_wrapper(
            scrape.scrape_single,
        )


class AsyncScrapeResourceWithStreamingResponse:
    def __init__(self, scrape: AsyncScrapeResource) -> None:
        self._scrape = scrape

        self.scrape_bulk = async_to_streamed_response_wrapper(
            scrape.scrape_bulk,
        )
        self.scrape_single = async_to_streamed_response_wrapper(
            scrape.scrape_single,
        )
