# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cartography import Cartography, AsyncCartography
from tests.utils import assert_matches_type
from cartography.types import (
    DownloadCreateBulkResponse,
    DownloadCreateSingleResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDownload:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_bulk(self, client: Cartography) -> None:
        download = client.download.create_bulk(
            crawl_id="download-123",
            s3_bucket="my-downloads",
            urls=["https://example.com/file1.pdf", "https://example.com/file2.pdf"],
        )
        assert_matches_type(DownloadCreateBulkResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_bulk_with_all_params(self, client: Cartography) -> None:
        download = client.download.create_bulk(
            crawl_id="download-123",
            s3_bucket="my-downloads",
            urls=["https://example.com/file1.pdf", "https://example.com/file2.pdf"],
            batch_size=1,
            debug=True,
            downloader_type="FLEET_ASYNC",
            max_workers=8,
            wait_until="commit",
        )
        assert_matches_type(DownloadCreateBulkResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_bulk(self, client: Cartography) -> None:
        response = client.download.with_raw_response.create_bulk(
            crawl_id="download-123",
            s3_bucket="my-downloads",
            urls=["https://example.com/file1.pdf", "https://example.com/file2.pdf"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        download = response.parse()
        assert_matches_type(DownloadCreateBulkResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_bulk(self, client: Cartography) -> None:
        with client.download.with_streaming_response.create_bulk(
            crawl_id="download-123",
            s3_bucket="my-downloads",
            urls=["https://example.com/file1.pdf", "https://example.com/file2.pdf"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            download = response.parse()
            assert_matches_type(DownloadCreateBulkResponse, download, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_single(self, client: Cartography) -> None:
        download = client.download.create_single(
            s3_bucket="my-downloads",
            url="https://example.com/file.pdf",
        )
        assert_matches_type(DownloadCreateSingleResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_single_with_all_params(self, client: Cartography) -> None:
        download = client.download.create_single(
            s3_bucket="my-downloads",
            url="https://example.com/file.pdf",
            downloader_type="FLEET_ASYNC",
            s3_key="s3_key",
            api_timeout=1000,
            wait_until="load",
        )
        assert_matches_type(DownloadCreateSingleResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_single(self, client: Cartography) -> None:
        response = client.download.with_raw_response.create_single(
            s3_bucket="my-downloads",
            url="https://example.com/file.pdf",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        download = response.parse()
        assert_matches_type(DownloadCreateSingleResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_single(self, client: Cartography) -> None:
        with client.download.with_streaming_response.create_single(
            s3_bucket="my-downloads",
            url="https://example.com/file.pdf",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            download = response.parse()
            assert_matches_type(DownloadCreateSingleResponse, download, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDownload:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_bulk(self, async_client: AsyncCartography) -> None:
        download = await async_client.download.create_bulk(
            crawl_id="download-123",
            s3_bucket="my-downloads",
            urls=["https://example.com/file1.pdf", "https://example.com/file2.pdf"],
        )
        assert_matches_type(DownloadCreateBulkResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_bulk_with_all_params(self, async_client: AsyncCartography) -> None:
        download = await async_client.download.create_bulk(
            crawl_id="download-123",
            s3_bucket="my-downloads",
            urls=["https://example.com/file1.pdf", "https://example.com/file2.pdf"],
            batch_size=1,
            debug=True,
            downloader_type="FLEET_ASYNC",
            max_workers=8,
            wait_until="commit",
        )
        assert_matches_type(DownloadCreateBulkResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_bulk(self, async_client: AsyncCartography) -> None:
        response = await async_client.download.with_raw_response.create_bulk(
            crawl_id="download-123",
            s3_bucket="my-downloads",
            urls=["https://example.com/file1.pdf", "https://example.com/file2.pdf"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        download = await response.parse()
        assert_matches_type(DownloadCreateBulkResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_bulk(self, async_client: AsyncCartography) -> None:
        async with async_client.download.with_streaming_response.create_bulk(
            crawl_id="download-123",
            s3_bucket="my-downloads",
            urls=["https://example.com/file1.pdf", "https://example.com/file2.pdf"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            download = await response.parse()
            assert_matches_type(DownloadCreateBulkResponse, download, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_single(self, async_client: AsyncCartography) -> None:
        download = await async_client.download.create_single(
            s3_bucket="my-downloads",
            url="https://example.com/file.pdf",
        )
        assert_matches_type(DownloadCreateSingleResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_single_with_all_params(self, async_client: AsyncCartography) -> None:
        download = await async_client.download.create_single(
            s3_bucket="my-downloads",
            url="https://example.com/file.pdf",
            downloader_type="FLEET_ASYNC",
            s3_key="s3_key",
            api_timeout=1000,
            wait_until="load",
        )
        assert_matches_type(DownloadCreateSingleResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_single(self, async_client: AsyncCartography) -> None:
        response = await async_client.download.with_raw_response.create_single(
            s3_bucket="my-downloads",
            url="https://example.com/file.pdf",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        download = await response.parse()
        assert_matches_type(DownloadCreateSingleResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_single(self, async_client: AsyncCartography) -> None:
        async with async_client.download.with_streaming_response.create_single(
            s3_bucket="my-downloads",
            url="https://example.com/file.pdf",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            download = await response.parse()
            assert_matches_type(DownloadCreateSingleResponse, download, path=["response"])

        assert cast(Any, response.is_closed) is True
