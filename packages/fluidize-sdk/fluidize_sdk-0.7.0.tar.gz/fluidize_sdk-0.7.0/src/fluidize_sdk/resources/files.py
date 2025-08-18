# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import (
    file_save_editor_file_params,
    file_save_file_content_params,
    file_get_simulation_path_params,
    file_get_project_node_path_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.signed_url import SignedURL
from ..types.save_file_response import SaveFileResponse
from ..types.file_list_directory_response import FileListDirectoryResponse
from ..types.file_load_editor_file_response import FileLoadEditorFileResponse

__all__ = ["FilesResource", "AsyncFilesResource"]


class FilesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FilesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return FilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FilesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return FilesResourceWithStreamingResponse(self)

    def fetch_download_signed_url(
        self,
        file_path: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SignedURL:
        """
        Generate a signed URL for downloading a file from cloud storage.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_path:
            raise ValueError(f"Expected a non-empty value for `file_path` but received {file_path!r}")
        return self._get(
            f"/files/fetch-download-signed-url/{file_path}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SignedURL,
        )

    def fetch_upload_signed_url(
        self,
        file_path: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SignedURL:
        """
        Generate a signed URL for uploading a file to cloud storage.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_path:
            raise ValueError(f"Expected a non-empty value for `file_path` but received {file_path!r}")
        return self._get(
            f"/files/fetch-upload-signed-url/{file_path}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SignedURL,
        )

    def get_project_node_path(
        self,
        *,
        id: str,
        node_id: str,
        description: str | NotGiven = NOT_GIVEN,
        label: str | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        metadata_version: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Get the path for a node within a specific project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/files/get_project_node_path/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "id": id,
                        "node_id": node_id,
                        "description": description,
                        "label": label,
                        "location": location,
                        "metadata_version": metadata_version,
                        "status": status,
                    },
                    file_get_project_node_path_params.FileGetProjectNodePathParams,
                ),
            ),
            cast_to=str,
        )

    def get_simulation_path(
        self,
        *,
        node_id: str,
        sim_global: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Get the initial directory response for simulations (global or user-specific).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/files/get_simulation_path/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "node_id": node_id,
                        "sim_global": sim_global,
                    },
                    file_get_simulation_path_params.FileGetSimulationPathParams,
                ),
            ),
            cast_to=str,
        )

    def list_directory(
        self,
        file_path: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileListDirectoryResponse:
        """
        List the contents of a directory for a given file path

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_path:
            raise ValueError(f"Expected a non-empty value for `file_path` but received {file_path!r}")
        return self._get(
            f"/files/list-directory/{file_path}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileListDirectoryResponse,
        )

    def load_editor_file(
        self,
        file_path: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileLoadEditorFileResponse:
        """
        Load a file from a specific path for the editor.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_path:
            raise ValueError(f"Expected a non-empty value for `file_path` but received {file_path!r}")
        return self._get(
            f"/files/load-editor-file/{file_path}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileLoadEditorFileResponse,
        )

    def save_editor_file(
        self,
        *,
        content: str,
        path: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SaveFileResponse:
        """
        Save content to a file in the editor.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/files/save-editor-file",
            body=maybe_transform(
                {
                    "content": content,
                    "path": path,
                },
                file_save_editor_file_params.FileSaveEditorFileParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SaveFileResponse,
        )

    def save_file_content(
        self,
        file_path: str,
        *,
        content: str,
        path: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SaveFileResponse:
        """
        Save content to a file in the editor.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_path:
            raise ValueError(f"Expected a non-empty value for `file_path` but received {file_path!r}")
        return self._post(
            f"/files/content/{file_path}",
            body=maybe_transform(
                {
                    "content": content,
                    "path": path,
                },
                file_save_file_content_params.FileSaveFileContentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SaveFileResponse,
        )

    def stream_file(
        self,
        file_path: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Stream a file from a specific path.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_path:
            raise ValueError(f"Expected a non-empty value for `file_path` but received {file_path!r}")
        return self._get(
            f"/files/stream-file/{file_path}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncFilesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFilesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncFilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFilesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return AsyncFilesResourceWithStreamingResponse(self)

    async def fetch_download_signed_url(
        self,
        file_path: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SignedURL:
        """
        Generate a signed URL for downloading a file from cloud storage.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_path:
            raise ValueError(f"Expected a non-empty value for `file_path` but received {file_path!r}")
        return await self._get(
            f"/files/fetch-download-signed-url/{file_path}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SignedURL,
        )

    async def fetch_upload_signed_url(
        self,
        file_path: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SignedURL:
        """
        Generate a signed URL for uploading a file to cloud storage.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_path:
            raise ValueError(f"Expected a non-empty value for `file_path` but received {file_path!r}")
        return await self._get(
            f"/files/fetch-upload-signed-url/{file_path}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SignedURL,
        )

    async def get_project_node_path(
        self,
        *,
        id: str,
        node_id: str,
        description: str | NotGiven = NOT_GIVEN,
        label: str | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        metadata_version: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Get the path for a node within a specific project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/files/get_project_node_path/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "id": id,
                        "node_id": node_id,
                        "description": description,
                        "label": label,
                        "location": location,
                        "metadata_version": metadata_version,
                        "status": status,
                    },
                    file_get_project_node_path_params.FileGetProjectNodePathParams,
                ),
            ),
            cast_to=str,
        )

    async def get_simulation_path(
        self,
        *,
        node_id: str,
        sim_global: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Get the initial directory response for simulations (global or user-specific).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/files/get_simulation_path/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "node_id": node_id,
                        "sim_global": sim_global,
                    },
                    file_get_simulation_path_params.FileGetSimulationPathParams,
                ),
            ),
            cast_to=str,
        )

    async def list_directory(
        self,
        file_path: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileListDirectoryResponse:
        """
        List the contents of a directory for a given file path

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_path:
            raise ValueError(f"Expected a non-empty value for `file_path` but received {file_path!r}")
        return await self._get(
            f"/files/list-directory/{file_path}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileListDirectoryResponse,
        )

    async def load_editor_file(
        self,
        file_path: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileLoadEditorFileResponse:
        """
        Load a file from a specific path for the editor.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_path:
            raise ValueError(f"Expected a non-empty value for `file_path` but received {file_path!r}")
        return await self._get(
            f"/files/load-editor-file/{file_path}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileLoadEditorFileResponse,
        )

    async def save_editor_file(
        self,
        *,
        content: str,
        path: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SaveFileResponse:
        """
        Save content to a file in the editor.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/files/save-editor-file",
            body=await async_maybe_transform(
                {
                    "content": content,
                    "path": path,
                },
                file_save_editor_file_params.FileSaveEditorFileParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SaveFileResponse,
        )

    async def save_file_content(
        self,
        file_path: str,
        *,
        content: str,
        path: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SaveFileResponse:
        """
        Save content to a file in the editor.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_path:
            raise ValueError(f"Expected a non-empty value for `file_path` but received {file_path!r}")
        return await self._post(
            f"/files/content/{file_path}",
            body=await async_maybe_transform(
                {
                    "content": content,
                    "path": path,
                },
                file_save_file_content_params.FileSaveFileContentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SaveFileResponse,
        )

    async def stream_file(
        self,
        file_path: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Stream a file from a specific path.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_path:
            raise ValueError(f"Expected a non-empty value for `file_path` but received {file_path!r}")
        return await self._get(
            f"/files/stream-file/{file_path}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class FilesResourceWithRawResponse:
    def __init__(self, files: FilesResource) -> None:
        self._files = files

        self.fetch_download_signed_url = to_raw_response_wrapper(
            files.fetch_download_signed_url,
        )
        self.fetch_upload_signed_url = to_raw_response_wrapper(
            files.fetch_upload_signed_url,
        )
        self.get_project_node_path = to_raw_response_wrapper(
            files.get_project_node_path,
        )
        self.get_simulation_path = to_raw_response_wrapper(
            files.get_simulation_path,
        )
        self.list_directory = to_raw_response_wrapper(
            files.list_directory,
        )
        self.load_editor_file = to_raw_response_wrapper(
            files.load_editor_file,
        )
        self.save_editor_file = to_raw_response_wrapper(
            files.save_editor_file,
        )
        self.save_file_content = to_raw_response_wrapper(
            files.save_file_content,
        )
        self.stream_file = to_raw_response_wrapper(
            files.stream_file,
        )


class AsyncFilesResourceWithRawResponse:
    def __init__(self, files: AsyncFilesResource) -> None:
        self._files = files

        self.fetch_download_signed_url = async_to_raw_response_wrapper(
            files.fetch_download_signed_url,
        )
        self.fetch_upload_signed_url = async_to_raw_response_wrapper(
            files.fetch_upload_signed_url,
        )
        self.get_project_node_path = async_to_raw_response_wrapper(
            files.get_project_node_path,
        )
        self.get_simulation_path = async_to_raw_response_wrapper(
            files.get_simulation_path,
        )
        self.list_directory = async_to_raw_response_wrapper(
            files.list_directory,
        )
        self.load_editor_file = async_to_raw_response_wrapper(
            files.load_editor_file,
        )
        self.save_editor_file = async_to_raw_response_wrapper(
            files.save_editor_file,
        )
        self.save_file_content = async_to_raw_response_wrapper(
            files.save_file_content,
        )
        self.stream_file = async_to_raw_response_wrapper(
            files.stream_file,
        )


class FilesResourceWithStreamingResponse:
    def __init__(self, files: FilesResource) -> None:
        self._files = files

        self.fetch_download_signed_url = to_streamed_response_wrapper(
            files.fetch_download_signed_url,
        )
        self.fetch_upload_signed_url = to_streamed_response_wrapper(
            files.fetch_upload_signed_url,
        )
        self.get_project_node_path = to_streamed_response_wrapper(
            files.get_project_node_path,
        )
        self.get_simulation_path = to_streamed_response_wrapper(
            files.get_simulation_path,
        )
        self.list_directory = to_streamed_response_wrapper(
            files.list_directory,
        )
        self.load_editor_file = to_streamed_response_wrapper(
            files.load_editor_file,
        )
        self.save_editor_file = to_streamed_response_wrapper(
            files.save_editor_file,
        )
        self.save_file_content = to_streamed_response_wrapper(
            files.save_file_content,
        )
        self.stream_file = to_streamed_response_wrapper(
            files.stream_file,
        )


class AsyncFilesResourceWithStreamingResponse:
    def __init__(self, files: AsyncFilesResource) -> None:
        self._files = files

        self.fetch_download_signed_url = async_to_streamed_response_wrapper(
            files.fetch_download_signed_url,
        )
        self.fetch_upload_signed_url = async_to_streamed_response_wrapper(
            files.fetch_upload_signed_url,
        )
        self.get_project_node_path = async_to_streamed_response_wrapper(
            files.get_project_node_path,
        )
        self.get_simulation_path = async_to_streamed_response_wrapper(
            files.get_simulation_path,
        )
        self.list_directory = async_to_streamed_response_wrapper(
            files.list_directory,
        )
        self.load_editor_file = async_to_streamed_response_wrapper(
            files.load_editor_file,
        )
        self.save_editor_file = async_to_streamed_response_wrapper(
            files.save_editor_file,
        )
        self.save_file_content = async_to_streamed_response_wrapper(
            files.save_file_content,
        )
        self.stream_file = async_to_streamed_response_wrapper(
            files.stream_file,
        )
