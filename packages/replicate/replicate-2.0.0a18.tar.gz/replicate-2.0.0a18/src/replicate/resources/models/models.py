# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from .readme import (
    ReadmeResource,
    AsyncReadmeResource,
    ReadmeResourceWithRawResponse,
    AsyncReadmeResourceWithRawResponse,
    ReadmeResourceWithStreamingResponse,
    AsyncReadmeResourceWithStreamingResponse,
)
from ...types import model_create_params, model_search_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from .examples import (
    ExamplesResource,
    AsyncExamplesResource,
    ExamplesResourceWithRawResponse,
    AsyncExamplesResourceWithRawResponse,
    ExamplesResourceWithStreamingResponse,
    AsyncExamplesResourceWithStreamingResponse,
)
from .versions import (
    VersionsResource,
    AsyncVersionsResource,
    VersionsResourceWithRawResponse,
    AsyncVersionsResourceWithRawResponse,
    VersionsResourceWithStreamingResponse,
    AsyncVersionsResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .predictions import (
    PredictionsResource,
    AsyncPredictionsResource,
    PredictionsResourceWithRawResponse,
    AsyncPredictionsResourceWithRawResponse,
    PredictionsResourceWithStreamingResponse,
    AsyncPredictionsResourceWithStreamingResponse,
)
from ...pagination import SyncCursorURLPage, AsyncCursorURLPage
from ..._base_client import AsyncPaginator, make_request_options
from ...types.model_get_response import ModelGetResponse
from ...types.model_list_response import ModelListResponse
from ...types.model_create_response import ModelCreateResponse
from ...types.model_search_response import ModelSearchResponse

__all__ = ["ModelsResource", "AsyncModelsResource"]


class ModelsResource(SyncAPIResource):
    @cached_property
    def examples(self) -> ExamplesResource:
        return ExamplesResource(self._client)

    @cached_property
    def predictions(self) -> PredictionsResource:
        return PredictionsResource(self._client)

    @cached_property
    def readme(self) -> ReadmeResource:
        return ReadmeResource(self._client)

    @cached_property
    def versions(self) -> VersionsResource:
        return VersionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return ModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return ModelsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        hardware: str,
        name: str,
        owner: str,
        visibility: Literal["public", "private"],
        cover_image_url: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        github_url: str | NotGiven = NOT_GIVEN,
        license_url: str | NotGiven = NOT_GIVEN,
        paper_url: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelCreateResponse:
        """
        Create a model.

        Example cURL request:

        ```console
        curl -s -X POST \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          -H 'Content-Type: application/json' \\
          -d '{"owner": "alice", "name": "hot-dog-detector", "description": "Detect hot dogs in images", "visibility": "public", "hardware": "cpu"}' \\
          https://api.replicate.com/v1/models
        ```

        The response will be a model object in the following format:

        ```json
        {
          "url": "https://replicate.com/alice/hot-dog-detector",
          "owner": "alice",
          "name": "hot-dog-detector",
          "description": "Detect hot dogs in images",
          "visibility": "public",
          "github_url": null,
          "paper_url": null,
          "license_url": null,
          "run_count": 0,
          "cover_image_url": null,
          "default_example": null,
          "latest_version": null
        }
        ```

        Note that there is a limit of 1,000 models per account. For most purposes, we
        recommend using a single model and pushing new
        [versions](https://replicate.com/docs/how-does-replicate-work#versions) of the
        model as you make changes to it.

        Args:
          hardware: The SKU for the hardware used to run the model. Possible values can be retrieved
              from the `hardware.list` endpoint.

          name: The name of the model. This must be unique among all models owned by the user or
              organization.

          owner: The name of the user or organization that will own the model. This must be the
              same as the user or organization that is making the API request. In other words,
              the API token used in the request must belong to this user or organization.

          visibility: Whether the model should be public or private. A public model can be viewed and
              run by anyone, whereas a private model can be viewed and run only by the user or
              organization members that own the model.

          cover_image_url: A URL for the model's cover image. This should be an image file.

          description: A description of the model.

          github_url: A URL for the model's source code on GitHub.

          license_url: A URL for the model's license.

          paper_url: A URL for the model's paper.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/models",
            body=maybe_transform(
                {
                    "hardware": hardware,
                    "name": name,
                    "owner": owner,
                    "visibility": visibility,
                    "cover_image_url": cover_image_url,
                    "description": description,
                    "github_url": github_url,
                    "license_url": license_url,
                    "paper_url": paper_url,
                },
                model_create_params.ModelCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelCreateResponse,
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
    ) -> SyncCursorURLPage[ModelListResponse]:
        """
        Get a paginated list of public models.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/models
        ```

        The response will be a pagination object containing a list of model objects.

        See the [`models.get`](#models.get) docs for more details about the model
        object.
        """
        return self._get_api_list(
            "/models",
            page=SyncCursorURLPage[ModelListResponse],
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            model=ModelListResponse,
        )

    def delete(
        self,
        *,
        model_owner: str,
        model_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete a model

        Model deletion has some restrictions:

        - You can only delete models you own.
        - You can only delete private models.
        - You can only delete models that have no versions associated with them.
          Currently you'll need to
          [delete the model's versions](#models.versions.delete) before you can delete
          the model itself.

        Example cURL request:

        ```command
        curl -s -X DELETE \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/models/replicate/hello-world
        ```

        The response will be an empty 204, indicating the model has been deleted.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_owner:
            raise ValueError(f"Expected a non-empty value for `model_owner` but received {model_owner!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/models/{model_owner}/{model_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get(
        self,
        *,
        model_owner: str,
        model_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelGetResponse:
        """
        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/models/replicate/hello-world
        ```

        The response will be a model object in the following format:

        ```json
        {
          "url": "https://replicate.com/replicate/hello-world",
          "owner": "replicate",
          "name": "hello-world",
          "description": "A tiny model that says hello",
          "visibility": "public",
          "github_url": "https://github.com/replicate/cog-examples",
          "paper_url": null,
          "license_url": null,
          "run_count": 5681081,
          "cover_image_url": "...",
          "default_example": {...},
          "latest_version": {...},
        }
        ```

        The model object includes the
        [input and output schema](https://replicate.com/docs/reference/openapi#model-schemas)
        for the latest version of the model.

        Here's an example showing how to fetch the model with cURL and display its input
        schema with [jq](https://stedolan.github.io/jq/):

        ```console
        curl -s \\
            -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
            https://api.replicate.com/v1/models/replicate/hello-world \\
            | jq ".latest_version.openapi_schema.components.schemas.Input"
        ```

        This will return the following JSON object:

        ```json
        {
          "type": "object",
          "title": "Input",
          "required": ["text"],
          "properties": {
            "text": {
              "type": "string",
              "title": "Text",
              "x-order": 0,
              "description": "Text to prefix with 'hello '"
            }
          }
        }
        ```

        The `cover_image_url` string is an HTTPS URL for an image file. This can be:

        - An image uploaded by the model author.
        - The output file of the example prediction, if the model author has not set a
          cover image.
        - The input file of the example prediction, if the model author has not set a
          cover image and the example prediction has no output file.
        - A generic fallback image.

        The `default_example` object is a [prediction](#predictions.get) created with
        this model.

        The `latest_version` object is the model's most recently pushed
        [version](#models.versions.get).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_owner:
            raise ValueError(f"Expected a non-empty value for `model_owner` but received {model_owner!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        return self._get(
            f"/models/{model_owner}/{model_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelGetResponse,
        )

    def search(
        self,
        *,
        body: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncCursorURLPage[ModelSearchResponse]:
        """
        Get a list of public models matching a search query.

        Example cURL request:

        ```console
        curl -s -X QUERY \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          -H "Content-Type: text/plain" \\
          -d "hello" \\
          https://api.replicate.com/v1/models
        ```

        The response will be a paginated JSON object containing an array of model
        objects.

        See the [`models.get`](#models.get) docs for more details about the model
        object.

        Args:
          body: The search query

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/models",
            page=SyncCursorURLPage[ModelSearchResponse],
            body=maybe_transform(body, model_search_params.ModelSearchParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            model=ModelSearchResponse,
            method="query",
        )


class AsyncModelsResource(AsyncAPIResource):
    @cached_property
    def examples(self) -> AsyncExamplesResource:
        return AsyncExamplesResource(self._client)

    @cached_property
    def predictions(self) -> AsyncPredictionsResource:
        return AsyncPredictionsResource(self._client)

    @cached_property
    def readme(self) -> AsyncReadmeResource:
        return AsyncReadmeResource(self._client)

    @cached_property
    def versions(self) -> AsyncVersionsResource:
        return AsyncVersionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return AsyncModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return AsyncModelsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        hardware: str,
        name: str,
        owner: str,
        visibility: Literal["public", "private"],
        cover_image_url: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        github_url: str | NotGiven = NOT_GIVEN,
        license_url: str | NotGiven = NOT_GIVEN,
        paper_url: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelCreateResponse:
        """
        Create a model.

        Example cURL request:

        ```console
        curl -s -X POST \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          -H 'Content-Type: application/json' \\
          -d '{"owner": "alice", "name": "hot-dog-detector", "description": "Detect hot dogs in images", "visibility": "public", "hardware": "cpu"}' \\
          https://api.replicate.com/v1/models
        ```

        The response will be a model object in the following format:

        ```json
        {
          "url": "https://replicate.com/alice/hot-dog-detector",
          "owner": "alice",
          "name": "hot-dog-detector",
          "description": "Detect hot dogs in images",
          "visibility": "public",
          "github_url": null,
          "paper_url": null,
          "license_url": null,
          "run_count": 0,
          "cover_image_url": null,
          "default_example": null,
          "latest_version": null
        }
        ```

        Note that there is a limit of 1,000 models per account. For most purposes, we
        recommend using a single model and pushing new
        [versions](https://replicate.com/docs/how-does-replicate-work#versions) of the
        model as you make changes to it.

        Args:
          hardware: The SKU for the hardware used to run the model. Possible values can be retrieved
              from the `hardware.list` endpoint.

          name: The name of the model. This must be unique among all models owned by the user or
              organization.

          owner: The name of the user or organization that will own the model. This must be the
              same as the user or organization that is making the API request. In other words,
              the API token used in the request must belong to this user or organization.

          visibility: Whether the model should be public or private. A public model can be viewed and
              run by anyone, whereas a private model can be viewed and run only by the user or
              organization members that own the model.

          cover_image_url: A URL for the model's cover image. This should be an image file.

          description: A description of the model.

          github_url: A URL for the model's source code on GitHub.

          license_url: A URL for the model's license.

          paper_url: A URL for the model's paper.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/models",
            body=await async_maybe_transform(
                {
                    "hardware": hardware,
                    "name": name,
                    "owner": owner,
                    "visibility": visibility,
                    "cover_image_url": cover_image_url,
                    "description": description,
                    "github_url": github_url,
                    "license_url": license_url,
                    "paper_url": paper_url,
                },
                model_create_params.ModelCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelCreateResponse,
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
    ) -> AsyncPaginator[ModelListResponse, AsyncCursorURLPage[ModelListResponse]]:
        """
        Get a paginated list of public models.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/models
        ```

        The response will be a pagination object containing a list of model objects.

        See the [`models.get`](#models.get) docs for more details about the model
        object.
        """
        return self._get_api_list(
            "/models",
            page=AsyncCursorURLPage[ModelListResponse],
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            model=ModelListResponse,
        )

    async def delete(
        self,
        *,
        model_owner: str,
        model_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete a model

        Model deletion has some restrictions:

        - You can only delete models you own.
        - You can only delete private models.
        - You can only delete models that have no versions associated with them.
          Currently you'll need to
          [delete the model's versions](#models.versions.delete) before you can delete
          the model itself.

        Example cURL request:

        ```command
        curl -s -X DELETE \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/models/replicate/hello-world
        ```

        The response will be an empty 204, indicating the model has been deleted.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_owner:
            raise ValueError(f"Expected a non-empty value for `model_owner` but received {model_owner!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/models/{model_owner}/{model_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get(
        self,
        *,
        model_owner: str,
        model_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelGetResponse:
        """
        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/models/replicate/hello-world
        ```

        The response will be a model object in the following format:

        ```json
        {
          "url": "https://replicate.com/replicate/hello-world",
          "owner": "replicate",
          "name": "hello-world",
          "description": "A tiny model that says hello",
          "visibility": "public",
          "github_url": "https://github.com/replicate/cog-examples",
          "paper_url": null,
          "license_url": null,
          "run_count": 5681081,
          "cover_image_url": "...",
          "default_example": {...},
          "latest_version": {...},
        }
        ```

        The model object includes the
        [input and output schema](https://replicate.com/docs/reference/openapi#model-schemas)
        for the latest version of the model.

        Here's an example showing how to fetch the model with cURL and display its input
        schema with [jq](https://stedolan.github.io/jq/):

        ```console
        curl -s \\
            -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
            https://api.replicate.com/v1/models/replicate/hello-world \\
            | jq ".latest_version.openapi_schema.components.schemas.Input"
        ```

        This will return the following JSON object:

        ```json
        {
          "type": "object",
          "title": "Input",
          "required": ["text"],
          "properties": {
            "text": {
              "type": "string",
              "title": "Text",
              "x-order": 0,
              "description": "Text to prefix with 'hello '"
            }
          }
        }
        ```

        The `cover_image_url` string is an HTTPS URL for an image file. This can be:

        - An image uploaded by the model author.
        - The output file of the example prediction, if the model author has not set a
          cover image.
        - The input file of the example prediction, if the model author has not set a
          cover image and the example prediction has no output file.
        - A generic fallback image.

        The `default_example` object is a [prediction](#predictions.get) created with
        this model.

        The `latest_version` object is the model's most recently pushed
        [version](#models.versions.get).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_owner:
            raise ValueError(f"Expected a non-empty value for `model_owner` but received {model_owner!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        return await self._get(
            f"/models/{model_owner}/{model_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelGetResponse,
        )

    def search(
        self,
        *,
        body: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[ModelSearchResponse, AsyncCursorURLPage[ModelSearchResponse]]:
        """
        Get a list of public models matching a search query.

        Example cURL request:

        ```console
        curl -s -X QUERY \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          -H "Content-Type: text/plain" \\
          -d "hello" \\
          https://api.replicate.com/v1/models
        ```

        The response will be a paginated JSON object containing an array of model
        objects.

        See the [`models.get`](#models.get) docs for more details about the model
        object.

        Args:
          body: The search query

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/models",
            page=AsyncCursorURLPage[ModelSearchResponse],
            body=maybe_transform(body, model_search_params.ModelSearchParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            model=ModelSearchResponse,
            method="query",
        )


class ModelsResourceWithRawResponse:
    def __init__(self, models: ModelsResource) -> None:
        self._models = models

        self.create = to_raw_response_wrapper(
            models.create,
        )
        self.list = to_raw_response_wrapper(
            models.list,
        )
        self.delete = to_raw_response_wrapper(
            models.delete,
        )
        self.get = to_raw_response_wrapper(
            models.get,
        )
        self.search = to_raw_response_wrapper(
            models.search,
        )

    @cached_property
    def examples(self) -> ExamplesResourceWithRawResponse:
        return ExamplesResourceWithRawResponse(self._models.examples)

    @cached_property
    def predictions(self) -> PredictionsResourceWithRawResponse:
        return PredictionsResourceWithRawResponse(self._models.predictions)

    @cached_property
    def readme(self) -> ReadmeResourceWithRawResponse:
        return ReadmeResourceWithRawResponse(self._models.readme)

    @cached_property
    def versions(self) -> VersionsResourceWithRawResponse:
        return VersionsResourceWithRawResponse(self._models.versions)


class AsyncModelsResourceWithRawResponse:
    def __init__(self, models: AsyncModelsResource) -> None:
        self._models = models

        self.create = async_to_raw_response_wrapper(
            models.create,
        )
        self.list = async_to_raw_response_wrapper(
            models.list,
        )
        self.delete = async_to_raw_response_wrapper(
            models.delete,
        )
        self.get = async_to_raw_response_wrapper(
            models.get,
        )
        self.search = async_to_raw_response_wrapper(
            models.search,
        )

    @cached_property
    def examples(self) -> AsyncExamplesResourceWithRawResponse:
        return AsyncExamplesResourceWithRawResponse(self._models.examples)

    @cached_property
    def predictions(self) -> AsyncPredictionsResourceWithRawResponse:
        return AsyncPredictionsResourceWithRawResponse(self._models.predictions)

    @cached_property
    def readme(self) -> AsyncReadmeResourceWithRawResponse:
        return AsyncReadmeResourceWithRawResponse(self._models.readme)

    @cached_property
    def versions(self) -> AsyncVersionsResourceWithRawResponse:
        return AsyncVersionsResourceWithRawResponse(self._models.versions)


class ModelsResourceWithStreamingResponse:
    def __init__(self, models: ModelsResource) -> None:
        self._models = models

        self.create = to_streamed_response_wrapper(
            models.create,
        )
        self.list = to_streamed_response_wrapper(
            models.list,
        )
        self.delete = to_streamed_response_wrapper(
            models.delete,
        )
        self.get = to_streamed_response_wrapper(
            models.get,
        )
        self.search = to_streamed_response_wrapper(
            models.search,
        )

    @cached_property
    def examples(self) -> ExamplesResourceWithStreamingResponse:
        return ExamplesResourceWithStreamingResponse(self._models.examples)

    @cached_property
    def predictions(self) -> PredictionsResourceWithStreamingResponse:
        return PredictionsResourceWithStreamingResponse(self._models.predictions)

    @cached_property
    def readme(self) -> ReadmeResourceWithStreamingResponse:
        return ReadmeResourceWithStreamingResponse(self._models.readme)

    @cached_property
    def versions(self) -> VersionsResourceWithStreamingResponse:
        return VersionsResourceWithStreamingResponse(self._models.versions)


class AsyncModelsResourceWithStreamingResponse:
    def __init__(self, models: AsyncModelsResource) -> None:
        self._models = models

        self.create = async_to_streamed_response_wrapper(
            models.create,
        )
        self.list = async_to_streamed_response_wrapper(
            models.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            models.delete,
        )
        self.get = async_to_streamed_response_wrapper(
            models.get,
        )
        self.search = async_to_streamed_response_wrapper(
            models.search,
        )

    @cached_property
    def examples(self) -> AsyncExamplesResourceWithStreamingResponse:
        return AsyncExamplesResourceWithStreamingResponse(self._models.examples)

    @cached_property
    def predictions(self) -> AsyncPredictionsResourceWithStreamingResponse:
        return AsyncPredictionsResourceWithStreamingResponse(self._models.predictions)

    @cached_property
    def readme(self) -> AsyncReadmeResourceWithStreamingResponse:
        return AsyncReadmeResourceWithStreamingResponse(self._models.readme)

    @cached_property
    def versions(self) -> AsyncVersionsResourceWithStreamingResponse:
        return AsyncVersionsResourceWithStreamingResponse(self._models.versions)
