# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cartography import Cartography, AsyncCartography
from tests.utils import assert_matches_type
from cartography.types.workflows.request import (
    WorkflowResult,
    CrawlCreateBulkResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCrawl:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Cartography) -> None:
        crawl = client.workflows.request.crawl.create(
            bucket_name="bucket_name",
            crawl_id="crawl_id",
            engines=["FLEET"],
            url="url",
        )
        assert_matches_type(WorkflowResult, crawl, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Cartography) -> None:
        crawl = client.workflows.request.crawl.create(
            bucket_name="bucket_name",
            crawl_id="crawl_id",
            engines=["FLEET"],
            url="url",
            absolute_only=True,
            batch_size=0,
            depth=0,
            keep_external=True,
            max_urls=0,
            max_workers=0,
            stealth=True,
            visit_external=True,
        )
        assert_matches_type(WorkflowResult, crawl, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Cartography) -> None:
        response = client.workflows.request.crawl.with_raw_response.create(
            bucket_name="bucket_name",
            crawl_id="crawl_id",
            engines=["FLEET"],
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        crawl = response.parse()
        assert_matches_type(WorkflowResult, crawl, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Cartography) -> None:
        with client.workflows.request.crawl.with_streaming_response.create(
            bucket_name="bucket_name",
            crawl_id="crawl_id",
            engines=["FLEET"],
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            crawl = response.parse()
            assert_matches_type(WorkflowResult, crawl, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_bulk(self, client: Cartography) -> None:
        crawl = client.workflows.request.crawl.create_bulk(
            jobs=[
                {
                    "bucket_name": "bucket_name",
                    "crawl_id": "crawl_id",
                    "engines": ["FLEET"],
                    "url": "url",
                }
            ],
        )
        assert_matches_type(CrawlCreateBulkResponse, crawl, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_bulk(self, client: Cartography) -> None:
        response = client.workflows.request.crawl.with_raw_response.create_bulk(
            jobs=[
                {
                    "bucket_name": "bucket_name",
                    "crawl_id": "crawl_id",
                    "engines": ["FLEET"],
                    "url": "url",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        crawl = response.parse()
        assert_matches_type(CrawlCreateBulkResponse, crawl, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_bulk(self, client: Cartography) -> None:
        with client.workflows.request.crawl.with_streaming_response.create_bulk(
            jobs=[
                {
                    "bucket_name": "bucket_name",
                    "crawl_id": "crawl_id",
                    "engines": ["FLEET"],
                    "url": "url",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            crawl = response.parse()
            assert_matches_type(CrawlCreateBulkResponse, crawl, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCrawl:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncCartography) -> None:
        crawl = await async_client.workflows.request.crawl.create(
            bucket_name="bucket_name",
            crawl_id="crawl_id",
            engines=["FLEET"],
            url="url",
        )
        assert_matches_type(WorkflowResult, crawl, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncCartography) -> None:
        crawl = await async_client.workflows.request.crawl.create(
            bucket_name="bucket_name",
            crawl_id="crawl_id",
            engines=["FLEET"],
            url="url",
            absolute_only=True,
            batch_size=0,
            depth=0,
            keep_external=True,
            max_urls=0,
            max_workers=0,
            stealth=True,
            visit_external=True,
        )
        assert_matches_type(WorkflowResult, crawl, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncCartography) -> None:
        response = await async_client.workflows.request.crawl.with_raw_response.create(
            bucket_name="bucket_name",
            crawl_id="crawl_id",
            engines=["FLEET"],
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        crawl = await response.parse()
        assert_matches_type(WorkflowResult, crawl, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncCartography) -> None:
        async with async_client.workflows.request.crawl.with_streaming_response.create(
            bucket_name="bucket_name",
            crawl_id="crawl_id",
            engines=["FLEET"],
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            crawl = await response.parse()
            assert_matches_type(WorkflowResult, crawl, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_bulk(self, async_client: AsyncCartography) -> None:
        crawl = await async_client.workflows.request.crawl.create_bulk(
            jobs=[
                {
                    "bucket_name": "bucket_name",
                    "crawl_id": "crawl_id",
                    "engines": ["FLEET"],
                    "url": "url",
                }
            ],
        )
        assert_matches_type(CrawlCreateBulkResponse, crawl, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_bulk(self, async_client: AsyncCartography) -> None:
        response = await async_client.workflows.request.crawl.with_raw_response.create_bulk(
            jobs=[
                {
                    "bucket_name": "bucket_name",
                    "crawl_id": "crawl_id",
                    "engines": ["FLEET"],
                    "url": "url",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        crawl = await response.parse()
        assert_matches_type(CrawlCreateBulkResponse, crawl, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_bulk(self, async_client: AsyncCartography) -> None:
        async with async_client.workflows.request.crawl.with_streaming_response.create_bulk(
            jobs=[
                {
                    "bucket_name": "bucket_name",
                    "crawl_id": "crawl_id",
                    "engines": ["FLEET"],
                    "url": "url",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            crawl = await response.parse()
            assert_matches_type(CrawlCreateBulkResponse, crawl, path=["response"])

        assert cast(Any, response.is_closed) is True
