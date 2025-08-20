# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from replicate import Replicate, AsyncReplicate
from tests.utils import assert_matches_type
from replicate.types import Prediction
from replicate.pagination import SyncCursorURLPage, AsyncCursorURLPage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestExamples:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Replicate) -> None:
        example = client.models.examples.list(
            model_owner="model_owner",
            model_name="model_name",
        )
        assert_matches_type(SyncCursorURLPage[Prediction], example, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Replicate) -> None:
        response = client.models.examples.with_raw_response.list(
            model_owner="model_owner",
            model_name="model_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        example = response.parse()
        assert_matches_type(SyncCursorURLPage[Prediction], example, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Replicate) -> None:
        with client.models.examples.with_streaming_response.list(
            model_owner="model_owner",
            model_name="model_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            example = response.parse()
            assert_matches_type(SyncCursorURLPage[Prediction], example, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Replicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_owner` but received ''"):
            client.models.examples.with_raw_response.list(
                model_owner="",
                model_name="model_name",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_name` but received ''"):
            client.models.examples.with_raw_response.list(
                model_owner="model_owner",
                model_name="",
            )


class TestAsyncExamples:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncReplicate) -> None:
        example = await async_client.models.examples.list(
            model_owner="model_owner",
            model_name="model_name",
        )
        assert_matches_type(AsyncCursorURLPage[Prediction], example, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncReplicate) -> None:
        response = await async_client.models.examples.with_raw_response.list(
            model_owner="model_owner",
            model_name="model_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        example = await response.parse()
        assert_matches_type(AsyncCursorURLPage[Prediction], example, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncReplicate) -> None:
        async with async_client.models.examples.with_streaming_response.list(
            model_owner="model_owner",
            model_name="model_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            example = await response.parse()
            assert_matches_type(AsyncCursorURLPage[Prediction], example, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncReplicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_owner` but received ''"):
            await async_client.models.examples.with_raw_response.list(
                model_owner="",
                model_name="model_name",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_name` but received ''"):
            await async_client.models.examples.with_raw_response.list(
                model_owner="model_owner",
                model_name="",
            )
