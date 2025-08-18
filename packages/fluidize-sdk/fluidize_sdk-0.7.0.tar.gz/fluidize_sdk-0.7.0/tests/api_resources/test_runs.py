# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fluidize_sdk import FluidizeSDK, AsyncFluidizeSDK
from fluidize_sdk.types import (
    RunListResponse,
    RunRunFlowResponse,
    RunFetchRunNodesResponse,
    RunGetPropertiesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRuns:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: FluidizeSDK) -> None:
        run = client.runs.list(
            id="id",
        )
        assert_matches_type(RunListResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: FluidizeSDK) -> None:
        run = client.runs.list(
            id="id",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(RunListResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: FluidizeSDK) -> None:
        response = client.runs.with_raw_response.list(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(RunListResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: FluidizeSDK) -> None:
        with client.runs.with_streaming_response.list(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = response.parse()
            assert_matches_type(RunListResponse, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_fetch_run_nodes(self, client: FluidizeSDK) -> None:
        run = client.runs.fetch_run_nodes(
            run_folder="run_folder",
            id="id",
        )
        assert_matches_type(RunFetchRunNodesResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_fetch_run_nodes_with_all_params(self, client: FluidizeSDK) -> None:
        run = client.runs.fetch_run_nodes(
            run_folder="run_folder",
            id="id",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(RunFetchRunNodesResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_fetch_run_nodes(self, client: FluidizeSDK) -> None:
        response = client.runs.with_raw_response.fetch_run_nodes(
            run_folder="run_folder",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(RunFetchRunNodesResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_fetch_run_nodes(self, client: FluidizeSDK) -> None:
        with client.runs.with_streaming_response.fetch_run_nodes(
            run_folder="run_folder",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = response.parse()
            assert_matches_type(RunFetchRunNodesResponse, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_fetch_run_nodes(self, client: FluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_folder` but received ''"):
            client.runs.with_raw_response.fetch_run_nodes(
                run_folder="",
                id="id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_file(self, client: FluidizeSDK) -> None:
        run = client.runs.get_file(
            "path",
        )
        assert run is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_file(self, client: FluidizeSDK) -> None:
        response = client.runs.with_raw_response.get_file(
            "path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert run is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_file(self, client: FluidizeSDK) -> None:
        with client.runs.with_streaming_response.get_file(
            "path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = response.parse()
            assert run is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_file(self, client: FluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path` but received ''"):
            client.runs.with_raw_response.get_file(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_properties(self, client: FluidizeSDK) -> None:
        run = client.runs.get_properties(
            run_folder="run_folder",
            id="id",
        )
        assert_matches_type(RunGetPropertiesResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_properties_with_all_params(self, client: FluidizeSDK) -> None:
        run = client.runs.get_properties(
            run_folder="run_folder",
            id="id",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(RunGetPropertiesResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_properties(self, client: FluidizeSDK) -> None:
        response = client.runs.with_raw_response.get_properties(
            run_folder="run_folder",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(RunGetPropertiesResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_properties(self, client: FluidizeSDK) -> None:
        with client.runs.with_streaming_response.get_properties(
            run_folder="run_folder",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = response.parse()
            assert_matches_type(RunGetPropertiesResponse, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_properties(self, client: FluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_folder` but received ''"):
            client.runs.with_raw_response.get_properties(
                run_folder="",
                id="id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_run_flow(self, client: FluidizeSDK) -> None:
        run = client.runs.run_flow(
            payload={},
            project={"id": "id"},
        )
        assert_matches_type(RunRunFlowResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_run_flow_with_all_params(self, client: FluidizeSDK) -> None:
        run = client.runs.run_flow(
            payload={
                "description": "description",
                "name": "name",
                "tags": ["string"],
            },
            project={
                "id": "id",
                "description": "description",
                "label": "label",
                "location": "location",
                "metadata_version": "metadata_version",
                "status": "status",
            },
        )
        assert_matches_type(RunRunFlowResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_run_flow(self, client: FluidizeSDK) -> None:
        response = client.runs.with_raw_response.run_flow(
            payload={},
            project={"id": "id"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(RunRunFlowResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_run_flow(self, client: FluidizeSDK) -> None:
        with client.runs.with_streaming_response.run_flow(
            payload={},
            project={"id": "id"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = response.parse()
            assert_matches_type(RunRunFlowResponse, run, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRuns:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFluidizeSDK) -> None:
        run = await async_client.runs.list(
            id="id",
        )
        assert_matches_type(RunListResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFluidizeSDK) -> None:
        run = await async_client.runs.list(
            id="id",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(RunListResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.runs.with_raw_response.list(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = await response.parse()
        assert_matches_type(RunListResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.runs.with_streaming_response.list(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = await response.parse()
            assert_matches_type(RunListResponse, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_fetch_run_nodes(self, async_client: AsyncFluidizeSDK) -> None:
        run = await async_client.runs.fetch_run_nodes(
            run_folder="run_folder",
            id="id",
        )
        assert_matches_type(RunFetchRunNodesResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_fetch_run_nodes_with_all_params(self, async_client: AsyncFluidizeSDK) -> None:
        run = await async_client.runs.fetch_run_nodes(
            run_folder="run_folder",
            id="id",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(RunFetchRunNodesResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_fetch_run_nodes(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.runs.with_raw_response.fetch_run_nodes(
            run_folder="run_folder",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = await response.parse()
        assert_matches_type(RunFetchRunNodesResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_fetch_run_nodes(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.runs.with_streaming_response.fetch_run_nodes(
            run_folder="run_folder",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = await response.parse()
            assert_matches_type(RunFetchRunNodesResponse, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_fetch_run_nodes(self, async_client: AsyncFluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_folder` but received ''"):
            await async_client.runs.with_raw_response.fetch_run_nodes(
                run_folder="",
                id="id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_file(self, async_client: AsyncFluidizeSDK) -> None:
        run = await async_client.runs.get_file(
            "path",
        )
        assert run is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_file(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.runs.with_raw_response.get_file(
            "path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = await response.parse()
        assert run is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_file(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.runs.with_streaming_response.get_file(
            "path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = await response.parse()
            assert run is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_file(self, async_client: AsyncFluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path` but received ''"):
            await async_client.runs.with_raw_response.get_file(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_properties(self, async_client: AsyncFluidizeSDK) -> None:
        run = await async_client.runs.get_properties(
            run_folder="run_folder",
            id="id",
        )
        assert_matches_type(RunGetPropertiesResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_properties_with_all_params(self, async_client: AsyncFluidizeSDK) -> None:
        run = await async_client.runs.get_properties(
            run_folder="run_folder",
            id="id",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(RunGetPropertiesResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_properties(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.runs.with_raw_response.get_properties(
            run_folder="run_folder",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = await response.parse()
        assert_matches_type(RunGetPropertiesResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_properties(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.runs.with_streaming_response.get_properties(
            run_folder="run_folder",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = await response.parse()
            assert_matches_type(RunGetPropertiesResponse, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_properties(self, async_client: AsyncFluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_folder` but received ''"):
            await async_client.runs.with_raw_response.get_properties(
                run_folder="",
                id="id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_run_flow(self, async_client: AsyncFluidizeSDK) -> None:
        run = await async_client.runs.run_flow(
            payload={},
            project={"id": "id"},
        )
        assert_matches_type(RunRunFlowResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_run_flow_with_all_params(self, async_client: AsyncFluidizeSDK) -> None:
        run = await async_client.runs.run_flow(
            payload={
                "description": "description",
                "name": "name",
                "tags": ["string"],
            },
            project={
                "id": "id",
                "description": "description",
                "label": "label",
                "location": "location",
                "metadata_version": "metadata_version",
                "status": "status",
            },
        )
        assert_matches_type(RunRunFlowResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_run_flow(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.runs.with_raw_response.run_flow(
            payload={},
            project={"id": "id"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = await response.parse()
        assert_matches_type(RunRunFlowResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_run_flow(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.runs.with_streaming_response.run_flow(
            payload={},
            project={"id": "id"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = await response.parse()
            assert_matches_type(RunRunFlowResponse, run, path=["response"])

        assert cast(Any, response.is_closed) is True
