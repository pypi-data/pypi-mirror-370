# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from replicate import Replicate, AsyncReplicate
from tests.utils import assert_matches_type
from replicate.types import Prediction
from replicate._utils import parse_datetime
from replicate.pagination import SyncCursorURLPageWithCreatedFilters, AsyncCursorURLPageWithCreatedFilters

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPredictions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Replicate) -> None:
        prediction = client.predictions.create(
            input={"text": "Alice"},
            version="replicate/hello-world:9dcd6d78e7c6560c340d916fe32e9f24aabfa331e5cce95fe31f77fb03121426",
        )
        assert_matches_type(Prediction, prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Replicate) -> None:
        prediction = client.predictions.create(
            input={"text": "Alice"},
            version="replicate/hello-world:9dcd6d78e7c6560c340d916fe32e9f24aabfa331e5cce95fe31f77fb03121426",
            stream=True,
            webhook="https://example.com/my-webhook-handler",
            webhook_events_filter=["start", "completed"],
            prefer="wait=5",
        )
        assert_matches_type(Prediction, prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Replicate) -> None:
        response = client.predictions.with_raw_response.create(
            input={"text": "Alice"},
            version="replicate/hello-world:9dcd6d78e7c6560c340d916fe32e9f24aabfa331e5cce95fe31f77fb03121426",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prediction = response.parse()
        assert_matches_type(Prediction, prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Replicate) -> None:
        with client.predictions.with_streaming_response.create(
            input={"text": "Alice"},
            version="replicate/hello-world:9dcd6d78e7c6560c340d916fe32e9f24aabfa331e5cce95fe31f77fb03121426",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prediction = response.parse()
            assert_matches_type(Prediction, prediction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Replicate) -> None:
        prediction = client.predictions.list()
        assert_matches_type(SyncCursorURLPageWithCreatedFilters[Prediction], prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Replicate) -> None:
        prediction = client.predictions.list(
            created_after=parse_datetime("2025-01-01T00:00:00Z"),
            created_before=parse_datetime("2025-02-01T00:00:00Z"),
        )
        assert_matches_type(SyncCursorURLPageWithCreatedFilters[Prediction], prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Replicate) -> None:
        response = client.predictions.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prediction = response.parse()
        assert_matches_type(SyncCursorURLPageWithCreatedFilters[Prediction], prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Replicate) -> None:
        with client.predictions.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prediction = response.parse()
            assert_matches_type(SyncCursorURLPageWithCreatedFilters[Prediction], prediction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cancel(self, client: Replicate) -> None:
        prediction = client.predictions.cancel(
            prediction_id="prediction_id",
        )
        assert_matches_type(Prediction, prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_cancel(self, client: Replicate) -> None:
        response = client.predictions.with_raw_response.cancel(
            prediction_id="prediction_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prediction = response.parse()
        assert_matches_type(Prediction, prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_cancel(self, client: Replicate) -> None:
        with client.predictions.with_streaming_response.cancel(
            prediction_id="prediction_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prediction = response.parse()
            assert_matches_type(Prediction, prediction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_cancel(self, client: Replicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `prediction_id` but received ''"):
            client.predictions.with_raw_response.cancel(
                prediction_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Replicate) -> None:
        prediction = client.predictions.get(
            prediction_id="prediction_id",
        )
        assert_matches_type(Prediction, prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Replicate) -> None:
        response = client.predictions.with_raw_response.get(
            prediction_id="prediction_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prediction = response.parse()
        assert_matches_type(Prediction, prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Replicate) -> None:
        with client.predictions.with_streaming_response.get(
            prediction_id="prediction_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prediction = response.parse()
            assert_matches_type(Prediction, prediction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Replicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `prediction_id` but received ''"):
            client.predictions.with_raw_response.get(
                prediction_id="",
            )


class TestAsyncPredictions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncReplicate) -> None:
        prediction = await async_client.predictions.create(
            input={"text": "Alice"},
            version="replicate/hello-world:9dcd6d78e7c6560c340d916fe32e9f24aabfa331e5cce95fe31f77fb03121426",
        )
        assert_matches_type(Prediction, prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncReplicate) -> None:
        prediction = await async_client.predictions.create(
            input={"text": "Alice"},
            version="replicate/hello-world:9dcd6d78e7c6560c340d916fe32e9f24aabfa331e5cce95fe31f77fb03121426",
            stream=True,
            webhook="https://example.com/my-webhook-handler",
            webhook_events_filter=["start", "completed"],
            prefer="wait=5",
        )
        assert_matches_type(Prediction, prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncReplicate) -> None:
        response = await async_client.predictions.with_raw_response.create(
            input={"text": "Alice"},
            version="replicate/hello-world:9dcd6d78e7c6560c340d916fe32e9f24aabfa331e5cce95fe31f77fb03121426",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prediction = await response.parse()
        assert_matches_type(Prediction, prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncReplicate) -> None:
        async with async_client.predictions.with_streaming_response.create(
            input={"text": "Alice"},
            version="replicate/hello-world:9dcd6d78e7c6560c340d916fe32e9f24aabfa331e5cce95fe31f77fb03121426",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prediction = await response.parse()
            assert_matches_type(Prediction, prediction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncReplicate) -> None:
        prediction = await async_client.predictions.list()
        assert_matches_type(AsyncCursorURLPageWithCreatedFilters[Prediction], prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncReplicate) -> None:
        prediction = await async_client.predictions.list(
            created_after=parse_datetime("2025-01-01T00:00:00Z"),
            created_before=parse_datetime("2025-02-01T00:00:00Z"),
        )
        assert_matches_type(AsyncCursorURLPageWithCreatedFilters[Prediction], prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncReplicate) -> None:
        response = await async_client.predictions.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prediction = await response.parse()
        assert_matches_type(AsyncCursorURLPageWithCreatedFilters[Prediction], prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncReplicate) -> None:
        async with async_client.predictions.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prediction = await response.parse()
            assert_matches_type(AsyncCursorURLPageWithCreatedFilters[Prediction], prediction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cancel(self, async_client: AsyncReplicate) -> None:
        prediction = await async_client.predictions.cancel(
            prediction_id="prediction_id",
        )
        assert_matches_type(Prediction, prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncReplicate) -> None:
        response = await async_client.predictions.with_raw_response.cancel(
            prediction_id="prediction_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prediction = await response.parse()
        assert_matches_type(Prediction, prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncReplicate) -> None:
        async with async_client.predictions.with_streaming_response.cancel(
            prediction_id="prediction_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prediction = await response.parse()
            assert_matches_type(Prediction, prediction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncReplicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `prediction_id` but received ''"):
            await async_client.predictions.with_raw_response.cancel(
                prediction_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncReplicate) -> None:
        prediction = await async_client.predictions.get(
            prediction_id="prediction_id",
        )
        assert_matches_type(Prediction, prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncReplicate) -> None:
        response = await async_client.predictions.with_raw_response.get(
            prediction_id="prediction_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prediction = await response.parse()
        assert_matches_type(Prediction, prediction, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncReplicate) -> None:
        async with async_client.predictions.with_streaming_response.get(
            prediction_id="prediction_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prediction = await response.parse()
            assert_matches_type(Prediction, prediction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncReplicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `prediction_id` but received ''"):
            await async_client.predictions.with_raw_response.get(
                prediction_id="",
            )
