# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from replicate import Replicate, AsyncReplicate
from tests.utils import assert_matches_type
from replicate.types import (
    ModelGetResponse,
    ModelListResponse,
    ModelCreateResponse,
    ModelSearchResponse,
)
from replicate.pagination import SyncCursorURLPage, AsyncCursorURLPage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestModels:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Replicate) -> None:
        model = client.models.create(
            hardware="cpu",
            name="hot-dog-detector",
            owner="alice",
            visibility="public",
        )
        assert_matches_type(ModelCreateResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Replicate) -> None:
        model = client.models.create(
            hardware="cpu",
            name="hot-dog-detector",
            owner="alice",
            visibility="public",
            cover_image_url="cover_image_url",
            description="Detect hot dogs in images",
            github_url="https://github.com/alice/hot-dog-detector",
            license_url="license_url",
            paper_url="https://arxiv.org/abs/2504.17639",
        )
        assert_matches_type(ModelCreateResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Replicate) -> None:
        response = client.models.with_raw_response.create(
            hardware="cpu",
            name="hot-dog-detector",
            owner="alice",
            visibility="public",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelCreateResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Replicate) -> None:
        with client.models.with_streaming_response.create(
            hardware="cpu",
            name="hot-dog-detector",
            owner="alice",
            visibility="public",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelCreateResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Replicate) -> None:
        model = client.models.list()
        assert_matches_type(SyncCursorURLPage[ModelListResponse], model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Replicate) -> None:
        response = client.models.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(SyncCursorURLPage[ModelListResponse], model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Replicate) -> None:
        with client.models.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(SyncCursorURLPage[ModelListResponse], model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Replicate) -> None:
        model = client.models.delete(
            model_owner="model_owner",
            model_name="model_name",
        )
        assert model is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Replicate) -> None:
        response = client.models.with_raw_response.delete(
            model_owner="model_owner",
            model_name="model_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert model is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Replicate) -> None:
        with client.models.with_streaming_response.delete(
            model_owner="model_owner",
            model_name="model_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert model is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Replicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_owner` but received ''"):
            client.models.with_raw_response.delete(
                model_owner="",
                model_name="model_name",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_name` but received ''"):
            client.models.with_raw_response.delete(
                model_owner="model_owner",
                model_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Replicate) -> None:
        model = client.models.get(
            model_owner="model_owner",
            model_name="model_name",
        )
        assert_matches_type(ModelGetResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Replicate) -> None:
        response = client.models.with_raw_response.get(
            model_owner="model_owner",
            model_name="model_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelGetResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Replicate) -> None:
        with client.models.with_streaming_response.get(
            model_owner="model_owner",
            model_name="model_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelGetResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Replicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_owner` but received ''"):
            client.models.with_raw_response.get(
                model_owner="",
                model_name="model_name",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_name` but received ''"):
            client.models.with_raw_response.get(
                model_owner="model_owner",
                model_name="",
            )

    @pytest.mark.skip(reason="Prism doesn't support query methods yet")
    @parametrize
    def test_method_search(self, client: Replicate) -> None:
        model = client.models.search(
            body="body",
        )
        assert_matches_type(SyncCursorURLPage[ModelSearchResponse], model, path=["response"])

    @pytest.mark.skip(reason="Prism doesn't support query methods yet")
    @parametrize
    def test_raw_response_search(self, client: Replicate) -> None:
        response = client.models.with_raw_response.search(
            body="body",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(SyncCursorURLPage[ModelSearchResponse], model, path=["response"])

    @pytest.mark.skip(reason="Prism doesn't support query methods yet")
    @parametrize
    def test_streaming_response_search(self, client: Replicate) -> None:
        with client.models.with_streaming_response.search(
            body="body",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(SyncCursorURLPage[ModelSearchResponse], model, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncModels:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncReplicate) -> None:
        model = await async_client.models.create(
            hardware="cpu",
            name="hot-dog-detector",
            owner="alice",
            visibility="public",
        )
        assert_matches_type(ModelCreateResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncReplicate) -> None:
        model = await async_client.models.create(
            hardware="cpu",
            name="hot-dog-detector",
            owner="alice",
            visibility="public",
            cover_image_url="cover_image_url",
            description="Detect hot dogs in images",
            github_url="https://github.com/alice/hot-dog-detector",
            license_url="license_url",
            paper_url="https://arxiv.org/abs/2504.17639",
        )
        assert_matches_type(ModelCreateResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncReplicate) -> None:
        response = await async_client.models.with_raw_response.create(
            hardware="cpu",
            name="hot-dog-detector",
            owner="alice",
            visibility="public",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelCreateResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncReplicate) -> None:
        async with async_client.models.with_streaming_response.create(
            hardware="cpu",
            name="hot-dog-detector",
            owner="alice",
            visibility="public",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelCreateResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncReplicate) -> None:
        model = await async_client.models.list()
        assert_matches_type(AsyncCursorURLPage[ModelListResponse], model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncReplicate) -> None:
        response = await async_client.models.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(AsyncCursorURLPage[ModelListResponse], model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncReplicate) -> None:
        async with async_client.models.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(AsyncCursorURLPage[ModelListResponse], model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncReplicate) -> None:
        model = await async_client.models.delete(
            model_owner="model_owner",
            model_name="model_name",
        )
        assert model is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncReplicate) -> None:
        response = await async_client.models.with_raw_response.delete(
            model_owner="model_owner",
            model_name="model_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert model is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncReplicate) -> None:
        async with async_client.models.with_streaming_response.delete(
            model_owner="model_owner",
            model_name="model_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert model is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncReplicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_owner` but received ''"):
            await async_client.models.with_raw_response.delete(
                model_owner="",
                model_name="model_name",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_name` but received ''"):
            await async_client.models.with_raw_response.delete(
                model_owner="model_owner",
                model_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncReplicate) -> None:
        model = await async_client.models.get(
            model_owner="model_owner",
            model_name="model_name",
        )
        assert_matches_type(ModelGetResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncReplicate) -> None:
        response = await async_client.models.with_raw_response.get(
            model_owner="model_owner",
            model_name="model_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelGetResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncReplicate) -> None:
        async with async_client.models.with_streaming_response.get(
            model_owner="model_owner",
            model_name="model_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelGetResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncReplicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_owner` but received ''"):
            await async_client.models.with_raw_response.get(
                model_owner="",
                model_name="model_name",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_name` but received ''"):
            await async_client.models.with_raw_response.get(
                model_owner="model_owner",
                model_name="",
            )

    @pytest.mark.skip(reason="Prism doesn't support query methods yet")
    @parametrize
    async def test_method_search(self, async_client: AsyncReplicate) -> None:
        model = await async_client.models.search(
            body="body",
        )
        assert_matches_type(AsyncCursorURLPage[ModelSearchResponse], model, path=["response"])

    @pytest.mark.skip(reason="Prism doesn't support query methods yet")
    @parametrize
    async def test_raw_response_search(self, async_client: AsyncReplicate) -> None:
        response = await async_client.models.with_raw_response.search(
            body="body",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(AsyncCursorURLPage[ModelSearchResponse], model, path=["response"])

    @pytest.mark.skip(reason="Prism doesn't support query methods yet")
    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncReplicate) -> None:
        async with async_client.models.with_streaming_response.search(
            body="body",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(AsyncCursorURLPage[ModelSearchResponse], model, path=["response"])

        assert cast(Any, response.is_closed) is True
