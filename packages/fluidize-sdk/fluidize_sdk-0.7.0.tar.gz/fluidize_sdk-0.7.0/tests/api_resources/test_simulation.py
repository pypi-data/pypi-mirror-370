# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fluidize_sdk import FluidizeSDK, AsyncFluidizeSDK
from fluidize_sdk.types import SimulationListSimulationsResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSimulation:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_simulations(self, client: FluidizeSDK) -> None:
        simulation = client.simulation.list_simulations(
            sim_global=True,
        )
        assert_matches_type(SimulationListSimulationsResponse, simulation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_simulations(self, client: FluidizeSDK) -> None:
        response = client.simulation.with_raw_response.list_simulations(
            sim_global=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        simulation = response.parse()
        assert_matches_type(SimulationListSimulationsResponse, simulation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_simulations(self, client: FluidizeSDK) -> None:
        with client.simulation.with_streaming_response.list_simulations(
            sim_global=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            simulation = response.parse()
            assert_matches_type(SimulationListSimulationsResponse, simulation, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSimulation:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_simulations(self, async_client: AsyncFluidizeSDK) -> None:
        simulation = await async_client.simulation.list_simulations(
            sim_global=True,
        )
        assert_matches_type(SimulationListSimulationsResponse, simulation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_simulations(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.simulation.with_raw_response.list_simulations(
            sim_global=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        simulation = await response.parse()
        assert_matches_type(SimulationListSimulationsResponse, simulation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_simulations(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.simulation.with_streaming_response.list_simulations(
            sim_global=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            simulation = await response.parse()
            assert_matches_type(SimulationListSimulationsResponse, simulation, path=["response"])

        assert cast(Any, response.is_closed) is True
