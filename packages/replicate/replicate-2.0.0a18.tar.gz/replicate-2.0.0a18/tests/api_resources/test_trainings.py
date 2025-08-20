# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from replicate import Replicate, AsyncReplicate
from tests.utils import assert_matches_type
from replicate.types import (
    TrainingGetResponse,
    TrainingListResponse,
    TrainingCancelResponse,
    TrainingCreateResponse,
)
from replicate.pagination import SyncCursorURLPage, AsyncCursorURLPage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTrainings:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Replicate) -> None:
        training = client.trainings.create(
            model_owner="model_owner",
            model_name="model_name",
            version_id="version_id",
            destination="destination",
            input={},
        )
        assert_matches_type(TrainingCreateResponse, training, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Replicate) -> None:
        training = client.trainings.create(
            model_owner="model_owner",
            model_name="model_name",
            version_id="version_id",
            destination="destination",
            input={},
            webhook="webhook",
            webhook_events_filter=["start"],
        )
        assert_matches_type(TrainingCreateResponse, training, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Replicate) -> None:
        response = client.trainings.with_raw_response.create(
            model_owner="model_owner",
            model_name="model_name",
            version_id="version_id",
            destination="destination",
            input={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training = response.parse()
        assert_matches_type(TrainingCreateResponse, training, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Replicate) -> None:
        with client.trainings.with_streaming_response.create(
            model_owner="model_owner",
            model_name="model_name",
            version_id="version_id",
            destination="destination",
            input={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training = response.parse()
            assert_matches_type(TrainingCreateResponse, training, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Replicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_owner` but received ''"):
            client.trainings.with_raw_response.create(
                model_owner="",
                model_name="model_name",
                version_id="version_id",
                destination="destination",
                input={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_name` but received ''"):
            client.trainings.with_raw_response.create(
                model_owner="model_owner",
                model_name="",
                version_id="version_id",
                destination="destination",
                input={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            client.trainings.with_raw_response.create(
                model_owner="model_owner",
                model_name="model_name",
                version_id="",
                destination="destination",
                input={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Replicate) -> None:
        training = client.trainings.list()
        assert_matches_type(SyncCursorURLPage[TrainingListResponse], training, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Replicate) -> None:
        response = client.trainings.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training = response.parse()
        assert_matches_type(SyncCursorURLPage[TrainingListResponse], training, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Replicate) -> None:
        with client.trainings.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training = response.parse()
            assert_matches_type(SyncCursorURLPage[TrainingListResponse], training, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cancel(self, client: Replicate) -> None:
        training = client.trainings.cancel(
            training_id="training_id",
        )
        assert_matches_type(TrainingCancelResponse, training, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_cancel(self, client: Replicate) -> None:
        response = client.trainings.with_raw_response.cancel(
            training_id="training_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training = response.parse()
        assert_matches_type(TrainingCancelResponse, training, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_cancel(self, client: Replicate) -> None:
        with client.trainings.with_streaming_response.cancel(
            training_id="training_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training = response.parse()
            assert_matches_type(TrainingCancelResponse, training, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_cancel(self, client: Replicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `training_id` but received ''"):
            client.trainings.with_raw_response.cancel(
                training_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Replicate) -> None:
        training = client.trainings.get(
            training_id="training_id",
        )
        assert_matches_type(TrainingGetResponse, training, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Replicate) -> None:
        response = client.trainings.with_raw_response.get(
            training_id="training_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training = response.parse()
        assert_matches_type(TrainingGetResponse, training, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Replicate) -> None:
        with client.trainings.with_streaming_response.get(
            training_id="training_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training = response.parse()
            assert_matches_type(TrainingGetResponse, training, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Replicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `training_id` but received ''"):
            client.trainings.with_raw_response.get(
                training_id="",
            )


class TestAsyncTrainings:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncReplicate) -> None:
        training = await async_client.trainings.create(
            model_owner="model_owner",
            model_name="model_name",
            version_id="version_id",
            destination="destination",
            input={},
        )
        assert_matches_type(TrainingCreateResponse, training, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncReplicate) -> None:
        training = await async_client.trainings.create(
            model_owner="model_owner",
            model_name="model_name",
            version_id="version_id",
            destination="destination",
            input={},
            webhook="webhook",
            webhook_events_filter=["start"],
        )
        assert_matches_type(TrainingCreateResponse, training, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncReplicate) -> None:
        response = await async_client.trainings.with_raw_response.create(
            model_owner="model_owner",
            model_name="model_name",
            version_id="version_id",
            destination="destination",
            input={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training = await response.parse()
        assert_matches_type(TrainingCreateResponse, training, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncReplicate) -> None:
        async with async_client.trainings.with_streaming_response.create(
            model_owner="model_owner",
            model_name="model_name",
            version_id="version_id",
            destination="destination",
            input={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training = await response.parse()
            assert_matches_type(TrainingCreateResponse, training, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncReplicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_owner` but received ''"):
            await async_client.trainings.with_raw_response.create(
                model_owner="",
                model_name="model_name",
                version_id="version_id",
                destination="destination",
                input={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_name` but received ''"):
            await async_client.trainings.with_raw_response.create(
                model_owner="model_owner",
                model_name="",
                version_id="version_id",
                destination="destination",
                input={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            await async_client.trainings.with_raw_response.create(
                model_owner="model_owner",
                model_name="model_name",
                version_id="",
                destination="destination",
                input={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncReplicate) -> None:
        training = await async_client.trainings.list()
        assert_matches_type(AsyncCursorURLPage[TrainingListResponse], training, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncReplicate) -> None:
        response = await async_client.trainings.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training = await response.parse()
        assert_matches_type(AsyncCursorURLPage[TrainingListResponse], training, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncReplicate) -> None:
        async with async_client.trainings.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training = await response.parse()
            assert_matches_type(AsyncCursorURLPage[TrainingListResponse], training, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cancel(self, async_client: AsyncReplicate) -> None:
        training = await async_client.trainings.cancel(
            training_id="training_id",
        )
        assert_matches_type(TrainingCancelResponse, training, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncReplicate) -> None:
        response = await async_client.trainings.with_raw_response.cancel(
            training_id="training_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training = await response.parse()
        assert_matches_type(TrainingCancelResponse, training, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncReplicate) -> None:
        async with async_client.trainings.with_streaming_response.cancel(
            training_id="training_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training = await response.parse()
            assert_matches_type(TrainingCancelResponse, training, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncReplicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `training_id` but received ''"):
            await async_client.trainings.with_raw_response.cancel(
                training_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncReplicate) -> None:
        training = await async_client.trainings.get(
            training_id="training_id",
        )
        assert_matches_type(TrainingGetResponse, training, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncReplicate) -> None:
        response = await async_client.trainings.with_raw_response.get(
            training_id="training_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training = await response.parse()
        assert_matches_type(TrainingGetResponse, training, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncReplicate) -> None:
        async with async_client.trainings.with_streaming_response.get(
            training_id="training_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training = await response.parse()
            assert_matches_type(TrainingGetResponse, training, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncReplicate) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `training_id` but received ''"):
            await async_client.trainings.with_raw_response.get(
                training_id="",
            )
