# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fluidize_sdk import FluidizeSDK, AsyncFluidizeSDK
from fluidize_sdk.types.auth import SSHConnectResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSSH:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_connect(self, client: FluidizeSDK) -> None:
        ssh = client.auth.ssh.connect(
            password="password",
            username="username",
            verification_code="verification_code",
        )
        assert_matches_type(SSHConnectResponse, ssh, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_connect_with_all_params(self, client: FluidizeSDK) -> None:
        ssh = client.auth.ssh.connect(
            password="password",
            username="username",
            verification_code="verification_code",
            host="host",
            port=0,
        )
        assert_matches_type(SSHConnectResponse, ssh, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_connect(self, client: FluidizeSDK) -> None:
        response = client.auth.ssh.with_raw_response.connect(
            password="password",
            username="username",
            verification_code="verification_code",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ssh = response.parse()
        assert_matches_type(SSHConnectResponse, ssh, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_connect(self, client: FluidizeSDK) -> None:
        with client.auth.ssh.with_streaming_response.connect(
            password="password",
            username="username",
            verification_code="verification_code",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ssh = response.parse()
            assert_matches_type(SSHConnectResponse, ssh, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_disconnect(self, client: FluidizeSDK) -> None:
        ssh = client.auth.ssh.disconnect()
        assert_matches_type(object, ssh, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_disconnect(self, client: FluidizeSDK) -> None:
        response = client.auth.ssh.with_raw_response.disconnect()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ssh = response.parse()
        assert_matches_type(object, ssh, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_disconnect(self, client: FluidizeSDK) -> None:
        with client.auth.ssh.with_streaming_response.disconnect() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ssh = response.parse()
            assert_matches_type(object, ssh, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_status(self, client: FluidizeSDK) -> None:
        ssh = client.auth.ssh.status()
        assert_matches_type(object, ssh, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_status(self, client: FluidizeSDK) -> None:
        response = client.auth.ssh.with_raw_response.status()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ssh = response.parse()
        assert_matches_type(object, ssh, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_status(self, client: FluidizeSDK) -> None:
        with client.auth.ssh.with_streaming_response.status() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ssh = response.parse()
            assert_matches_type(object, ssh, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSSH:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_connect(self, async_client: AsyncFluidizeSDK) -> None:
        ssh = await async_client.auth.ssh.connect(
            password="password",
            username="username",
            verification_code="verification_code",
        )
        assert_matches_type(SSHConnectResponse, ssh, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_connect_with_all_params(self, async_client: AsyncFluidizeSDK) -> None:
        ssh = await async_client.auth.ssh.connect(
            password="password",
            username="username",
            verification_code="verification_code",
            host="host",
            port=0,
        )
        assert_matches_type(SSHConnectResponse, ssh, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_connect(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.auth.ssh.with_raw_response.connect(
            password="password",
            username="username",
            verification_code="verification_code",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ssh = await response.parse()
        assert_matches_type(SSHConnectResponse, ssh, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_connect(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.auth.ssh.with_streaming_response.connect(
            password="password",
            username="username",
            verification_code="verification_code",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ssh = await response.parse()
            assert_matches_type(SSHConnectResponse, ssh, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_disconnect(self, async_client: AsyncFluidizeSDK) -> None:
        ssh = await async_client.auth.ssh.disconnect()
        assert_matches_type(object, ssh, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_disconnect(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.auth.ssh.with_raw_response.disconnect()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ssh = await response.parse()
        assert_matches_type(object, ssh, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_disconnect(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.auth.ssh.with_streaming_response.disconnect() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ssh = await response.parse()
            assert_matches_type(object, ssh, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_status(self, async_client: AsyncFluidizeSDK) -> None:
        ssh = await async_client.auth.ssh.status()
        assert_matches_type(object, ssh, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_status(self, async_client: AsyncFluidizeSDK) -> None:
        response = await async_client.auth.ssh.with_raw_response.status()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ssh = await response.parse()
        assert_matches_type(object, ssh, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_status(self, async_client: AsyncFluidizeSDK) -> None:
        async with async_client.auth.ssh.with_streaming_response.status() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ssh = await response.parse()
            assert_matches_type(object, ssh, path=["response"])

        assert cast(Any, response.is_closed) is True
