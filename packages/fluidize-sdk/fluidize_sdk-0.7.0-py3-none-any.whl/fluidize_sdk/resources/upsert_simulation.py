# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ..types import upsert_simulation_create_params
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
from ..types.upsert_simulation_create_response import UpsertSimulationCreateResponse

__all__ = ["UpsertSimulationResource", "AsyncUpsertSimulationResource"]


class UpsertSimulationResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UpsertSimulationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return UpsertSimulationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UpsertSimulationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return UpsertSimulationResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        container_image: str,
        environment_variables: Iterable[upsert_simulation_create_params.EnvironmentVariable],
        name: str,
        package_managers: Iterable[upsert_simulation_create_params.PackageManager],
        post_install_script: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UpsertSimulationCreateResponse:
        """
        Upsert Simulation

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/upsert_simulation",
            body=maybe_transform(
                {
                    "container_image": container_image,
                    "environment_variables": environment_variables,
                    "name": name,
                    "package_managers": package_managers,
                    "post_install_script": post_install_script,
                },
                upsert_simulation_create_params.UpsertSimulationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpsertSimulationCreateResponse,
        )


class AsyncUpsertSimulationResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUpsertSimulationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncUpsertSimulationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUpsertSimulationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return AsyncUpsertSimulationResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        container_image: str,
        environment_variables: Iterable[upsert_simulation_create_params.EnvironmentVariable],
        name: str,
        package_managers: Iterable[upsert_simulation_create_params.PackageManager],
        post_install_script: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UpsertSimulationCreateResponse:
        """
        Upsert Simulation

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/upsert_simulation",
            body=await async_maybe_transform(
                {
                    "container_image": container_image,
                    "environment_variables": environment_variables,
                    "name": name,
                    "package_managers": package_managers,
                    "post_install_script": post_install_script,
                },
                upsert_simulation_create_params.UpsertSimulationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UpsertSimulationCreateResponse,
        )


class UpsertSimulationResourceWithRawResponse:
    def __init__(self, upsert_simulation: UpsertSimulationResource) -> None:
        self._upsert_simulation = upsert_simulation

        self.create = to_raw_response_wrapper(
            upsert_simulation.create,
        )


class AsyncUpsertSimulationResourceWithRawResponse:
    def __init__(self, upsert_simulation: AsyncUpsertSimulationResource) -> None:
        self._upsert_simulation = upsert_simulation

        self.create = async_to_raw_response_wrapper(
            upsert_simulation.create,
        )


class UpsertSimulationResourceWithStreamingResponse:
    def __init__(self, upsert_simulation: UpsertSimulationResource) -> None:
        self._upsert_simulation = upsert_simulation

        self.create = to_streamed_response_wrapper(
            upsert_simulation.create,
        )


class AsyncUpsertSimulationResourceWithStreamingResponse:
    def __init__(self, upsert_simulation: AsyncUpsertSimulationResource) -> None:
        self._upsert_simulation = upsert_simulation

        self.create = async_to_streamed_response_wrapper(
            upsert_simulation.create,
        )
