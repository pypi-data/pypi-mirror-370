# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...types import deployment_create_params, deployment_update_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
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
from ...types.deployment_get_response import DeploymentGetResponse
from ...types.deployment_list_response import DeploymentListResponse
from ...types.deployment_create_response import DeploymentCreateResponse
from ...types.deployment_update_response import DeploymentUpdateResponse

__all__ = ["DeploymentsResource", "AsyncDeploymentsResource"]


class DeploymentsResource(SyncAPIResource):
    @cached_property
    def predictions(self) -> PredictionsResource:
        return PredictionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> DeploymentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return DeploymentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DeploymentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return DeploymentsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        hardware: str,
        max_instances: int,
        min_instances: int,
        model: str,
        name: str,
        version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeploymentCreateResponse:
        """
        Create a new deployment:

        Example cURL request:

        ```console
        curl -s \\
          -X POST \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          -H "Content-Type: application/json" \\
          -d '{
                "name": "my-app-image-generator",
                "model": "stability-ai/sdxl",
                "version": "da77bc59ee60423279fd632efb4795ab731d9e3ca9705ef3341091fb989b7eaf",
                "hardware": "gpu-t4",
                "min_instances": 0,
                "max_instances": 3
              }' \\
          https://api.replicate.com/v1/deployments
        ```

        The response will be a JSON object describing the deployment:

        ```json
        {
          "owner": "acme",
          "name": "my-app-image-generator",
          "current_release": {
            "number": 1,
            "model": "stability-ai/sdxl",
            "version": "da77bc59ee60423279fd632efb4795ab731d9e3ca9705ef3341091fb989b7eaf",
            "created_at": "2024-02-15T16:32:57.018467Z",
            "created_by": {
              "type": "organization",
              "username": "acme",
              "name": "Acme Corp, Inc.",
              "avatar_url": "https://cdn.replicate.com/avatars/acme.png",
              "github_url": "https://github.com/acme"
            },
            "configuration": {
              "hardware": "gpu-t4",
              "min_instances": 1,
              "max_instances": 5
            }
          }
        }
        ```

        Args:
          hardware: The SKU for the hardware used to run the model. Possible values can be retrieved
              from the `hardware.list` endpoint.

          max_instances: The maximum number of instances for scaling.

          min_instances: The minimum number of instances for scaling.

          model: The full name of the model that you want to deploy e.g. stability-ai/sdxl.

          name: The name of the deployment.

          version: The 64-character string ID of the model version that you want to deploy.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/deployments",
            body=maybe_transform(
                {
                    "hardware": hardware,
                    "max_instances": max_instances,
                    "min_instances": min_instances,
                    "model": model,
                    "name": name,
                    "version": version,
                },
                deployment_create_params.DeploymentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeploymentCreateResponse,
        )

    def update(
        self,
        *,
        deployment_owner: str,
        deployment_name: str,
        hardware: str | NotGiven = NOT_GIVEN,
        max_instances: int | NotGiven = NOT_GIVEN,
        min_instances: int | NotGiven = NOT_GIVEN,
        version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeploymentUpdateResponse:
        """
        Update properties of an existing deployment, including hardware, min/max
        instances, and the deployment's underlying model
        [version](https://replicate.com/docs/how-does-replicate-work#versions).

        Example cURL request:

        ```console
        curl -s \\
          -X PATCH \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          -H "Content-Type: application/json" \\
          -d '{"min_instances": 3, "max_instances": 10}' \\
          https://api.replicate.com/v1/deployments/acme/my-app-image-generator
        ```

        The response will be a JSON object describing the deployment:

        ```json
        {
          "owner": "acme",
          "name": "my-app-image-generator",
          "current_release": {
            "number": 2,
            "model": "stability-ai/sdxl",
            "version": "da77bc59ee60423279fd632efb4795ab731d9e3ca9705ef3341091fb989b7eaf",
            "created_at": "2024-02-15T16:32:57.018467Z",
            "created_by": {
              "type": "organization",
              "username": "acme",
              "name": "Acme Corp, Inc.",
              "avatar_url": "https://cdn.replicate.com/avatars/acme.png",
              "github_url": "https://github.com/acme"
            },
            "configuration": {
              "hardware": "gpu-t4",
              "min_instances": 3,
              "max_instances": 10
            }
          }
        }
        ```

        Updating any deployment properties will increment the `number` field of the
        `current_release`.

        Args:
          hardware: The SKU for the hardware used to run the model. Possible values can be retrieved
              from the `hardware.list` endpoint.

          max_instances: The maximum number of instances for scaling.

          min_instances: The minimum number of instances for scaling.

          version: The ID of the model version that you want to deploy

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not deployment_owner:
            raise ValueError(f"Expected a non-empty value for `deployment_owner` but received {deployment_owner!r}")
        if not deployment_name:
            raise ValueError(f"Expected a non-empty value for `deployment_name` but received {deployment_name!r}")
        return self._patch(
            f"/deployments/{deployment_owner}/{deployment_name}",
            body=maybe_transform(
                {
                    "hardware": hardware,
                    "max_instances": max_instances,
                    "min_instances": min_instances,
                    "version": version,
                },
                deployment_update_params.DeploymentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeploymentUpdateResponse,
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
    ) -> SyncCursorURLPage[DeploymentListResponse]:
        """
        Get a list of deployments associated with the current account, including the
        latest release configuration for each deployment.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/deployments
        ```

        The response will be a paginated JSON array of deployment objects, sorted with
        the most recent deployment first:

        ```json
        {
          "next": "http://api.replicate.com/v1/deployments?cursor=cD0yMDIzLTA2LTA2KzIzJTNBNDAlM0EwOC45NjMwMDAlMkIwMCUzQTAw",
          "previous": null,
          "results": [
            {
              "owner": "replicate",
              "name": "my-app-image-generator",
              "current_release": {
                "number": 1,
                "model": "stability-ai/sdxl",
                "version": "da77bc59ee60423279fd632efb4795ab731d9e3ca9705ef3341091fb989b7eaf",
                "created_at": "2024-02-15T16:32:57.018467Z",
                "created_by": {
                  "type": "organization",
                  "username": "acme",
                  "name": "Acme Corp, Inc.",
                  "avatar_url": "https://cdn.replicate.com/avatars/acme.png",
                  "github_url": "https://github.com/acme"
                },
                "configuration": {
                  "hardware": "gpu-t4",
                  "min_instances": 1,
                  "max_instances": 5
                }
              }
            }
          ]
        }
        ```
        """
        return self._get_api_list(
            "/deployments",
            page=SyncCursorURLPage[DeploymentListResponse],
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            model=DeploymentListResponse,
        )

    def delete(
        self,
        *,
        deployment_owner: str,
        deployment_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete a deployment

        Deployment deletion has some restrictions:

        - You can only delete deployments that have been offline and unused for at least
          15 minutes.

        Example cURL request:

        ```command
        curl -s -X DELETE \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/deployments/acme/my-app-image-generator
        ```

        The response will be an empty 204, indicating the deployment has been deleted.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not deployment_owner:
            raise ValueError(f"Expected a non-empty value for `deployment_owner` but received {deployment_owner!r}")
        if not deployment_name:
            raise ValueError(f"Expected a non-empty value for `deployment_name` but received {deployment_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/deployments/{deployment_owner}/{deployment_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get(
        self,
        *,
        deployment_owner: str,
        deployment_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeploymentGetResponse:
        """
        Get information about a deployment by name including the current release.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/deployments/replicate/my-app-image-generator
        ```

        The response will be a JSON object describing the deployment:

        ```json
        {
          "owner": "acme",
          "name": "my-app-image-generator",
          "current_release": {
            "number": 1,
            "model": "stability-ai/sdxl",
            "version": "da77bc59ee60423279fd632efb4795ab731d9e3ca9705ef3341091fb989b7eaf",
            "created_at": "2024-02-15T16:32:57.018467Z",
            "created_by": {
              "type": "organization",
              "username": "acme",
              "name": "Acme Corp, Inc.",
              "avatar_url": "https://cdn.replicate.com/avatars/acme.png",
              "github_url": "https://github.com/acme"
            },
            "configuration": {
              "hardware": "gpu-t4",
              "min_instances": 1,
              "max_instances": 5
            }
          }
        }
        ```

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not deployment_owner:
            raise ValueError(f"Expected a non-empty value for `deployment_owner` but received {deployment_owner!r}")
        if not deployment_name:
            raise ValueError(f"Expected a non-empty value for `deployment_name` but received {deployment_name!r}")
        return self._get(
            f"/deployments/{deployment_owner}/{deployment_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeploymentGetResponse,
        )


class AsyncDeploymentsResource(AsyncAPIResource):
    @cached_property
    def predictions(self) -> AsyncPredictionsResource:
        return AsyncPredictionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDeploymentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return AsyncDeploymentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDeploymentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return AsyncDeploymentsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        hardware: str,
        max_instances: int,
        min_instances: int,
        model: str,
        name: str,
        version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeploymentCreateResponse:
        """
        Create a new deployment:

        Example cURL request:

        ```console
        curl -s \\
          -X POST \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          -H "Content-Type: application/json" \\
          -d '{
                "name": "my-app-image-generator",
                "model": "stability-ai/sdxl",
                "version": "da77bc59ee60423279fd632efb4795ab731d9e3ca9705ef3341091fb989b7eaf",
                "hardware": "gpu-t4",
                "min_instances": 0,
                "max_instances": 3
              }' \\
          https://api.replicate.com/v1/deployments
        ```

        The response will be a JSON object describing the deployment:

        ```json
        {
          "owner": "acme",
          "name": "my-app-image-generator",
          "current_release": {
            "number": 1,
            "model": "stability-ai/sdxl",
            "version": "da77bc59ee60423279fd632efb4795ab731d9e3ca9705ef3341091fb989b7eaf",
            "created_at": "2024-02-15T16:32:57.018467Z",
            "created_by": {
              "type": "organization",
              "username": "acme",
              "name": "Acme Corp, Inc.",
              "avatar_url": "https://cdn.replicate.com/avatars/acme.png",
              "github_url": "https://github.com/acme"
            },
            "configuration": {
              "hardware": "gpu-t4",
              "min_instances": 1,
              "max_instances": 5
            }
          }
        }
        ```

        Args:
          hardware: The SKU for the hardware used to run the model. Possible values can be retrieved
              from the `hardware.list` endpoint.

          max_instances: The maximum number of instances for scaling.

          min_instances: The minimum number of instances for scaling.

          model: The full name of the model that you want to deploy e.g. stability-ai/sdxl.

          name: The name of the deployment.

          version: The 64-character string ID of the model version that you want to deploy.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/deployments",
            body=await async_maybe_transform(
                {
                    "hardware": hardware,
                    "max_instances": max_instances,
                    "min_instances": min_instances,
                    "model": model,
                    "name": name,
                    "version": version,
                },
                deployment_create_params.DeploymentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeploymentCreateResponse,
        )

    async def update(
        self,
        *,
        deployment_owner: str,
        deployment_name: str,
        hardware: str | NotGiven = NOT_GIVEN,
        max_instances: int | NotGiven = NOT_GIVEN,
        min_instances: int | NotGiven = NOT_GIVEN,
        version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeploymentUpdateResponse:
        """
        Update properties of an existing deployment, including hardware, min/max
        instances, and the deployment's underlying model
        [version](https://replicate.com/docs/how-does-replicate-work#versions).

        Example cURL request:

        ```console
        curl -s \\
          -X PATCH \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          -H "Content-Type: application/json" \\
          -d '{"min_instances": 3, "max_instances": 10}' \\
          https://api.replicate.com/v1/deployments/acme/my-app-image-generator
        ```

        The response will be a JSON object describing the deployment:

        ```json
        {
          "owner": "acme",
          "name": "my-app-image-generator",
          "current_release": {
            "number": 2,
            "model": "stability-ai/sdxl",
            "version": "da77bc59ee60423279fd632efb4795ab731d9e3ca9705ef3341091fb989b7eaf",
            "created_at": "2024-02-15T16:32:57.018467Z",
            "created_by": {
              "type": "organization",
              "username": "acme",
              "name": "Acme Corp, Inc.",
              "avatar_url": "https://cdn.replicate.com/avatars/acme.png",
              "github_url": "https://github.com/acme"
            },
            "configuration": {
              "hardware": "gpu-t4",
              "min_instances": 3,
              "max_instances": 10
            }
          }
        }
        ```

        Updating any deployment properties will increment the `number` field of the
        `current_release`.

        Args:
          hardware: The SKU for the hardware used to run the model. Possible values can be retrieved
              from the `hardware.list` endpoint.

          max_instances: The maximum number of instances for scaling.

          min_instances: The minimum number of instances for scaling.

          version: The ID of the model version that you want to deploy

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not deployment_owner:
            raise ValueError(f"Expected a non-empty value for `deployment_owner` but received {deployment_owner!r}")
        if not deployment_name:
            raise ValueError(f"Expected a non-empty value for `deployment_name` but received {deployment_name!r}")
        return await self._patch(
            f"/deployments/{deployment_owner}/{deployment_name}",
            body=await async_maybe_transform(
                {
                    "hardware": hardware,
                    "max_instances": max_instances,
                    "min_instances": min_instances,
                    "version": version,
                },
                deployment_update_params.DeploymentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeploymentUpdateResponse,
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
    ) -> AsyncPaginator[DeploymentListResponse, AsyncCursorURLPage[DeploymentListResponse]]:
        """
        Get a list of deployments associated with the current account, including the
        latest release configuration for each deployment.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/deployments
        ```

        The response will be a paginated JSON array of deployment objects, sorted with
        the most recent deployment first:

        ```json
        {
          "next": "http://api.replicate.com/v1/deployments?cursor=cD0yMDIzLTA2LTA2KzIzJTNBNDAlM0EwOC45NjMwMDAlMkIwMCUzQTAw",
          "previous": null,
          "results": [
            {
              "owner": "replicate",
              "name": "my-app-image-generator",
              "current_release": {
                "number": 1,
                "model": "stability-ai/sdxl",
                "version": "da77bc59ee60423279fd632efb4795ab731d9e3ca9705ef3341091fb989b7eaf",
                "created_at": "2024-02-15T16:32:57.018467Z",
                "created_by": {
                  "type": "organization",
                  "username": "acme",
                  "name": "Acme Corp, Inc.",
                  "avatar_url": "https://cdn.replicate.com/avatars/acme.png",
                  "github_url": "https://github.com/acme"
                },
                "configuration": {
                  "hardware": "gpu-t4",
                  "min_instances": 1,
                  "max_instances": 5
                }
              }
            }
          ]
        }
        ```
        """
        return self._get_api_list(
            "/deployments",
            page=AsyncCursorURLPage[DeploymentListResponse],
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            model=DeploymentListResponse,
        )

    async def delete(
        self,
        *,
        deployment_owner: str,
        deployment_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete a deployment

        Deployment deletion has some restrictions:

        - You can only delete deployments that have been offline and unused for at least
          15 minutes.

        Example cURL request:

        ```command
        curl -s -X DELETE \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/deployments/acme/my-app-image-generator
        ```

        The response will be an empty 204, indicating the deployment has been deleted.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not deployment_owner:
            raise ValueError(f"Expected a non-empty value for `deployment_owner` but received {deployment_owner!r}")
        if not deployment_name:
            raise ValueError(f"Expected a non-empty value for `deployment_name` but received {deployment_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/deployments/{deployment_owner}/{deployment_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get(
        self,
        *,
        deployment_owner: str,
        deployment_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeploymentGetResponse:
        """
        Get information about a deployment by name including the current release.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/deployments/replicate/my-app-image-generator
        ```

        The response will be a JSON object describing the deployment:

        ```json
        {
          "owner": "acme",
          "name": "my-app-image-generator",
          "current_release": {
            "number": 1,
            "model": "stability-ai/sdxl",
            "version": "da77bc59ee60423279fd632efb4795ab731d9e3ca9705ef3341091fb989b7eaf",
            "created_at": "2024-02-15T16:32:57.018467Z",
            "created_by": {
              "type": "organization",
              "username": "acme",
              "name": "Acme Corp, Inc.",
              "avatar_url": "https://cdn.replicate.com/avatars/acme.png",
              "github_url": "https://github.com/acme"
            },
            "configuration": {
              "hardware": "gpu-t4",
              "min_instances": 1,
              "max_instances": 5
            }
          }
        }
        ```

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not deployment_owner:
            raise ValueError(f"Expected a non-empty value for `deployment_owner` but received {deployment_owner!r}")
        if not deployment_name:
            raise ValueError(f"Expected a non-empty value for `deployment_name` but received {deployment_name!r}")
        return await self._get(
            f"/deployments/{deployment_owner}/{deployment_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeploymentGetResponse,
        )


class DeploymentsResourceWithRawResponse:
    def __init__(self, deployments: DeploymentsResource) -> None:
        self._deployments = deployments

        self.create = to_raw_response_wrapper(
            deployments.create,
        )
        self.update = to_raw_response_wrapper(
            deployments.update,
        )
        self.list = to_raw_response_wrapper(
            deployments.list,
        )
        self.delete = to_raw_response_wrapper(
            deployments.delete,
        )
        self.get = to_raw_response_wrapper(
            deployments.get,
        )

    @cached_property
    def predictions(self) -> PredictionsResourceWithRawResponse:
        return PredictionsResourceWithRawResponse(self._deployments.predictions)


class AsyncDeploymentsResourceWithRawResponse:
    def __init__(self, deployments: AsyncDeploymentsResource) -> None:
        self._deployments = deployments

        self.create = async_to_raw_response_wrapper(
            deployments.create,
        )
        self.update = async_to_raw_response_wrapper(
            deployments.update,
        )
        self.list = async_to_raw_response_wrapper(
            deployments.list,
        )
        self.delete = async_to_raw_response_wrapper(
            deployments.delete,
        )
        self.get = async_to_raw_response_wrapper(
            deployments.get,
        )

    @cached_property
    def predictions(self) -> AsyncPredictionsResourceWithRawResponse:
        return AsyncPredictionsResourceWithRawResponse(self._deployments.predictions)


class DeploymentsResourceWithStreamingResponse:
    def __init__(self, deployments: DeploymentsResource) -> None:
        self._deployments = deployments

        self.create = to_streamed_response_wrapper(
            deployments.create,
        )
        self.update = to_streamed_response_wrapper(
            deployments.update,
        )
        self.list = to_streamed_response_wrapper(
            deployments.list,
        )
        self.delete = to_streamed_response_wrapper(
            deployments.delete,
        )
        self.get = to_streamed_response_wrapper(
            deployments.get,
        )

    @cached_property
    def predictions(self) -> PredictionsResourceWithStreamingResponse:
        return PredictionsResourceWithStreamingResponse(self._deployments.predictions)


class AsyncDeploymentsResourceWithStreamingResponse:
    def __init__(self, deployments: AsyncDeploymentsResource) -> None:
        self._deployments = deployments

        self.create = async_to_streamed_response_wrapper(
            deployments.create,
        )
        self.update = async_to_streamed_response_wrapper(
            deployments.update,
        )
        self.list = async_to_streamed_response_wrapper(
            deployments.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            deployments.delete,
        )
        self.get = async_to_streamed_response_wrapper(
            deployments.get,
        )

    @cached_property
    def predictions(self) -> AsyncPredictionsResourceWithStreamingResponse:
        return AsyncPredictionsResourceWithStreamingResponse(self._deployments.predictions)
