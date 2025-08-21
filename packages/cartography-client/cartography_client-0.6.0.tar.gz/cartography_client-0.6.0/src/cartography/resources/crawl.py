# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal

import httpx

from ..types import crawl_create_graph_params
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
from ..types.crawl_create_graph_response import CrawlCreateGraphResponse

__all__ = ["CrawlResource", "AsyncCrawlResource"]


class CrawlResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CrawlResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/cartography-client#accessing-raw-response-data-eg-headers
        """
        return CrawlResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CrawlResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/cartography-client#with_streaming_response
        """
        return CrawlResourceWithStreamingResponse(self)

    def create_graph(
        self,
        *,
        crawl_id: str,
        engines: List[Literal["FLEET", "ZENROWS", "SCRAPINGBEE", "FLEET_ASYNC", "FLEET_WORKFLOW"]],
        s3_bucket: str,
        url: str,
        absolute_only: bool | NotGiven = NOT_GIVEN,
        batch_size: int | NotGiven = NOT_GIVEN,
        debug: bool | NotGiven = NOT_GIVEN,
        depth: Optional[int] | NotGiven = NOT_GIVEN,
        keep_external: bool | NotGiven = NOT_GIVEN,
        max_urls: int | NotGiven = NOT_GIVEN,
        max_workers: int | NotGiven = NOT_GIVEN,
        visit_external: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CrawlCreateGraphResponse:
        """
        Create a crawl graph by recursively crawling from a root URL

        This endpoint crawls a website starting from the given URL up to the specified
        depth, extracting links and building a graph structure. Results are checkpointed
        to S3.

        Requires permission: crawl:write

        Args:
          crawl_id: Unique identifier for this crawl

          engines: List of engines to use

          s3_bucket: S3 bucket for checkpointing

          url: Root URL to start crawling from

          absolute_only: Only extract absolute URLs

          batch_size: URLs per batch

          debug: Enable debug information

          depth: Maximum crawl depth

          keep_external: Keep external URLs in results

          max_urls: Maximum URLs to crawl

          max_workers: Maximum concurrent workers

          visit_external: Visit external URLs

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/crawl/graph",
            body=maybe_transform(
                {
                    "crawl_id": crawl_id,
                    "engines": engines,
                    "s3_bucket": s3_bucket,
                    "url": url,
                    "absolute_only": absolute_only,
                    "batch_size": batch_size,
                    "debug": debug,
                    "depth": depth,
                    "keep_external": keep_external,
                    "max_urls": max_urls,
                    "max_workers": max_workers,
                    "visit_external": visit_external,
                },
                crawl_create_graph_params.CrawlCreateGraphParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CrawlCreateGraphResponse,
        )


class AsyncCrawlResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCrawlResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/cartography-client#accessing-raw-response-data-eg-headers
        """
        return AsyncCrawlResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCrawlResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/cartography-client#with_streaming_response
        """
        return AsyncCrawlResourceWithStreamingResponse(self)

    async def create_graph(
        self,
        *,
        crawl_id: str,
        engines: List[Literal["FLEET", "ZENROWS", "SCRAPINGBEE", "FLEET_ASYNC", "FLEET_WORKFLOW"]],
        s3_bucket: str,
        url: str,
        absolute_only: bool | NotGiven = NOT_GIVEN,
        batch_size: int | NotGiven = NOT_GIVEN,
        debug: bool | NotGiven = NOT_GIVEN,
        depth: Optional[int] | NotGiven = NOT_GIVEN,
        keep_external: bool | NotGiven = NOT_GIVEN,
        max_urls: int | NotGiven = NOT_GIVEN,
        max_workers: int | NotGiven = NOT_GIVEN,
        visit_external: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CrawlCreateGraphResponse:
        """
        Create a crawl graph by recursively crawling from a root URL

        This endpoint crawls a website starting from the given URL up to the specified
        depth, extracting links and building a graph structure. Results are checkpointed
        to S3.

        Requires permission: crawl:write

        Args:
          crawl_id: Unique identifier for this crawl

          engines: List of engines to use

          s3_bucket: S3 bucket for checkpointing

          url: Root URL to start crawling from

          absolute_only: Only extract absolute URLs

          batch_size: URLs per batch

          debug: Enable debug information

          depth: Maximum crawl depth

          keep_external: Keep external URLs in results

          max_urls: Maximum URLs to crawl

          max_workers: Maximum concurrent workers

          visit_external: Visit external URLs

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/crawl/graph",
            body=await async_maybe_transform(
                {
                    "crawl_id": crawl_id,
                    "engines": engines,
                    "s3_bucket": s3_bucket,
                    "url": url,
                    "absolute_only": absolute_only,
                    "batch_size": batch_size,
                    "debug": debug,
                    "depth": depth,
                    "keep_external": keep_external,
                    "max_urls": max_urls,
                    "max_workers": max_workers,
                    "visit_external": visit_external,
                },
                crawl_create_graph_params.CrawlCreateGraphParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CrawlCreateGraphResponse,
        )


class CrawlResourceWithRawResponse:
    def __init__(self, crawl: CrawlResource) -> None:
        self._crawl = crawl

        self.create_graph = to_raw_response_wrapper(
            crawl.create_graph,
        )


class AsyncCrawlResourceWithRawResponse:
    def __init__(self, crawl: AsyncCrawlResource) -> None:
        self._crawl = crawl

        self.create_graph = async_to_raw_response_wrapper(
            crawl.create_graph,
        )


class CrawlResourceWithStreamingResponse:
    def __init__(self, crawl: CrawlResource) -> None:
        self._crawl = crawl

        self.create_graph = to_streamed_response_wrapper(
            crawl.create_graph,
        )


class AsyncCrawlResourceWithStreamingResponse:
    def __init__(self, crawl: AsyncCrawlResource) -> None:
        self._crawl = crawl

        self.create_graph = async_to_streamed_response_wrapper(
            crawl.create_graph,
        )
