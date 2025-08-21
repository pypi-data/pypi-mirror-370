# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cartography import Cartography, AsyncCartography
from tests.utils import assert_matches_type
from cartography.types import (
    ScrapeScrapeBulkResponse,
    ScrapeScrapeSingleResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestScrape:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_scrape_bulk(self, client: Cartography) -> None:
        scrape = client.scrape.scrape_bulk(
            crawl_id="crawl-123",
            engines=[{"engine_type": "FLEET"}],
            s3_bucket="my-scraping-bucket",
            urls=["https://example.com", "https://example.org"],
        )
        assert_matches_type(ScrapeScrapeBulkResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_scrape_bulk_with_all_params(self, client: Cartography) -> None:
        scrape = client.scrape.scrape_bulk(
            crawl_id="crawl-123",
            engines=[
                {
                    "engine_type": "FLEET",
                    "headers": {"foo": "string"},
                    "proxy": "proxy",
                    "screenshot": True,
                    "timeout": 0,
                    "wait_for": "wait_for",
                }
            ],
            s3_bucket="my-scraping-bucket",
            urls=["https://example.com", "https://example.org"],
            batch_size=50,
            debug=True,
            max_workers=8,
        )
        assert_matches_type(ScrapeScrapeBulkResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_scrape_bulk(self, client: Cartography) -> None:
        response = client.scrape.with_raw_response.scrape_bulk(
            crawl_id="crawl-123",
            engines=[{"engine_type": "FLEET"}],
            s3_bucket="my-scraping-bucket",
            urls=["https://example.com", "https://example.org"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scrape = response.parse()
        assert_matches_type(ScrapeScrapeBulkResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_scrape_bulk(self, client: Cartography) -> None:
        with client.scrape.with_streaming_response.scrape_bulk(
            crawl_id="crawl-123",
            engines=[{"engine_type": "FLEET"}],
            s3_bucket="my-scraping-bucket",
            urls=["https://example.com", "https://example.org"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scrape = response.parse()
            assert_matches_type(ScrapeScrapeBulkResponse, scrape, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_scrape_single(self, client: Cartography) -> None:
        scrape = client.scrape.scrape_single(
            engines=[{"engine_type": "FLEET"}],
            url="https://example.com",
        )
        assert_matches_type(ScrapeScrapeSingleResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_scrape_single(self, client: Cartography) -> None:
        response = client.scrape.with_raw_response.scrape_single(
            engines=[{"engine_type": "FLEET"}],
            url="https://example.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scrape = response.parse()
        assert_matches_type(ScrapeScrapeSingleResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_scrape_single(self, client: Cartography) -> None:
        with client.scrape.with_streaming_response.scrape_single(
            engines=[{"engine_type": "FLEET"}],
            url="https://example.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scrape = response.parse()
            assert_matches_type(ScrapeScrapeSingleResponse, scrape, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncScrape:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_scrape_bulk(self, async_client: AsyncCartography) -> None:
        scrape = await async_client.scrape.scrape_bulk(
            crawl_id="crawl-123",
            engines=[{"engine_type": "FLEET"}],
            s3_bucket="my-scraping-bucket",
            urls=["https://example.com", "https://example.org"],
        )
        assert_matches_type(ScrapeScrapeBulkResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_scrape_bulk_with_all_params(self, async_client: AsyncCartography) -> None:
        scrape = await async_client.scrape.scrape_bulk(
            crawl_id="crawl-123",
            engines=[
                {
                    "engine_type": "FLEET",
                    "headers": {"foo": "string"},
                    "proxy": "proxy",
                    "screenshot": True,
                    "timeout": 0,
                    "wait_for": "wait_for",
                }
            ],
            s3_bucket="my-scraping-bucket",
            urls=["https://example.com", "https://example.org"],
            batch_size=50,
            debug=True,
            max_workers=8,
        )
        assert_matches_type(ScrapeScrapeBulkResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_scrape_bulk(self, async_client: AsyncCartography) -> None:
        response = await async_client.scrape.with_raw_response.scrape_bulk(
            crawl_id="crawl-123",
            engines=[{"engine_type": "FLEET"}],
            s3_bucket="my-scraping-bucket",
            urls=["https://example.com", "https://example.org"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scrape = await response.parse()
        assert_matches_type(ScrapeScrapeBulkResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_scrape_bulk(self, async_client: AsyncCartography) -> None:
        async with async_client.scrape.with_streaming_response.scrape_bulk(
            crawl_id="crawl-123",
            engines=[{"engine_type": "FLEET"}],
            s3_bucket="my-scraping-bucket",
            urls=["https://example.com", "https://example.org"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scrape = await response.parse()
            assert_matches_type(ScrapeScrapeBulkResponse, scrape, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_scrape_single(self, async_client: AsyncCartography) -> None:
        scrape = await async_client.scrape.scrape_single(
            engines=[{"engine_type": "FLEET"}],
            url="https://example.com",
        )
        assert_matches_type(ScrapeScrapeSingleResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_scrape_single(self, async_client: AsyncCartography) -> None:
        response = await async_client.scrape.with_raw_response.scrape_single(
            engines=[{"engine_type": "FLEET"}],
            url="https://example.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scrape = await response.parse()
        assert_matches_type(ScrapeScrapeSingleResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_scrape_single(self, async_client: AsyncCartography) -> None:
        async with async_client.scrape.with_streaming_response.scrape_single(
            engines=[{"engine_type": "FLEET"}],
            url="https://example.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scrape = await response.parse()
            assert_matches_type(ScrapeScrapeSingleResponse, scrape, path=["response"])

        assert cast(Any, response.is_closed) is True
