# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from replicate import Replicate, AsyncReplicate
from tests.utils import assert_matches_type
from replicate.types import (
    DeploymentGetResponse,
    DeploymentListResponse,
    DeploymentCreateResponse,
    DeploymentUpdateResponse,
)
from replicate.pagination import SyncCursorURLPage, AsyncCursorURLPage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDeployments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Replicate) -> None:
        deployment = client.deployments.create(
            hardware="hardware",
            max_instances=0,
            min_instances=0,
            model="model",
            name="name",
            version="version",
        )
        assert_matches_type(DeploymentCreateResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Replicate) -> None:
        response = client.deployments.with_raw_response.create(
            hardware="hardware",
            max_instances=0,
            min_instances=0,
            model="model",
            name="name",
            version="version",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(DeploymentCreateResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Replicate) -> None:
        with client.deployments.with_streaming_response.create(
            hardware="hardware",
            max_instances=0,
            min_instances=0,
            model="model",
            name="name",
            version="version",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(DeploymentCreateResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Replicate) -> None:
        deployment = client.deployments.update(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
        )
        assert_matches_type(DeploymentUpdateResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Replicate) -> None:
        deployment = client.deployments.update(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
            hardware="hardware",
            max_instances=0,
            min_instances=0,
            version="version",
        )
        assert_matches_type(DeploymentUpdateResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Replicate) -> None:
        response = client.deployments.with_raw_response.update(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(DeploymentUpdateResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Replicate) -> None:
        with client.deployments.with_streaming_response.update(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(DeploymentUpdateResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Replicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_owner` but received ''"):
            client.deployments.with_raw_response.update(
                deployment_owner="",
                deployment_name="deployment_name",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_name` but received ''"):
            client.deployments.with_raw_response.update(
                deployment_owner="deployment_owner",
                deployment_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Replicate) -> None:
        deployment = client.deployments.list()
        assert_matches_type(SyncCursorURLPage[DeploymentListResponse], deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Replicate) -> None:
        response = client.deployments.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(SyncCursorURLPage[DeploymentListResponse], deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Replicate) -> None:
        with client.deployments.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(SyncCursorURLPage[DeploymentListResponse], deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Replicate) -> None:
        deployment = client.deployments.delete(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
        )
        assert deployment is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Replicate) -> None:
        response = client.deployments.with_raw_response.delete(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert deployment is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Replicate) -> None:
        with client.deployments.with_streaming_response.delete(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert deployment is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Replicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_owner` but received ''"):
            client.deployments.with_raw_response.delete(
                deployment_owner="",
                deployment_name="deployment_name",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_name` but received ''"):
            client.deployments.with_raw_response.delete(
                deployment_owner="deployment_owner",
                deployment_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Replicate) -> None:
        deployment = client.deployments.get(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
        )
        assert_matches_type(DeploymentGetResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Replicate) -> None:
        response = client.deployments.with_raw_response.get(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(DeploymentGetResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Replicate) -> None:
        with client.deployments.with_streaming_response.get(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(DeploymentGetResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Replicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_owner` but received ''"):
            client.deployments.with_raw_response.get(
                deployment_owner="",
                deployment_name="deployment_name",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_name` but received ''"):
            client.deployments.with_raw_response.get(
                deployment_owner="deployment_owner",
                deployment_name="",
            )


class TestAsyncDeployments:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncReplicate) -> None:
        deployment = await async_client.deployments.create(
            hardware="hardware",
            max_instances=0,
            min_instances=0,
            model="model",
            name="name",
            version="version",
        )
        assert_matches_type(DeploymentCreateResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncReplicate) -> None:
        response = await async_client.deployments.with_raw_response.create(
            hardware="hardware",
            max_instances=0,
            min_instances=0,
            model="model",
            name="name",
            version="version",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(DeploymentCreateResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncReplicate) -> None:
        async with async_client.deployments.with_streaming_response.create(
            hardware="hardware",
            max_instances=0,
            min_instances=0,
            model="model",
            name="name",
            version="version",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(DeploymentCreateResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncReplicate) -> None:
        deployment = await async_client.deployments.update(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
        )
        assert_matches_type(DeploymentUpdateResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncReplicate) -> None:
        deployment = await async_client.deployments.update(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
            hardware="hardware",
            max_instances=0,
            min_instances=0,
            version="version",
        )
        assert_matches_type(DeploymentUpdateResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncReplicate) -> None:
        response = await async_client.deployments.with_raw_response.update(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(DeploymentUpdateResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncReplicate) -> None:
        async with async_client.deployments.with_streaming_response.update(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(DeploymentUpdateResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncReplicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_owner` but received ''"):
            await async_client.deployments.with_raw_response.update(
                deployment_owner="",
                deployment_name="deployment_name",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_name` but received ''"):
            await async_client.deployments.with_raw_response.update(
                deployment_owner="deployment_owner",
                deployment_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncReplicate) -> None:
        deployment = await async_client.deployments.list()
        assert_matches_type(AsyncCursorURLPage[DeploymentListResponse], deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncReplicate) -> None:
        response = await async_client.deployments.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(AsyncCursorURLPage[DeploymentListResponse], deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncReplicate) -> None:
        async with async_client.deployments.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(AsyncCursorURLPage[DeploymentListResponse], deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncReplicate) -> None:
        deployment = await async_client.deployments.delete(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
        )
        assert deployment is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncReplicate) -> None:
        response = await async_client.deployments.with_raw_response.delete(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert deployment is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncReplicate) -> None:
        async with async_client.deployments.with_streaming_response.delete(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert deployment is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncReplicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_owner` but received ''"):
            await async_client.deployments.with_raw_response.delete(
                deployment_owner="",
                deployment_name="deployment_name",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_name` but received ''"):
            await async_client.deployments.with_raw_response.delete(
                deployment_owner="deployment_owner",
                deployment_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncReplicate) -> None:
        deployment = await async_client.deployments.get(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
        )
        assert_matches_type(DeploymentGetResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncReplicate) -> None:
        response = await async_client.deployments.with_raw_response.get(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(DeploymentGetResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncReplicate) -> None:
        async with async_client.deployments.with_streaming_response.get(
            deployment_owner="deployment_owner",
            deployment_name="deployment_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(DeploymentGetResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncReplicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_owner` but received ''"):
            await async_client.deployments.with_raw_response.get(
                deployment_owner="",
                deployment_name="deployment_name",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_name` but received ''"):
            await async_client.deployments.with_raw_response.get(
                deployment_owner="deployment_owner",
                deployment_name="",
            )
