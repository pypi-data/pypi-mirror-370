# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Union, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Body,
    Omit,
    Query,
    Headers,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from ._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .resources import candy, files, graph, projects, simulation, test_connection, list_environments, upsert_simulation
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError, FluidizeSDKError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
    make_request_options,
)
from .resources.auth import auth
from .resources.runs import runs
from .resources.utils import utils

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "FluidizeSDK",
    "AsyncFluidizeSDK",
    "Client",
    "AsyncClient",
]


class FluidizeSDK(SyncAPIClient):
    test_connection: test_connection.TestConnectionResource
    candy: candy.CandyResource
    graph: graph.GraphResource
    projects: projects.ProjectsResource
    files: files.FilesResource
    runs: runs.RunsResource
    auth: auth.AuthResource
    list_environments: list_environments.ListEnvironmentsResource
    upsert_simulation: upsert_simulation.UpsertSimulationResource
    utils: utils.UtilsResource
    simulation: simulation.SimulationResource
    with_raw_response: FluidizeSDKWithRawResponse
    with_streaming_response: FluidizeSDKWithStreamedResponse

    # client options
    api_token: str

    def __init__(
        self,
        *,
        api_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous FluidizeSDK client instance.

        This automatically infers the `api_token` argument from the `FLUIDIZE_API_TOKEN` environment variable if it is not provided.
        """
        if api_token is None:
            api_token = os.environ.get("FLUIDIZE_API_TOKEN")
        if api_token is None:
            raise FluidizeSDKError(
                "The api_token client option must be set either by passing api_token to the client or by setting the FLUIDIZE_API_TOKEN environment variable"
            )
        self.api_token = api_token

        if base_url is None:
            base_url = os.environ.get("FLUIDIZE_SDK_BASE_URL")
        if base_url is None:
            base_url = f"https://api.fluidize.ai"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.test_connection = test_connection.TestConnectionResource(self)
        self.candy = candy.CandyResource(self)
        self.graph = graph.GraphResource(self)
        self.projects = projects.ProjectsResource(self)
        self.files = files.FilesResource(self)
        self.runs = runs.RunsResource(self)
        self.auth = auth.AuthResource(self)
        self.list_environments = list_environments.ListEnvironmentsResource(self)
        self.upsert_simulation = upsert_simulation.UpsertSimulationResource(self)
        self.utils = utils.UtilsResource(self)
        self.simulation = simulation.SimulationResource(self)
        self.with_raw_response = FluidizeSDKWithRawResponse(self)
        self.with_streaming_response = FluidizeSDKWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_token = self.api_token
        return {"Authorization": f"Bearer {api_token}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_token=api_token or self.api_token,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    def retrieve_root(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Read Root"""
        return self.get(
            "/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncFluidizeSDK(AsyncAPIClient):
    test_connection: test_connection.AsyncTestConnectionResource
    candy: candy.AsyncCandyResource
    graph: graph.AsyncGraphResource
    projects: projects.AsyncProjectsResource
    files: files.AsyncFilesResource
    runs: runs.AsyncRunsResource
    auth: auth.AsyncAuthResource
    list_environments: list_environments.AsyncListEnvironmentsResource
    upsert_simulation: upsert_simulation.AsyncUpsertSimulationResource
    utils: utils.AsyncUtilsResource
    simulation: simulation.AsyncSimulationResource
    with_raw_response: AsyncFluidizeSDKWithRawResponse
    with_streaming_response: AsyncFluidizeSDKWithStreamedResponse

    # client options
    api_token: str

    def __init__(
        self,
        *,
        api_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncFluidizeSDK client instance.

        This automatically infers the `api_token` argument from the `FLUIDIZE_API_TOKEN` environment variable if it is not provided.
        """
        if api_token is None:
            api_token = os.environ.get("FLUIDIZE_API_TOKEN")
        if api_token is None:
            raise FluidizeSDKError(
                "The api_token client option must be set either by passing api_token to the client or by setting the FLUIDIZE_API_TOKEN environment variable"
            )
        self.api_token = api_token

        if base_url is None:
            base_url = os.environ.get("FLUIDIZE_SDK_BASE_URL")
        if base_url is None:
            base_url = f"https://api.fluidize.ai"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.test_connection = test_connection.AsyncTestConnectionResource(self)
        self.candy = candy.AsyncCandyResource(self)
        self.graph = graph.AsyncGraphResource(self)
        self.projects = projects.AsyncProjectsResource(self)
        self.files = files.AsyncFilesResource(self)
        self.runs = runs.AsyncRunsResource(self)
        self.auth = auth.AsyncAuthResource(self)
        self.list_environments = list_environments.AsyncListEnvironmentsResource(self)
        self.upsert_simulation = upsert_simulation.AsyncUpsertSimulationResource(self)
        self.utils = utils.AsyncUtilsResource(self)
        self.simulation = simulation.AsyncSimulationResource(self)
        self.with_raw_response = AsyncFluidizeSDKWithRawResponse(self)
        self.with_streaming_response = AsyncFluidizeSDKWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_token = self.api_token
        return {"Authorization": f"Bearer {api_token}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_token=api_token or self.api_token,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    async def retrieve_root(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Read Root"""
        return await self.get(
            "/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class FluidizeSDKWithRawResponse:
    def __init__(self, client: FluidizeSDK) -> None:
        self.test_connection = test_connection.TestConnectionResourceWithRawResponse(client.test_connection)
        self.candy = candy.CandyResourceWithRawResponse(client.candy)
        self.graph = graph.GraphResourceWithRawResponse(client.graph)
        self.projects = projects.ProjectsResourceWithRawResponse(client.projects)
        self.files = files.FilesResourceWithRawResponse(client.files)
        self.runs = runs.RunsResourceWithRawResponse(client.runs)
        self.auth = auth.AuthResourceWithRawResponse(client.auth)
        self.list_environments = list_environments.ListEnvironmentsResourceWithRawResponse(client.list_environments)
        self.upsert_simulation = upsert_simulation.UpsertSimulationResourceWithRawResponse(client.upsert_simulation)
        self.utils = utils.UtilsResourceWithRawResponse(client.utils)
        self.simulation = simulation.SimulationResourceWithRawResponse(client.simulation)

        self.retrieve_root = to_raw_response_wrapper(
            client.retrieve_root,
        )


class AsyncFluidizeSDKWithRawResponse:
    def __init__(self, client: AsyncFluidizeSDK) -> None:
        self.test_connection = test_connection.AsyncTestConnectionResourceWithRawResponse(client.test_connection)
        self.candy = candy.AsyncCandyResourceWithRawResponse(client.candy)
        self.graph = graph.AsyncGraphResourceWithRawResponse(client.graph)
        self.projects = projects.AsyncProjectsResourceWithRawResponse(client.projects)
        self.files = files.AsyncFilesResourceWithRawResponse(client.files)
        self.runs = runs.AsyncRunsResourceWithRawResponse(client.runs)
        self.auth = auth.AsyncAuthResourceWithRawResponse(client.auth)
        self.list_environments = list_environments.AsyncListEnvironmentsResourceWithRawResponse(
            client.list_environments
        )
        self.upsert_simulation = upsert_simulation.AsyncUpsertSimulationResourceWithRawResponse(
            client.upsert_simulation
        )
        self.utils = utils.AsyncUtilsResourceWithRawResponse(client.utils)
        self.simulation = simulation.AsyncSimulationResourceWithRawResponse(client.simulation)

        self.retrieve_root = async_to_raw_response_wrapper(
            client.retrieve_root,
        )


class FluidizeSDKWithStreamedResponse:
    def __init__(self, client: FluidizeSDK) -> None:
        self.test_connection = test_connection.TestConnectionResourceWithStreamingResponse(client.test_connection)
        self.candy = candy.CandyResourceWithStreamingResponse(client.candy)
        self.graph = graph.GraphResourceWithStreamingResponse(client.graph)
        self.projects = projects.ProjectsResourceWithStreamingResponse(client.projects)
        self.files = files.FilesResourceWithStreamingResponse(client.files)
        self.runs = runs.RunsResourceWithStreamingResponse(client.runs)
        self.auth = auth.AuthResourceWithStreamingResponse(client.auth)
        self.list_environments = list_environments.ListEnvironmentsResourceWithStreamingResponse(
            client.list_environments
        )
        self.upsert_simulation = upsert_simulation.UpsertSimulationResourceWithStreamingResponse(
            client.upsert_simulation
        )
        self.utils = utils.UtilsResourceWithStreamingResponse(client.utils)
        self.simulation = simulation.SimulationResourceWithStreamingResponse(client.simulation)

        self.retrieve_root = to_streamed_response_wrapper(
            client.retrieve_root,
        )


class AsyncFluidizeSDKWithStreamedResponse:
    def __init__(self, client: AsyncFluidizeSDK) -> None:
        self.test_connection = test_connection.AsyncTestConnectionResourceWithStreamingResponse(client.test_connection)
        self.candy = candy.AsyncCandyResourceWithStreamingResponse(client.candy)
        self.graph = graph.AsyncGraphResourceWithStreamingResponse(client.graph)
        self.projects = projects.AsyncProjectsResourceWithStreamingResponse(client.projects)
        self.files = files.AsyncFilesResourceWithStreamingResponse(client.files)
        self.runs = runs.AsyncRunsResourceWithStreamingResponse(client.runs)
        self.auth = auth.AsyncAuthResourceWithStreamingResponse(client.auth)
        self.list_environments = list_environments.AsyncListEnvironmentsResourceWithStreamingResponse(
            client.list_environments
        )
        self.upsert_simulation = upsert_simulation.AsyncUpsertSimulationResourceWithStreamingResponse(
            client.upsert_simulation
        )
        self.utils = utils.AsyncUtilsResourceWithStreamingResponse(client.utils)
        self.simulation = simulation.AsyncSimulationResourceWithStreamingResponse(client.simulation)

        self.retrieve_root = async_to_streamed_response_wrapper(
            client.retrieve_root,
        )


Client = FluidizeSDK

AsyncClient = AsyncFluidizeSDK
