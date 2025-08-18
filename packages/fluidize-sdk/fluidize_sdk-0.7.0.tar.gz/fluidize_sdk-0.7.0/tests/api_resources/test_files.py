# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fluidize_sdk import FluidizeSDK, AsyncFluidizeSDK
from fluidize_sdk.types import (
    SignedURL,
    SaveFileResponse,
    FileListDirectoryResponse,
    FileLoadEditorFileResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFiles:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_fetch_download_signed_url(self, client: FluidizeSDK) -> None:
        file = client.files.fetch_download_signed_url(
            "file_path",
        )
        assert_matches_type(SignedURL, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_fetch_download_signed_url(self, client: FluidizeSDK) -> None:
        response = client.files.with_raw_response.fetch_download_signed_url(
            "file_path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(SignedURL, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_fetch_download_signed_url(self, client: FluidizeSDK) -> None:
        with client.files.with_streaming_response.fetch_download_signed_url(
            "file_path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(SignedURL, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_fetch_download_signed_url(self, client: FluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_path` but received ''"):
            client.files.with_raw_response.fetch_download_signed_url(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_fetch_upload_signed_url(self, client: FluidizeSDK) -> None:
        file = client.files.fetch_upload_signed_url(
            "file_path",
        )
        assert_matches_type(SignedURL, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_fetch_upload_signed_url(self, client: FluidizeSDK) -> None:
        response = client.files.with_raw_response.fetch_upload_signed_url(
            "file_path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(SignedURL, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_fetch_upload_signed_url(self, client: FluidizeSDK) -> None:
        with client.files.with_streaming_response.fetch_upload_signed_url(
            "file_path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(SignedURL, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_fetch_upload_signed_url(self, client: FluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_path` but received ''"):
            client.files.with_raw_response.fetch_upload_signed_url(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_project_node_path(self, client: FluidizeSDK) -> None:
        file = client.files.get_project_node_path(
            id="id",
            node_id="node_id",
        )
        assert_matches_type(str, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_project_node_path_with_all_params(self, client: FluidizeSDK) -> None:
        file = client.files.get_project_node_path(
            id="id",
            node_id="node_id",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(str, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_project_node_path(self, client: FluidizeSDK) -> None:
        response = client.files.with_raw_response.get_project_node_path(
            id="id",
            node_id="node_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(str, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_project_node_path(self, client: FluidizeSDK) -> None:
        with client.files.with_streaming_response.get_project_node_path(
            id="id",
            node_id="node_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(str, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_simulation_path(self, client: FluidizeSDK) -> None:
        file = client.files.get_simulation_path(
            node_id="node_id",
            sim_global=True,
        )
        assert_matches_type(str, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_simulation_path(self, client: FluidizeSDK) -> None:
        response = client.files.with_raw_response.get_simulation_path(
            node_id="node_id",
            sim_global=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(str, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_simulation_path(self, client: FluidizeSDK) -> None:
        with client.files.with_streaming_response.get_simulation_path(
            node_id="node_id",
            sim_global=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(str, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_directory(self, client: FluidizeSDK) -> None:
        file = client.files.list_directory(
            "file_path",
        )
        assert_matches_type(FileListDirectoryResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_directory(self, client: FluidizeSDK) -> None:
        response = client.files.with_raw_response.list_directory(
            "file_path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileListDirectoryResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_directory(self, client: FluidizeSDK) -> None:
        with client.files.with_streaming_response.list_directory(
            "file_path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(FileListDirectoryResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_directory(self, client: FluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_path` but received ''"):
            client.files.with_raw_response.list_directory(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_load_editor_file(self, client: FluidizeSDK) -> None:
        file = client.files.load_editor_file(
            "file_path",
        )
        assert_matches_type(FileLoadEditorFileResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_load_editor_file(self, client: FluidizeSDK) -> None:
        response = client.files.with_raw_response.load_editor_file(
            "file_path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileLoadEditorFileResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_load_editor_file(self, client: FluidizeSDK) -> None:
        with client.files.with_streaming_response.load_editor_file(
            "file_path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(FileLoadEditorFileResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_load_editor_file(self, client: FluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_path` but received ''"):
            client.files.with_raw_response.load_editor_file(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_save_editor_file(self, client: FluidizeSDK) -> None:
        file = client.files.save_editor_file(
            content="content",
            path="path",
        )
        assert_matches_type(SaveFileResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_save_editor_file(self, client: FluidizeSDK) -> None:
        response = client.files.with_raw_response.save_editor_file(
            content="content",
            path="path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(SaveFileResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_save_editor_file(self, client: FluidizeSDK) -> None:
        with client.files.with_streaming_response.save_editor_file(
            content="content",
            path="path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(SaveFileResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_save_file_content(self, client: FluidizeSDK) -> None:
        file = client.files.save_file_content(
            file_path="file_path",
            content="content",
            path="path",
        )
        assert_matches_type(SaveFileResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_save_file_content(self, client: FluidizeSDK) -> None:
        response = client.files.with_raw_response.save_file_content(
            file_path="file_path",
            content="content",
            path="path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(SaveFileResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_save_file_content(self, client: FluidizeSDK) -> None:
        with client.files.with_streaming_response.save_file_content(
            file_path="file_path",
            content="content",
            path="path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(SaveFileResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_save_file_content(self, client: FluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_path` but received ''"):
            client.files.with_raw_response.save_file_content(
                file_path="",
                content="content",
                path="path",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_stream_file(self, client: FluidizeSDK) -> None:
        file = client.files.stream_file(
            "file_path",
        )
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_stream_file(self, client: FluidizeSDK) -> None:
        response = client.files.with_raw_response.stream_file(
            "file_path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_stream_file(self, client: FluidizeSDK) -> None:
        with client.files.with_streaming_response.stream_file(
            "file_path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(object, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_stream_file(self, client: FluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_path` but received ''"):
            client.files.with_raw_response.stream_file(
                "",
            )


class TestAsyncFiles:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_fetch_download_signed_url(self, async_client: AsyncFluidizeSDK) -> None:
        file = await async_client.files.fetch_download_signed_url(
            "file_path",
        )
        assert_matches_type(SignedURL, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_fetch_download_signed_url(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.files.with_raw_response.fetch_download_signed_url(
            "file_path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(SignedURL, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_fetch_download_signed_url(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.files.with_streaming_response.fetch_download_signed_url(
            "file_path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(SignedURL, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_fetch_download_signed_url(self, async_client: AsyncFluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_path` but received ''"):
            await async_client.files.with_raw_response.fetch_download_signed_url(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_fetch_upload_signed_url(self, async_client: AsyncFluidizeSDK) -> None:
        file = await async_client.files.fetch_upload_signed_url(
            "file_path",
        )
        assert_matches_type(SignedURL, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_fetch_upload_signed_url(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.files.with_raw_response.fetch_upload_signed_url(
            "file_path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(SignedURL, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_fetch_upload_signed_url(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.files.with_streaming_response.fetch_upload_signed_url(
            "file_path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(SignedURL, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_fetch_upload_signed_url(self, async_client: AsyncFluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_path` but received ''"):
            await async_client.files.with_raw_response.fetch_upload_signed_url(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_project_node_path(self, async_client: AsyncFluidizeSDK) -> None:
        file = await async_client.files.get_project_node_path(
            id="id",
            node_id="node_id",
        )
        assert_matches_type(str, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_project_node_path_with_all_params(self, async_client: AsyncFluidizeSDK) -> None:
        file = await async_client.files.get_project_node_path(
            id="id",
            node_id="node_id",
            description="description",
            label="label",
            location="location",
            metadata_version="metadata_version",
            status="status",
        )
        assert_matches_type(str, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_project_node_path(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.files.with_raw_response.get_project_node_path(
            id="id",
            node_id="node_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(str, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_project_node_path(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.files.with_streaming_response.get_project_node_path(
            id="id",
            node_id="node_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(str, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_simulation_path(self, async_client: AsyncFluidizeSDK) -> None:
        file = await async_client.files.get_simulation_path(
            node_id="node_id",
            sim_global=True,
        )
        assert_matches_type(str, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_simulation_path(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.files.with_raw_response.get_simulation_path(
            node_id="node_id",
            sim_global=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(str, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_simulation_path(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.files.with_streaming_response.get_simulation_path(
            node_id="node_id",
            sim_global=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(str, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_directory(self, async_client: AsyncFluidizeSDK) -> None:
        file = await async_client.files.list_directory(
            "file_path",
        )
        assert_matches_type(FileListDirectoryResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_directory(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.files.with_raw_response.list_directory(
            "file_path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(FileListDirectoryResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_directory(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.files.with_streaming_response.list_directory(
            "file_path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(FileListDirectoryResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_directory(self, async_client: AsyncFluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_path` but received ''"):
            await async_client.files.with_raw_response.list_directory(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_load_editor_file(self, async_client: AsyncFluidizeSDK) -> None:
        file = await async_client.files.load_editor_file(
            "file_path",
        )
        assert_matches_type(FileLoadEditorFileResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_load_editor_file(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.files.with_raw_response.load_editor_file(
            "file_path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(FileLoadEditorFileResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_load_editor_file(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.files.with_streaming_response.load_editor_file(
            "file_path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(FileLoadEditorFileResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_load_editor_file(self, async_client: AsyncFluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_path` but received ''"):
            await async_client.files.with_raw_response.load_editor_file(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_save_editor_file(self, async_client: AsyncFluidizeSDK) -> None:
        file = await async_client.files.save_editor_file(
            content="content",
            path="path",
        )
        assert_matches_type(SaveFileResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_save_editor_file(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.files.with_raw_response.save_editor_file(
            content="content",
            path="path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(SaveFileResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_save_editor_file(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.files.with_streaming_response.save_editor_file(
            content="content",
            path="path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(SaveFileResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_save_file_content(self, async_client: AsyncFluidizeSDK) -> None:
        file = await async_client.files.save_file_content(
            file_path="file_path",
            content="content",
            path="path",
        )
        assert_matches_type(SaveFileResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_save_file_content(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.files.with_raw_response.save_file_content(
            file_path="file_path",
            content="content",
            path="path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(SaveFileResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_save_file_content(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.files.with_streaming_response.save_file_content(
            file_path="file_path",
            content="content",
            path="path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(SaveFileResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_save_file_content(self, async_client: AsyncFluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_path` but received ''"):
            await async_client.files.with_raw_response.save_file_content(
                file_path="",
                content="content",
                path="path",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_stream_file(self, async_client: AsyncFluidizeSDK) -> None:
        file = await async_client.files.stream_file(
            "file_path",
        )
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_stream_file(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.files.with_raw_response.stream_file(
            "file_path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_stream_file(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.files.with_streaming_response.stream_file(
            "file_path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(object, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_stream_file(self, async_client: AsyncFluidizeSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_path` but received ''"):
            await async_client.files.with_raw_response.stream_file(
                "",
            )
