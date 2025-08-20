# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from ..types import training_create_params
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
from ..pagination import SyncCursorURLPage, AsyncCursorURLPage
from .._base_client import AsyncPaginator, make_request_options
from ..types.training_get_response import TrainingGetResponse
from ..types.training_list_response import TrainingListResponse
from ..types.training_cancel_response import TrainingCancelResponse
from ..types.training_create_response import TrainingCreateResponse

__all__ = ["TrainingsResource", "AsyncTrainingsResource"]


class TrainingsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TrainingsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return TrainingsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TrainingsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return TrainingsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        model_owner: str,
        model_name: str,
        version_id: str,
        destination: str,
        input: object,
        webhook: str | NotGiven = NOT_GIVEN,
        webhook_events_filter: List[Literal["start", "output", "logs", "completed"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TrainingCreateResponse:
        """
        Start a new training of the model version you specify.

        Example request body:

        ```json
        {
          "destination": "{new_owner}/{new_name}",
          "input": {
            "train_data": "https://example.com/my-input-images.zip"
          },
          "webhook": "https://example.com/my-webhook"
        }
        ```

        Example cURL request:

        ```console
        curl -s -X POST \\
          -d '{"destination": "{new_owner}/{new_name}", "input": {"input_images": "https://example.com/my-input-images.zip"}}' \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          -H 'Content-Type: application/json' \\
          https://api.replicate.com/v1/models/stability-ai/sdxl/versions/da77bc59ee60423279fd632efb4795ab731d9e3ca9705ef3341091fb989b7eaf/trainings
        ```

        The response will be the training object:

        ```json
        {
          "id": "zz4ibbonubfz7carwiefibzgga",
          "model": "stability-ai/sdxl",
          "version": "da77bc59ee60423279fd632efb4795ab731d9e3ca9705ef3341091fb989b7eaf",
          "input": {
            "input_images": "https://example.com/my-input-images.zip"
          },
          "logs": "",
          "error": null,
          "status": "starting",
          "created_at": "2023-09-08T16:32:56.990893084Z",
          "urls": {
            "web": "https://replicate.com/p/zz4ibbonubfz7carwiefibzgga",
            "get": "https://api.replicate.com/v1/predictions/zz4ibbonubfz7carwiefibzgga",
            "cancel": "https://api.replicate.com/v1/predictions/zz4ibbonubfz7carwiefibzgga/cancel"
          }
        }
        ```

        As models can take several minutes or more to train, the result will not be
        available immediately. To get the final result of the training you should either
        provide a `webhook` HTTPS URL for us to call when the results are ready, or poll
        the [get a training](#trainings.get) endpoint until it has finished.

        When a training completes, it creates a new
        [version](https://replicate.com/docs/how-does-replicate-work#terminology) of the
        model at the specified destination.

        To find some models to train on, check out the
        [trainable language models collection](https://replicate.com/collections/trainable-language-models).

        Args:
          destination: A string representing the desired model to push to in the format
              `{destination_model_owner}/{destination_model_name}`. This should be an existing
              model owned by the user or organization making the API request. If the
              destination is invalid, the server will return an appropriate 4XX response.

          input: An object containing inputs to the Cog model's `train()` function.

          webhook: An HTTPS URL for receiving a webhook when the training completes. The webhook
              will be a POST request where the request body is the same as the response body
              of the [get training](#trainings.get) operation. If there are network problems,
              we will retry the webhook a few times, so make sure it can be safely called more
              than once. Replicate will not follow redirects when sending webhook requests to
              your service, so be sure to specify a URL that will resolve without redirecting.

          webhook_events_filter: By default, we will send requests to your webhook URL whenever there are new
              outputs or the training has finished. You can change which events trigger
              webhook requests by specifying `webhook_events_filter` in the training request:

              - `start`: immediately on training start
              - `output`: each time a training generates an output (note that trainings can
                generate multiple outputs)
              - `logs`: each time log output is generated by a training
              - `completed`: when the training reaches a terminal state
                (succeeded/canceled/failed)

              For example, if you only wanted requests to be sent at the start and end of the
              training, you would provide:

              ```json
              {
                "destination": "my-organization/my-model",
                "input": {
                  "text": "Alice"
                },
                "webhook": "https://example.com/my-webhook",
                "webhook_events_filter": ["start", "completed"]
              }
              ```

              Requests for event types `output` and `logs` will be sent at most once every
              500ms. If you request `start` and `completed` webhooks, then they'll always be
              sent regardless of throttling.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_owner:
            raise ValueError(f"Expected a non-empty value for `model_owner` but received {model_owner!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        return self._post(
            f"/models/{model_owner}/{model_name}/versions/{version_id}/trainings",
            body=maybe_transform(
                {
                    "destination": destination,
                    "input": input,
                    "webhook": webhook,
                    "webhook_events_filter": webhook_events_filter,
                },
                training_create_params.TrainingCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TrainingCreateResponse,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncCursorURLPage[TrainingListResponse]:
        """
        Get a paginated list of all trainings created by the user or organization
        associated with the provided API token.

        This will include trainings created from the API and the website. It will return
        100 records per page.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/trainings
        ```

        The response will be a paginated JSON array of training objects, sorted with the
        most recent training first:

        ```json
        {
          "next": null,
          "previous": null,
          "results": [
            {
              "completed_at": "2023-09-08T16:41:19.826523Z",
              "created_at": "2023-09-08T16:32:57.018467Z",
              "error": null,
              "id": "zz4ibbonubfz7carwiefibzgga",
              "input": {
                "input_images": "https://example.com/my-input-images.zip"
              },
              "metrics": {
                "predict_time": 502.713876
              },
              "output": {
                "version": "...",
                "weights": "..."
              },
              "started_at": "2023-09-08T16:32:57.112647Z",
              "source": "api",
              "status": "succeeded",
              "urls": {
                "web": "https://replicate.com/p/zz4ibbonubfz7carwiefibzgga",
                "get": "https://api.replicate.com/v1/trainings/zz4ibbonubfz7carwiefibzgga",
                "cancel": "https://api.replicate.com/v1/trainings/zz4ibbonubfz7carwiefibzgga/cancel"
              },
              "model": "stability-ai/sdxl",
              "version": "da77bc59ee60423279fd632efb4795ab731d9e3ca9705ef3341091fb989b7eaf"
            }
          ]
        }
        ```

        `id` will be the unique ID of the training.

        `source` will indicate how the training was created. Possible values are `web`
        or `api`.

        `status` will be the status of the training. Refer to
        [get a single training](#trainings.get) for possible values.

        `urls` will be a convenience object that can be used to construct new API
        requests for the given training.

        `version` will be the unique ID of model version used to create the training.
        """
        return self._get_api_list(
            "/trainings",
            page=SyncCursorURLPage[TrainingListResponse],
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            model=TrainingListResponse,
        )

    def cancel(
        self,
        *,
        training_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TrainingCancelResponse:
        """
        Cancel a training

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not training_id:
            raise ValueError(f"Expected a non-empty value for `training_id` but received {training_id!r}")
        return self._post(
            f"/trainings/{training_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TrainingCancelResponse,
        )

    def get(
        self,
        *,
        training_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TrainingGetResponse:
        """
        Get the current state of a training.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/trainings/zz4ibbonubfz7carwiefibzgga
        ```

        The response will be the training object:

        ```json
        {
          "completed_at": "2023-09-08T16:41:19.826523Z",
          "created_at": "2023-09-08T16:32:57.018467Z",
          "error": null,
          "id": "zz4ibbonubfz7carwiefibzgga",
          "input": {
            "input_images": "https://example.com/my-input-images.zip"
          },
          "logs": "...",
          "metrics": {
            "predict_time": 502.713876
          },
          "output": {
            "version": "...",
            "weights": "..."
          },
          "started_at": "2023-09-08T16:32:57.112647Z",
          "status": "succeeded",
          "urls": {
            "web": "https://replicate.com/p/zz4ibbonubfz7carwiefibzgga",
            "get": "https://api.replicate.com/v1/trainings/zz4ibbonubfz7carwiefibzgga",
            "cancel": "https://api.replicate.com/v1/trainings/zz4ibbonubfz7carwiefibzgga/cancel"
          },
          "model": "stability-ai/sdxl",
          "version": "da77bc59ee60423279fd632efb4795ab731d9e3ca9705ef3341091fb989b7eaf"
        }
        ```

        `status` will be one of:

        - `starting`: the training is starting up. If this status lasts longer than a
          few seconds, then it's typically because a new worker is being started to run
          the training.
        - `processing`: the `train()` method of the model is currently running.
        - `succeeded`: the training completed successfully.
        - `failed`: the training encountered an error during processing.
        - `canceled`: the training was canceled by its creator.

        In the case of success, `output` will be an object containing the output of the
        model. Any files will be represented as HTTPS URLs. You'll need to pass the
        `Authorization` header to request them.

        In the case of failure, `error` will contain the error encountered during the
        training.

        Terminated trainings (with a status of `succeeded`, `failed`, or `canceled`)
        will include a `metrics` object with a `predict_time` property showing the
        amount of CPU or GPU time, in seconds, that the training used while running. It
        won't include time waiting for the training to start.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not training_id:
            raise ValueError(f"Expected a non-empty value for `training_id` but received {training_id!r}")
        return self._get(
            f"/trainings/{training_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TrainingGetResponse,
        )


class AsyncTrainingsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTrainingsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return AsyncTrainingsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTrainingsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return AsyncTrainingsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        model_owner: str,
        model_name: str,
        version_id: str,
        destination: str,
        input: object,
        webhook: str | NotGiven = NOT_GIVEN,
        webhook_events_filter: List[Literal["start", "output", "logs", "completed"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TrainingCreateResponse:
        """
        Start a new training of the model version you specify.

        Example request body:

        ```json
        {
          "destination": "{new_owner}/{new_name}",
          "input": {
            "train_data": "https://example.com/my-input-images.zip"
          },
          "webhook": "https://example.com/my-webhook"
        }
        ```

        Example cURL request:

        ```console
        curl -s -X POST \\
          -d '{"destination": "{new_owner}/{new_name}", "input": {"input_images": "https://example.com/my-input-images.zip"}}' \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          -H 'Content-Type: application/json' \\
          https://api.replicate.com/v1/models/stability-ai/sdxl/versions/da77bc59ee60423279fd632efb4795ab731d9e3ca9705ef3341091fb989b7eaf/trainings
        ```

        The response will be the training object:

        ```json
        {
          "id": "zz4ibbonubfz7carwiefibzgga",
          "model": "stability-ai/sdxl",
          "version": "da77bc59ee60423279fd632efb4795ab731d9e3ca9705ef3341091fb989b7eaf",
          "input": {
            "input_images": "https://example.com/my-input-images.zip"
          },
          "logs": "",
          "error": null,
          "status": "starting",
          "created_at": "2023-09-08T16:32:56.990893084Z",
          "urls": {
            "web": "https://replicate.com/p/zz4ibbonubfz7carwiefibzgga",
            "get": "https://api.replicate.com/v1/predictions/zz4ibbonubfz7carwiefibzgga",
            "cancel": "https://api.replicate.com/v1/predictions/zz4ibbonubfz7carwiefibzgga/cancel"
          }
        }
        ```

        As models can take several minutes or more to train, the result will not be
        available immediately. To get the final result of the training you should either
        provide a `webhook` HTTPS URL for us to call when the results are ready, or poll
        the [get a training](#trainings.get) endpoint until it has finished.

        When a training completes, it creates a new
        [version](https://replicate.com/docs/how-does-replicate-work#terminology) of the
        model at the specified destination.

        To find some models to train on, check out the
        [trainable language models collection](https://replicate.com/collections/trainable-language-models).

        Args:
          destination: A string representing the desired model to push to in the format
              `{destination_model_owner}/{destination_model_name}`. This should be an existing
              model owned by the user or organization making the API request. If the
              destination is invalid, the server will return an appropriate 4XX response.

          input: An object containing inputs to the Cog model's `train()` function.

          webhook: An HTTPS URL for receiving a webhook when the training completes. The webhook
              will be a POST request where the request body is the same as the response body
              of the [get training](#trainings.get) operation. If there are network problems,
              we will retry the webhook a few times, so make sure it can be safely called more
              than once. Replicate will not follow redirects when sending webhook requests to
              your service, so be sure to specify a URL that will resolve without redirecting.

          webhook_events_filter: By default, we will send requests to your webhook URL whenever there are new
              outputs or the training has finished. You can change which events trigger
              webhook requests by specifying `webhook_events_filter` in the training request:

              - `start`: immediately on training start
              - `output`: each time a training generates an output (note that trainings can
                generate multiple outputs)
              - `logs`: each time log output is generated by a training
              - `completed`: when the training reaches a terminal state
                (succeeded/canceled/failed)

              For example, if you only wanted requests to be sent at the start and end of the
              training, you would provide:

              ```json
              {
                "destination": "my-organization/my-model",
                "input": {
                  "text": "Alice"
                },
                "webhook": "https://example.com/my-webhook",
                "webhook_events_filter": ["start", "completed"]
              }
              ```

              Requests for event types `output` and `logs` will be sent at most once every
              500ms. If you request `start` and `completed` webhooks, then they'll always be
              sent regardless of throttling.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_owner:
            raise ValueError(f"Expected a non-empty value for `model_owner` but received {model_owner!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        return await self._post(
            f"/models/{model_owner}/{model_name}/versions/{version_id}/trainings",
            body=await async_maybe_transform(
                {
                    "destination": destination,
                    "input": input,
                    "webhook": webhook,
                    "webhook_events_filter": webhook_events_filter,
                },
                training_create_params.TrainingCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TrainingCreateResponse,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[TrainingListResponse, AsyncCursorURLPage[TrainingListResponse]]:
        """
        Get a paginated list of all trainings created by the user or organization
        associated with the provided API token.

        This will include trainings created from the API and the website. It will return
        100 records per page.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/trainings
        ```

        The response will be a paginated JSON array of training objects, sorted with the
        most recent training first:

        ```json
        {
          "next": null,
          "previous": null,
          "results": [
            {
              "completed_at": "2023-09-08T16:41:19.826523Z",
              "created_at": "2023-09-08T16:32:57.018467Z",
              "error": null,
              "id": "zz4ibbonubfz7carwiefibzgga",
              "input": {
                "input_images": "https://example.com/my-input-images.zip"
              },
              "metrics": {
                "predict_time": 502.713876
              },
              "output": {
                "version": "...",
                "weights": "..."
              },
              "started_at": "2023-09-08T16:32:57.112647Z",
              "source": "api",
              "status": "succeeded",
              "urls": {
                "web": "https://replicate.com/p/zz4ibbonubfz7carwiefibzgga",
                "get": "https://api.replicate.com/v1/trainings/zz4ibbonubfz7carwiefibzgga",
                "cancel": "https://api.replicate.com/v1/trainings/zz4ibbonubfz7carwiefibzgga/cancel"
              },
              "model": "stability-ai/sdxl",
              "version": "da77bc59ee60423279fd632efb4795ab731d9e3ca9705ef3341091fb989b7eaf"
            }
          ]
        }
        ```

        `id` will be the unique ID of the training.

        `source` will indicate how the training was created. Possible values are `web`
        or `api`.

        `status` will be the status of the training. Refer to
        [get a single training](#trainings.get) for possible values.

        `urls` will be a convenience object that can be used to construct new API
        requests for the given training.

        `version` will be the unique ID of model version used to create the training.
        """
        return self._get_api_list(
            "/trainings",
            page=AsyncCursorURLPage[TrainingListResponse],
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            model=TrainingListResponse,
        )

    async def cancel(
        self,
        *,
        training_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TrainingCancelResponse:
        """
        Cancel a training

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not training_id:
            raise ValueError(f"Expected a non-empty value for `training_id` but received {training_id!r}")
        return await self._post(
            f"/trainings/{training_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TrainingCancelResponse,
        )

    async def get(
        self,
        *,
        training_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TrainingGetResponse:
        """
        Get the current state of a training.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/trainings/zz4ibbonubfz7carwiefibzgga
        ```

        The response will be the training object:

        ```json
        {
          "completed_at": "2023-09-08T16:41:19.826523Z",
          "created_at": "2023-09-08T16:32:57.018467Z",
          "error": null,
          "id": "zz4ibbonubfz7carwiefibzgga",
          "input": {
            "input_images": "https://example.com/my-input-images.zip"
          },
          "logs": "...",
          "metrics": {
            "predict_time": 502.713876
          },
          "output": {
            "version": "...",
            "weights": "..."
          },
          "started_at": "2023-09-08T16:32:57.112647Z",
          "status": "succeeded",
          "urls": {
            "web": "https://replicate.com/p/zz4ibbonubfz7carwiefibzgga",
            "get": "https://api.replicate.com/v1/trainings/zz4ibbonubfz7carwiefibzgga",
            "cancel": "https://api.replicate.com/v1/trainings/zz4ibbonubfz7carwiefibzgga/cancel"
          },
          "model": "stability-ai/sdxl",
          "version": "da77bc59ee60423279fd632efb4795ab731d9e3ca9705ef3341091fb989b7eaf"
        }
        ```

        `status` will be one of:

        - `starting`: the training is starting up. If this status lasts longer than a
          few seconds, then it's typically because a new worker is being started to run
          the training.
        - `processing`: the `train()` method of the model is currently running.
        - `succeeded`: the training completed successfully.
        - `failed`: the training encountered an error during processing.
        - `canceled`: the training was canceled by its creator.

        In the case of success, `output` will be an object containing the output of the
        model. Any files will be represented as HTTPS URLs. You'll need to pass the
        `Authorization` header to request them.

        In the case of failure, `error` will contain the error encountered during the
        training.

        Terminated trainings (with a status of `succeeded`, `failed`, or `canceled`)
        will include a `metrics` object with a `predict_time` property showing the
        amount of CPU or GPU time, in seconds, that the training used while running. It
        won't include time waiting for the training to start.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not training_id:
            raise ValueError(f"Expected a non-empty value for `training_id` but received {training_id!r}")
        return await self._get(
            f"/trainings/{training_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TrainingGetResponse,
        )


class TrainingsResourceWithRawResponse:
    def __init__(self, trainings: TrainingsResource) -> None:
        self._trainings = trainings

        self.create = to_raw_response_wrapper(
            trainings.create,
        )
        self.list = to_raw_response_wrapper(
            trainings.list,
        )
        self.cancel = to_raw_response_wrapper(
            trainings.cancel,
        )
        self.get = to_raw_response_wrapper(
            trainings.get,
        )


class AsyncTrainingsResourceWithRawResponse:
    def __init__(self, trainings: AsyncTrainingsResource) -> None:
        self._trainings = trainings

        self.create = async_to_raw_response_wrapper(
            trainings.create,
        )
        self.list = async_to_raw_response_wrapper(
            trainings.list,
        )
        self.cancel = async_to_raw_response_wrapper(
            trainings.cancel,
        )
        self.get = async_to_raw_response_wrapper(
            trainings.get,
        )


class TrainingsResourceWithStreamingResponse:
    def __init__(self, trainings: TrainingsResource) -> None:
        self._trainings = trainings

        self.create = to_streamed_response_wrapper(
            trainings.create,
        )
        self.list = to_streamed_response_wrapper(
            trainings.list,
        )
        self.cancel = to_streamed_response_wrapper(
            trainings.cancel,
        )
        self.get = to_streamed_response_wrapper(
            trainings.get,
        )


class AsyncTrainingsResourceWithStreamingResponse:
    def __init__(self, trainings: AsyncTrainingsResource) -> None:
        self._trainings = trainings

        self.create = async_to_streamed_response_wrapper(
            trainings.create,
        )
        self.list = async_to_streamed_response_wrapper(
            trainings.list,
        )
        self.cancel = async_to_streamed_response_wrapper(
            trainings.cancel,
        )
        self.get = async_to_streamed_response_wrapper(
            trainings.get,
        )
