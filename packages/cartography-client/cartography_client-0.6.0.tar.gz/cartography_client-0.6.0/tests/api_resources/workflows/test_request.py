# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cartography import Cartography, AsyncCartography
from tests.utils import assert_matches_type
from cartography.types.workflows import RequestCreateDownloadResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRequest:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_download(self, client: Cartography) -> None:
        request = client.workflows.request.create_download(
            bucket_name="bucket_name",
            crawl_id="crawl_id",
            downloader_type="downloader_type",
            urls=["string"],
        )
        assert_matches_type(RequestCreateDownloadResponse, request, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_download(self, client: Cartography) -> None:
        response = client.workflows.request.with_raw_response.create_download(
            bucket_name="bucket_name",
            crawl_id="crawl_id",
            downloader_type="downloader_type",
            urls=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        request = response.parse()
        assert_matches_type(RequestCreateDownloadResponse, request, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_download(self, client: Cartography) -> None:
        with client.workflows.request.with_streaming_response.create_download(
            bucket_name="bucket_name",
            crawl_id="crawl_id",
            downloader_type="downloader_type",
            urls=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            request = response.parse()
            assert_matches_type(RequestCreateDownloadResponse, request, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRequest:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_download(self, async_client: AsyncCartography) -> None:
        request = await async_client.workflows.request.create_download(
            bucket_name="bucket_name",
            crawl_id="crawl_id",
            downloader_type="downloader_type",
            urls=["string"],
        )
        assert_matches_type(RequestCreateDownloadResponse, request, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_download(self, async_client: AsyncCartography) -> None:
        response = await async_client.workflows.request.with_raw_response.create_download(
            bucket_name="bucket_name",
            crawl_id="crawl_id",
            downloader_type="downloader_type",
            urls=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        request = await response.parse()
        assert_matches_type(RequestCreateDownloadResponse, request, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_download(self, async_client: AsyncCartography) -> None:
        async with async_client.workflows.request.with_streaming_response.create_download(
            bucket_name="bucket_name",
            crawl_id="crawl_id",
            downloader_type="downloader_type",
            urls=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            request = await response.parse()
            assert_matches_type(RequestCreateDownloadResponse, request, path=["response"])

        assert cast(Any, response.is_closed) is True
