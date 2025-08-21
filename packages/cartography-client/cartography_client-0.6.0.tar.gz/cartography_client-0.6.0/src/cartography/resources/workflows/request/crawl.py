# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal

import httpx

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
from ....types.workflows.request import crawl_create_params, crawl_create_bulk_params
from ....types.workflows.request.workflow_result import WorkflowResult
from ....types.workflows.request.crawl_request_param import CrawlRequestParam
from ....types.workflows.request.crawl_create_bulk_response import CrawlCreateBulkResponse

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

    def create(
        self,
        *,
        bucket_name: str,
        crawl_id: str,
        engines: List[Literal["FLEET", "ZENROWS", "SCRAPINGBEE", "FLEET_ASYNC", "FLEET_WORKFLOW"]],
        url: str,
        absolute_only: bool | NotGiven = NOT_GIVEN,
        batch_size: int | NotGiven = NOT_GIVEN,
        depth: int | NotGiven = NOT_GIVEN,
        keep_external: bool | NotGiven = NOT_GIVEN,
        max_urls: int | NotGiven = NOT_GIVEN,
        max_workers: int | NotGiven = NOT_GIVEN,
        stealth: bool | NotGiven = NOT_GIVEN,
        visit_external: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowResult:
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
            "/workflows/request/crawl",
            body=maybe_transform(
                {
                    "bucket_name": bucket_name,
                    "crawl_id": crawl_id,
                    "engines": engines,
                    "url": url,
                    "absolute_only": absolute_only,
                    "batch_size": batch_size,
                    "depth": depth,
                    "keep_external": keep_external,
                    "max_urls": max_urls,
                    "max_workers": max_workers,
                    "stealth": stealth,
                    "visit_external": visit_external,
                },
                crawl_create_params.CrawlCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowResult,
        )

    def create_bulk(
        self,
        *,
        jobs: Iterable[CrawlRequestParam],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CrawlCreateBulkResponse:
        """
        Make up to 50 requests to temporal crawl worker

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/workflows/request/crawl/bulk",
            body=maybe_transform({"jobs": jobs}, crawl_create_bulk_params.CrawlCreateBulkParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CrawlCreateBulkResponse,
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

    async def create(
        self,
        *,
        bucket_name: str,
        crawl_id: str,
        engines: List[Literal["FLEET", "ZENROWS", "SCRAPINGBEE", "FLEET_ASYNC", "FLEET_WORKFLOW"]],
        url: str,
        absolute_only: bool | NotGiven = NOT_GIVEN,
        batch_size: int | NotGiven = NOT_GIVEN,
        depth: int | NotGiven = NOT_GIVEN,
        keep_external: bool | NotGiven = NOT_GIVEN,
        max_urls: int | NotGiven = NOT_GIVEN,
        max_workers: int | NotGiven = NOT_GIVEN,
        stealth: bool | NotGiven = NOT_GIVEN,
        visit_external: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowResult:
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
            "/workflows/request/crawl",
            body=await async_maybe_transform(
                {
                    "bucket_name": bucket_name,
                    "crawl_id": crawl_id,
                    "engines": engines,
                    "url": url,
                    "absolute_only": absolute_only,
                    "batch_size": batch_size,
                    "depth": depth,
                    "keep_external": keep_external,
                    "max_urls": max_urls,
                    "max_workers": max_workers,
                    "stealth": stealth,
                    "visit_external": visit_external,
                },
                crawl_create_params.CrawlCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowResult,
        )

    async def create_bulk(
        self,
        *,
        jobs: Iterable[CrawlRequestParam],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CrawlCreateBulkResponse:
        """
        Make up to 50 requests to temporal crawl worker

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/workflows/request/crawl/bulk",
            body=await async_maybe_transform({"jobs": jobs}, crawl_create_bulk_params.CrawlCreateBulkParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CrawlCreateBulkResponse,
        )


class CrawlResourceWithRawResponse:
    def __init__(self, crawl: CrawlResource) -> None:
        self._crawl = crawl

        self.create = to_raw_response_wrapper(
            crawl.create,
        )
        self.create_bulk = to_raw_response_wrapper(
            crawl.create_bulk,
        )


class AsyncCrawlResourceWithRawResponse:
    def __init__(self, crawl: AsyncCrawlResource) -> None:
        self._crawl = crawl

        self.create = async_to_raw_response_wrapper(
            crawl.create,
        )
        self.create_bulk = async_to_raw_response_wrapper(
            crawl.create_bulk,
        )


class CrawlResourceWithStreamingResponse:
    def __init__(self, crawl: CrawlResource) -> None:
        self._crawl = crawl

        self.create = to_streamed_response_wrapper(
            crawl.create,
        )
        self.create_bulk = to_streamed_response_wrapper(
            crawl.create_bulk,
        )


class AsyncCrawlResourceWithStreamingResponse:
    def __init__(self, crawl: AsyncCrawlResource) -> None:
        self._crawl = crawl

        self.create = async_to_streamed_response_wrapper(
            crawl.create,
        )
        self.create_bulk = async_to_streamed_response_wrapper(
            crawl.create_bulk,
        )
