# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fluidize_sdk import FluidizeSDK, AsyncFluidizeSDK
from fluidize_sdk.types.utils import RetrievalMode

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRetrievalMode:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: FluidizeSDK) -> None:
        retrieval_mode = client.utils.retrieval_mode.retrieve()
        assert_matches_type(RetrievalMode, retrieval_mode, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: FluidizeSDK) -> None:
        response = client.utils.retrieval_mode.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        retrieval_mode = response.parse()
        assert_matches_type(RetrievalMode, retrieval_mode, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: FluidizeSDK) -> None:
        with client.utils.retrieval_mode.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            retrieval_mode = response.parse()
            assert_matches_type(RetrievalMode, retrieval_mode, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: FluidizeSDK) -> None:
        retrieval_mode = client.utils.retrieval_mode.update(
            mode="mode",
        )
        assert_matches_type(RetrievalMode, retrieval_mode, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: FluidizeSDK) -> None:
        response = client.utils.retrieval_mode.with_raw_response.update(
            mode="mode",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        retrieval_mode = response.parse()
        assert_matches_type(RetrievalMode, retrieval_mode, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: FluidizeSDK) -> None:
        with client.utils.retrieval_mode.with_streaming_response.update(
            mode="mode",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            retrieval_mode = response.parse()
            assert_matches_type(RetrievalMode, retrieval_mode, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRetrievalMode:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFluidizeSDK) -> None:
        retrieval_mode = await async_client.utils.retrieval_mode.retrieve()
        assert_matches_type(RetrievalMode, retrieval_mode, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.utils.retrieval_mode.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        retrieval_mode = await response.parse()
        assert_matches_type(RetrievalMode, retrieval_mode, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.utils.retrieval_mode.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            retrieval_mode = await response.parse()
            assert_matches_type(RetrievalMode, retrieval_mode, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncFluidizeSDK) -> None:
        retrieval_mode = await async_client.utils.retrieval_mode.update(
            mode="mode",
        )
        assert_matches_type(RetrievalMode, retrieval_mode, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.utils.retrieval_mode.with_raw_response.update(
            mode="mode",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        retrieval_mode = await response.parse()
        assert_matches_type(RetrievalMode, retrieval_mode, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.utils.retrieval_mode.with_streaming_response.update(
            mode="mode",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            retrieval_mode = await response.parse()
            assert_matches_type(RetrievalMode, retrieval_mode, path=["response"])

        assert cast(Any, response.is_closed) is True
