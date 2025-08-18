# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fluidize_sdk import FluidizeSDK, AsyncFluidizeSDK
from fluidize_sdk.types import (
    GraphEdge,
    GraphNode,
    Parameter,
    GraphRetrieveResponse,
    GraphGetParametersResponse,
    GraphSetParametersResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestGraph:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: FluidizeSDK) -> None:
        graph = client.graph.retrieve(
            id="id",
        )
        assert_matches_type(GraphRetrieveResponse, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: FluidizeSDK) -> None:
        graph = client.graph.retrieve(
            id="id",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(GraphRetrieveResponse, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: FluidizeSDK) -> None:
        response = client.graph.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = response.parse()
        assert_matches_type(GraphRetrieveResponse, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: FluidizeSDK) -> None:
        with client.graph.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = response.parse()
            assert_matches_type(GraphRetrieveResponse, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_edge(self, client: FluidizeSDK) -> None:
        graph = client.graph.delete_edge(
            edge_id="edge_id",
            id="id",
        )
        assert_matches_type(object, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_edge_with_all_params(self, client: FluidizeSDK) -> None:
        graph = client.graph.delete_edge(
            edge_id="edge_id",
            id="id",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(object, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete_edge(self, client: FluidizeSDK) -> None:
        response = client.graph.with_raw_response.delete_edge(
            edge_id="edge_id",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = response.parse()
        assert_matches_type(object, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete_edge(self, client: FluidizeSDK) -> None:
        with client.graph.with_streaming_response.delete_edge(
            edge_id="edge_id",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = response.parse()
            assert_matches_type(object, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete_edge(self, client: FluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `edge_id` but received ''"):
            client.graph.with_raw_response.delete_edge(
                edge_id="",
                id="id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_node(self, client: FluidizeSDK) -> None:
        graph = client.graph.delete_node(
            node_id="node_id",
            id="id",
        )
        assert_matches_type(object, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_node_with_all_params(self, client: FluidizeSDK) -> None:
        graph = client.graph.delete_node(
            node_id="node_id",
            id="id",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(object, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete_node(self, client: FluidizeSDK) -> None:
        response = client.graph.with_raw_response.delete_node(
            node_id="node_id",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = response.parse()
        assert_matches_type(object, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete_node(self, client: FluidizeSDK) -> None:
        with client.graph.with_streaming_response.delete_node(
            node_id="node_id",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = response.parse()
            assert_matches_type(object, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete_node(self, client: FluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `node_id` but received ''"):
            client.graph.with_raw_response.delete_node(
                node_id="",
                id="id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_parameters(self, client: FluidizeSDK) -> None:
        graph = client.graph.get_parameters(
            node_id="node_id",
            id="id",
        )
        assert_matches_type(GraphGetParametersResponse, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_parameters_with_all_params(self, client: FluidizeSDK) -> None:
        graph = client.graph.get_parameters(
            node_id="node_id",
            id="id",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(GraphGetParametersResponse, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_parameters(self, client: FluidizeSDK) -> None:
        response = client.graph.with_raw_response.get_parameters(
            node_id="node_id",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = response.parse()
        assert_matches_type(GraphGetParametersResponse, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_parameters(self, client: FluidizeSDK) -> None:
        with client.graph.with_streaming_response.get_parameters(
            node_id="node_id",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = response.parse()
            assert_matches_type(GraphGetParametersResponse, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_parameters(self, client: FluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `node_id` but received ''"):
            client.graph.with_raw_response.get_parameters(
                node_id="",
                id="id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_insert_node(self, client: FluidizeSDK) -> None:
        graph = client.graph.insert_node(
            node={
                "id": "id",
                "data": {"label": "label"},
                "position": {
                    "x": 0,
                    "y": 0,
                },
                "type": "type",
            },
            project={"id": "id"},
        )
        assert_matches_type(GraphNode, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_insert_node_with_all_params(self, client: FluidizeSDK) -> None:
        graph = client.graph.insert_node(
            node={
                "id": "id",
                "data": {
                    "label": "label",
                    "simulation_id": "simulation_id",
                },
                "position": {
                    "x": 0,
                    "y": 0,
                },
                "type": "type",
            },
            project={
                "id": "id",
                "description": "description",
                "label": "label",
                "location": "location",
                "metadata_version": "metadata_version",
                "status": "status",
            },
            sim_global=True,
        )
        assert_matches_type(GraphNode, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_insert_node(self, client: FluidizeSDK) -> None:
        response = client.graph.with_raw_response.insert_node(
            node={
                "id": "id",
                "data": {"label": "label"},
                "position": {
                    "x": 0,
                    "y": 0,
                },
                "type": "type",
            },
            project={"id": "id"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = response.parse()
        assert_matches_type(GraphNode, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_insert_node(self, client: FluidizeSDK) -> None:
        with client.graph.with_streaming_response.insert_node(
            node={
                "id": "id",
                "data": {"label": "label"},
                "position": {
                    "x": 0,
                    "y": 0,
                },
                "type": "type",
            },
            project={"id": "id"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = response.parse()
            assert_matches_type(GraphNode, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set_parameters(self, client: FluidizeSDK) -> None:
        graph = client.graph.set_parameters(
            node_id="node_id",
            id="id",
            body=[
                {
                    "description": "description",
                    "label": "label",
                    "name": "name",
                    "type": "type",
                    "value": "value",
                }
            ],
        )
        assert_matches_type(GraphSetParametersResponse, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set_parameters_with_all_params(self, client: FluidizeSDK) -> None:
        graph = client.graph.set_parameters(
            node_id="node_id",
            id="id",
            body=[
                {
                    "description": "description",
                    "label": "label",
                    "name": "name",
                    "type": "type",
                    "value": "value",
                    "latex": "latex",
                    "location": ["string"],
                    "options": [
                        {
                            "label": "label",
                            "value": "value",
                        }
                    ],
                    "scope": "scope",
                }
            ],
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(GraphSetParametersResponse, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_set_parameters(self, client: FluidizeSDK) -> None:
        response = client.graph.with_raw_response.set_parameters(
            node_id="node_id",
            id="id",
            body=[
                {
                    "description": "description",
                    "label": "label",
                    "name": "name",
                    "type": "type",
                    "value": "value",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = response.parse()
        assert_matches_type(GraphSetParametersResponse, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_set_parameters(self, client: FluidizeSDK) -> None:
        with client.graph.with_streaming_response.set_parameters(
            node_id="node_id",
            id="id",
            body=[
                {
                    "description": "description",
                    "label": "label",
                    "name": "name",
                    "type": "type",
                    "value": "value",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = response.parse()
            assert_matches_type(GraphSetParametersResponse, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_set_parameters(self, client: FluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `node_id` but received ''"):
            client.graph.with_raw_response.set_parameters(
                node_id="",
                id="id",
                body=[
                    {
                        "description": "description",
                        "label": "label",
                        "name": "name",
                        "type": "type",
                        "value": "value",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_sync(self, client: FluidizeSDK) -> None:
        graph = client.graph.sync(
            id="id",
        )
        assert_matches_type(object, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_sync_with_all_params(self, client: FluidizeSDK) -> None:
        graph = client.graph.sync(
            id="id",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(object, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_sync(self, client: FluidizeSDK) -> None:
        response = client.graph.with_raw_response.sync(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = response.parse()
        assert_matches_type(object, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_sync(self, client: FluidizeSDK) -> None:
        with client.graph.with_streaming_response.sync(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = response.parse()
            assert_matches_type(object, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_node_position(self, client: FluidizeSDK) -> None:
        graph = client.graph.update_node_position(
            query_id="id",
            body_id="id",
            data={"label": "label"},
            position={
                "x": 0,
                "y": 0,
            },
            type="type",
        )
        assert_matches_type(GraphNode, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_node_position_with_all_params(self, client: FluidizeSDK) -> None:
        graph = client.graph.update_node_position(
            query_id="id",
            body_id="id",
            data={
                "label": "label",
                "simulation_id": "simulation_id",
            },
            position={
                "x": 0,
                "y": 0,
            },
            type="type",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(GraphNode, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_node_position(self, client: FluidizeSDK) -> None:
        response = client.graph.with_raw_response.update_node_position(
            query_id="id",
            body_id="id",
            data={"label": "label"},
            position={
                "x": 0,
                "y": 0,
            },
            type="type",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = response.parse()
        assert_matches_type(GraphNode, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_node_position(self, client: FluidizeSDK) -> None:
        with client.graph.with_streaming_response.update_node_position(
            query_id="id",
            body_id="id",
            data={"label": "label"},
            position={
                "x": 0,
                "y": 0,
            },
            type="type",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = response.parse()
            assert_matches_type(GraphNode, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upsert_edge(self, client: FluidizeSDK) -> None:
        graph = client.graph.upsert_edge(
            query_id="id",
            body_id="id",
            source="source",
            target="target",
            type="type",
        )
        assert_matches_type(GraphEdge, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upsert_edge_with_all_params(self, client: FluidizeSDK) -> None:
        graph = client.graph.upsert_edge(
            query_id="id",
            body_id="id",
            source="source",
            target="target",
            type="type",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(GraphEdge, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_upsert_edge(self, client: FluidizeSDK) -> None:
        response = client.graph.with_raw_response.upsert_edge(
            query_id="id",
            body_id="id",
            source="source",
            target="target",
            type="type",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = response.parse()
        assert_matches_type(GraphEdge, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_upsert_edge(self, client: FluidizeSDK) -> None:
        with client.graph.with_streaming_response.upsert_edge(
            query_id="id",
            body_id="id",
            source="source",
            target="target",
            type="type",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = response.parse()
            assert_matches_type(GraphEdge, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upsert_parameter(self, client: FluidizeSDK) -> None:
        graph = client.graph.upsert_parameter(
            path="path",
            description="description",
            label="label",
            name="name",
            type="type",
            value="value",
        )
        assert_matches_type(Parameter, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upsert_parameter_with_all_params(self, client: FluidizeSDK) -> None:
        graph = client.graph.upsert_parameter(
            path="path",
            description="description",
            label="label",
            name="name",
            type="type",
            value="value",
            latex="latex",
            location=["string"],
            options=[
                {
                    "label": "label",
                    "value": "value",
                }
            ],
            scope="scope",
        )
        assert_matches_type(Parameter, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_upsert_parameter(self, client: FluidizeSDK) -> None:
        response = client.graph.with_raw_response.upsert_parameter(
            path="path",
            description="description",
            label="label",
            name="name",
            type="type",
            value="value",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = response.parse()
        assert_matches_type(Parameter, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_upsert_parameter(self, client: FluidizeSDK) -> None:
        with client.graph.with_streaming_response.upsert_parameter(
            path="path",
            description="description",
            label="label",
            name="name",
            type="type",
            value="value",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = response.parse()
            assert_matches_type(Parameter, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_upsert_parameter(self, client: FluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path` but received ''"):
            client.graph.with_raw_response.upsert_parameter(
                path="",
                description="description",
                label="label",
                name="name",
                type="type",
                value="value",
            )


class TestAsyncGraph:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.retrieve(
            id="id",
        )
        assert_matches_type(GraphRetrieveResponse, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.retrieve(
            id="id",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(GraphRetrieveResponse, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.graph.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = await response.parse()
        assert_matches_type(GraphRetrieveResponse, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.graph.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = await response.parse()
            assert_matches_type(GraphRetrieveResponse, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_edge(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.delete_edge(
            edge_id="edge_id",
            id="id",
        )
        assert_matches_type(object, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_edge_with_all_params(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.delete_edge(
            edge_id="edge_id",
            id="id",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(object, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete_edge(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.graph.with_raw_response.delete_edge(
            edge_id="edge_id",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = await response.parse()
        assert_matches_type(object, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete_edge(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.graph.with_streaming_response.delete_edge(
            edge_id="edge_id",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = await response.parse()
            assert_matches_type(object, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete_edge(self, async_client: AsyncFluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `edge_id` but received ''"):
            await async_client.graph.with_raw_response.delete_edge(
                edge_id="",
                id="id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_node(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.delete_node(
            node_id="node_id",
            id="id",
        )
        assert_matches_type(object, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_node_with_all_params(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.delete_node(
            node_id="node_id",
            id="id",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(object, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete_node(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.graph.with_raw_response.delete_node(
            node_id="node_id",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = await response.parse()
        assert_matches_type(object, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete_node(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.graph.with_streaming_response.delete_node(
            node_id="node_id",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = await response.parse()
            assert_matches_type(object, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete_node(self, async_client: AsyncFluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `node_id` but received ''"):
            await async_client.graph.with_raw_response.delete_node(
                node_id="",
                id="id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_parameters(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.get_parameters(
            node_id="node_id",
            id="id",
        )
        assert_matches_type(GraphGetParametersResponse, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_parameters_with_all_params(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.get_parameters(
            node_id="node_id",
            id="id",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(GraphGetParametersResponse, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_parameters(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.graph.with_raw_response.get_parameters(
            node_id="node_id",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = await response.parse()
        assert_matches_type(GraphGetParametersResponse, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_parameters(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.graph.with_streaming_response.get_parameters(
            node_id="node_id",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = await response.parse()
            assert_matches_type(GraphGetParametersResponse, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_parameters(self, async_client: AsyncFluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `node_id` but received ''"):
            await async_client.graph.with_raw_response.get_parameters(
                node_id="",
                id="id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_insert_node(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.insert_node(
            node={
                "id": "id",
                "data": {"label": "label"},
                "position": {
                    "x": 0,
                    "y": 0,
                },
                "type": "type",
            },
            project={"id": "id"},
        )
        assert_matches_type(GraphNode, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_insert_node_with_all_params(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.insert_node(
            node={
                "id": "id",
                "data": {
                    "label": "label",
                    "simulation_id": "simulation_id",
                },
                "position": {
                    "x": 0,
                    "y": 0,
                },
                "type": "type",
            },
            project={
                "id": "id",
                "description": "description",
                "label": "label",
                "location": "location",
                "metadata_version": "metadata_version",
                "status": "status",
            },
            sim_global=True,
        )
        assert_matches_type(GraphNode, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_insert_node(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.graph.with_raw_response.insert_node(
            node={
                "id": "id",
                "data": {"label": "label"},
                "position": {
                    "x": 0,
                    "y": 0,
                },
                "type": "type",
            },
            project={"id": "id"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = await response.parse()
        assert_matches_type(GraphNode, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_insert_node(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.graph.with_streaming_response.insert_node(
            node={
                "id": "id",
                "data": {"label": "label"},
                "position": {
                    "x": 0,
                    "y": 0,
                },
                "type": "type",
            },
            project={"id": "id"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = await response.parse()
            assert_matches_type(GraphNode, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set_parameters(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.set_parameters(
            node_id="node_id",
            id="id",
            body=[
                {
                    "description": "description",
                    "label": "label",
                    "name": "name",
                    "type": "type",
                    "value": "value",
                }
            ],
        )
        assert_matches_type(GraphSetParametersResponse, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set_parameters_with_all_params(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.set_parameters(
            node_id="node_id",
            id="id",
            body=[
                {
                    "description": "description",
                    "label": "label",
                    "name": "name",
                    "type": "type",
                    "value": "value",
                    "latex": "latex",
                    "location": ["string"],
                    "options": [
                        {
                            "label": "label",
                            "value": "value",
                        }
                    ],
                    "scope": "scope",
                }
            ],
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(GraphSetParametersResponse, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_set_parameters(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.graph.with_raw_response.set_parameters(
            node_id="node_id",
            id="id",
            body=[
                {
                    "description": "description",
                    "label": "label",
                    "name": "name",
                    "type": "type",
                    "value": "value",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = await response.parse()
        assert_matches_type(GraphSetParametersResponse, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_set_parameters(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.graph.with_streaming_response.set_parameters(
            node_id="node_id",
            id="id",
            body=[
                {
                    "description": "description",
                    "label": "label",
                    "name": "name",
                    "type": "type",
                    "value": "value",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = await response.parse()
            assert_matches_type(GraphSetParametersResponse, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_set_parameters(self, async_client: AsyncFluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `node_id` but received ''"):
            await async_client.graph.with_raw_response.set_parameters(
                node_id="",
                id="id",
                body=[
                    {
                        "description": "description",
                        "label": "label",
                        "name": "name",
                        "type": "type",
                        "value": "value",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_sync(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.sync(
            id="id",
        )
        assert_matches_type(object, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_sync_with_all_params(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.sync(
            id="id",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(object, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_sync(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.graph.with_raw_response.sync(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = await response.parse()
        assert_matches_type(object, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_sync(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.graph.with_streaming_response.sync(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = await response.parse()
            assert_matches_type(object, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_node_position(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.update_node_position(
            query_id="id",
            body_id="id",
            data={"label": "label"},
            position={
                "x": 0,
                "y": 0,
            },
            type="type",
        )
        assert_matches_type(GraphNode, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_node_position_with_all_params(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.update_node_position(
            query_id="id",
            body_id="id",
            data={
                "label": "label",
                "simulation_id": "simulation_id",
            },
            position={
                "x": 0,
                "y": 0,
            },
            type="type",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(GraphNode, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_node_position(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.graph.with_raw_response.update_node_position(
            query_id="id",
            body_id="id",
            data={"label": "label"},
            position={
                "x": 0,
                "y": 0,
            },
            type="type",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = await response.parse()
        assert_matches_type(GraphNode, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_node_position(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.graph.with_streaming_response.update_node_position(
            query_id="id",
            body_id="id",
            data={"label": "label"},
            position={
                "x": 0,
                "y": 0,
            },
            type="type",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = await response.parse()
            assert_matches_type(GraphNode, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upsert_edge(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.upsert_edge(
            query_id="id",
            body_id="id",
            source="source",
            target="target",
            type="type",
        )
        assert_matches_type(GraphEdge, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upsert_edge_with_all_params(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.upsert_edge(
            query_id="id",
            body_id="id",
            source="source",
            target="target",
            type="type",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(GraphEdge, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_upsert_edge(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.graph.with_raw_response.upsert_edge(
            query_id="id",
            body_id="id",
            source="source",
            target="target",
            type="type",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = await response.parse()
        assert_matches_type(GraphEdge, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_upsert_edge(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.graph.with_streaming_response.upsert_edge(
            query_id="id",
            body_id="id",
            source="source",
            target="target",
            type="type",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = await response.parse()
            assert_matches_type(GraphEdge, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upsert_parameter(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.upsert_parameter(
            path="path",
            description="description",
            label="label",
            name="name",
            type="type",
            value="value",
        )
        assert_matches_type(Parameter, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upsert_parameter_with_all_params(self, async_client: AsyncFluidizeSDK) -> None:
        graph = await async_client.graph.upsert_parameter(
            path="path",
            description="description",
            label="label",
            name="name",
            type="type",
            value="value",
            latex="latex",
            location=["string"],
            options=[
                {
                    "label": "label",
                    "value": "value",
                }
            ],
            scope="scope",
        )
        assert_matches_type(Parameter, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_upsert_parameter(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.graph.with_raw_response.upsert_parameter(
            path="path",
            description="description",
            label="label",
            name="name",
            type="type",
            value="value",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        graph = await response.parse()
        assert_matches_type(Parameter, graph, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_upsert_parameter(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.graph.with_streaming_response.upsert_parameter(
            path="path",
            description="description",
            label="label",
            name="name",
            type="type",
            value="value",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            graph = await response.parse()
            assert_matches_type(Parameter, graph, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_upsert_parameter(self, async_client: AsyncFluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path` but received ''"):
            await async_client.graph.with_raw_response.upsert_parameter(
                path="",
                description="description",
                label="label",
                name="name",
                type="type",
                value="value",
            )
