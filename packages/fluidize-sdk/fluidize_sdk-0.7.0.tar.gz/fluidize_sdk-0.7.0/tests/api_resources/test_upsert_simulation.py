# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fluidize_sdk import FluidizeSDK, AsyncFluidizeSDK
from fluidize_sdk.types import UpsertSimulationCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUpsertSimulation:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: FluidizeSDK) -> None:
        upsert_simulation = client.upsert_simulation.create(
            container_image="container_image",
            environment_variables=[
                {
                    "key": "key",
                    "value": "value",
                }
            ],
            name="name",
            package_managers=[
                {
                    "name": "name",
                    "packages": ["string"],
                    "version": "version",
                }
            ],
            post_install_script="post_install_script",
        )
        assert_matches_type(UpsertSimulationCreateResponse, upsert_simulation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: FluidizeSDK) -> None:
        response = client.upsert_simulation.with_raw_response.create(
            container_image="container_image",
            environment_variables=[
                {
                    "key": "key",
                    "value": "value",
                }
            ],
            name="name",
            package_managers=[
                {
                    "name": "name",
                    "packages": ["string"],
                    "version": "version",
                }
            ],
            post_install_script="post_install_script",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upsert_simulation = response.parse()
        assert_matches_type(UpsertSimulationCreateResponse, upsert_simulation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: FluidizeSDK) -> None:
        with client.upsert_simulation.with_streaming_response.create(
            container_image="container_image",
            environment_variables=[
                {
                    "key": "key",
                    "value": "value",
                }
            ],
            name="name",
            package_managers=[
                {
                    "name": "name",
                    "packages": ["string"],
                    "version": "version",
                }
            ],
            post_install_script="post_install_script",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upsert_simulation = response.parse()
            assert_matches_type(UpsertSimulationCreateResponse, upsert_simulation, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncUpsertSimulation:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFluidizeSDK) -> None:
        upsert_simulation = await async_client.upsert_simulation.create(
            container_image="container_image",
            environment_variables=[
                {
                    "key": "key",
                    "value": "value",
                }
            ],
            name="name",
            package_managers=[
                {
                    "name": "name",
                    "packages": ["string"],
                    "version": "version",
                }
            ],
            post_install_script="post_install_script",
        )
        assert_matches_type(UpsertSimulationCreateResponse, upsert_simulation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.upsert_simulation.with_raw_response.create(
            container_image="container_image",
            environment_variables=[
                {
                    "key": "key",
                    "value": "value",
                }
            ],
            name="name",
            package_managers=[
                {
                    "name": "name",
                    "packages": ["string"],
                    "version": "version",
                }
            ],
            post_install_script="post_install_script",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upsert_simulation = await response.parse()
        assert_matches_type(UpsertSimulationCreateResponse, upsert_simulation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.upsert_simulation.with_streaming_response.create(
            container_image="container_image",
            environment_variables=[
                {
                    "key": "key",
                    "value": "value",
                }
            ],
            name="name",
            package_managers=[
                {
                    "name": "name",
                    "packages": ["string"],
                    "version": "version",
                }
            ],
            post_install_script="post_install_script",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upsert_simulation = await response.parse()
            assert_matches_type(UpsertSimulationCreateResponse, upsert_simulation, path=["response"])

        assert cast(Any, response.is_closed) is True
