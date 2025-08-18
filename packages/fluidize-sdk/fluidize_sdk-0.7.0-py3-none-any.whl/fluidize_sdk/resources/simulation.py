# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import simulation_list_simulations_params
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
from ..types.simulation_list_simulations_response import SimulationListSimulationsResponse

__all__ = ["SimulationResource", "AsyncSimulationResource"]


class SimulationResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SimulationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return SimulationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SimulationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return SimulationResourceWithStreamingResponse(self)

    def list_simulations(
        self,
        *,
        sim_global: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimulationListSimulationsResponse:
        """Get a list of all simulation nodes available in the system.

        This function does
        not need to change as it reads from a different source.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/simulation/list_simulations",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"sim_global": sim_global}, simulation_list_simulations_params.SimulationListSimulationsParams
                ),
            ),
            cast_to=SimulationListSimulationsResponse,
        )


class AsyncSimulationResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSimulationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncSimulationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSimulationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return AsyncSimulationResourceWithStreamingResponse(self)

    async def list_simulations(
        self,
        *,
        sim_global: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimulationListSimulationsResponse:
        """Get a list of all simulation nodes available in the system.

        This function does
        not need to change as it reads from a different source.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/simulation/list_simulations",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"sim_global": sim_global}, simulation_list_simulations_params.SimulationListSimulationsParams
                ),
            ),
            cast_to=SimulationListSimulationsResponse,
        )


class SimulationResourceWithRawResponse:
    def __init__(self, simulation: SimulationResource) -> None:
        self._simulation = simulation

        self.list_simulations = to_raw_response_wrapper(
            simulation.list_simulations,
        )


class AsyncSimulationResourceWithRawResponse:
    def __init__(self, simulation: AsyncSimulationResource) -> None:
        self._simulation = simulation

        self.list_simulations = async_to_raw_response_wrapper(
            simulation.list_simulations,
        )


class SimulationResourceWithStreamingResponse:
    def __init__(self, simulation: SimulationResource) -> None:
        self._simulation = simulation

        self.list_simulations = to_streamed_response_wrapper(
            simulation.list_simulations,
        )


class AsyncSimulationResourceWithStreamingResponse:
    def __init__(self, simulation: AsyncSimulationResource) -> None:
        self._simulation = simulation

        self.list_simulations = async_to_streamed_response_wrapper(
            simulation.list_simulations,
        )
