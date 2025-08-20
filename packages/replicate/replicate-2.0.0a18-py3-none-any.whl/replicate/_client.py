# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import (
    TYPE_CHECKING,
    Any,
    Union,
    Literal,
    Mapping,
    TypeVar,
    Callable,
    Iterator,
    Optional,
    AsyncIterator,
    overload,
)
from typing_extensions import Self, Unpack, ParamSpec, override

import httpx

from replicate.lib.cog import _get_api_token_from_environment
from replicate.lib._files import FileEncodingStrategy
from replicate.lib._predictions_run import Model, Version, ModelVersionIdentifier
from replicate.types.prediction_create_params import PredictionCreateParamsWithoutVersion

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import is_given, get_async_library
from ._compat import cached_property
from ._version import __version__
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError, ReplicateError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

if TYPE_CHECKING:
    from .resources import files, models, account, hardware, webhooks, trainings, collections, deployments, predictions
    from .resources.files import FilesResource, AsyncFilesResource
    from .resources.account import AccountResource, AsyncAccountResource
    from .resources.hardware import HardwareResource, AsyncHardwareResource
    from .resources.trainings import TrainingsResource, AsyncTrainingsResource
    from .resources.collections import CollectionsResource, AsyncCollectionsResource
    from .resources.predictions import PredictionsResource, AsyncPredictionsResource
    from .resources.models.models import ModelsResource, AsyncModelsResource
    from .resources.webhooks.webhooks import WebhooksResource, AsyncWebhooksResource
    from .resources.deployments.deployments import DeploymentsResource, AsyncDeploymentsResource

if TYPE_CHECKING:
    from .lib._predictions_use import Function, FunctionRef, AsyncFunction

Input = ParamSpec("Input")
Output = TypeVar("Output")

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Replicate",
    "AsyncReplicate",
    "Client",
    "AsyncClient",
]


class Replicate(SyncAPIClient):
    # client options
    bearer_token: str

    def __init__(
        self,
        *,
        bearer_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Replicate client instance.

        This automatically infers the `bearer_token` argument from the `REPLICATE_API_TOKEN` environment variable if it is not provided.
        """
        if bearer_token is None:
            bearer_token = _get_api_token_from_environment()
        if bearer_token is None:
            raise ReplicateError(
                "The bearer_token client option must be set either by passing bearer_token to the client or by setting the REPLICATE_API_TOKEN environment variable"
            )
        self.bearer_token = bearer_token

        if base_url is None:
            base_url = os.environ.get("REPLICATE_BASE_URL")
        if base_url is None:
            base_url = f"https://api.replicate.com/v1"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

    @cached_property
    def collections(self) -> CollectionsResource:
        from .resources.collections import CollectionsResource

        return CollectionsResource(self)

    @cached_property
    def deployments(self) -> DeploymentsResource:
        from .resources.deployments import DeploymentsResource

        return DeploymentsResource(self)

    @cached_property
    def hardware(self) -> HardwareResource:
        from .resources.hardware import HardwareResource

        return HardwareResource(self)

    @cached_property
    def account(self) -> AccountResource:
        from .resources.account import AccountResource

        return AccountResource(self)

    @cached_property
    def models(self) -> ModelsResource:
        from .resources.models import ModelsResource

        return ModelsResource(self)

    @cached_property
    def predictions(self) -> PredictionsResource:
        from .resources.predictions import PredictionsResource

        return PredictionsResource(self)

    @cached_property
    def trainings(self) -> TrainingsResource:
        from .resources.trainings import TrainingsResource

        return TrainingsResource(self)

    @cached_property
    def webhooks(self) -> WebhooksResource:
        from .resources.webhooks import WebhooksResource

        return WebhooksResource(self)

    @cached_property
    def files(self) -> FilesResource:
        from .resources.files import FilesResource

        return FilesResource(self)

    @cached_property
    def with_raw_response(self) -> ReplicateWithRawResponse:
        return ReplicateWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ReplicateWithStreamedResponse:
        return ReplicateWithStreamedResponse(self)

    @cached_property
    def poll_interval(self) -> float:
        return float(os.environ.get("REPLICATE_POLL_INTERVAL", "0.5"))

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        bearer_token = self.bearer_token
        return {"Authorization": f"Bearer {bearer_token}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def run(
        self,
        ref: Union[Model, Version, ModelVersionIdentifier, str],
        *,
        file_encoding_strategy: Optional["FileEncodingStrategy"] = None,
        use_file_output: bool = True,
        wait: Union[int, bool, NotGiven] = NOT_GIVEN,
        **params: Unpack[PredictionCreateParamsWithoutVersion],
    ) -> Any:
        """
        Run a model prediction.

        Args:
            ref: Reference to the model or version to run. Can be:
                - A string containing a version ID (e.g. "5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa")
                - A string with owner/name format (e.g. "replicate/hello-world")
                - A string with owner/name:version format (e.g. "replicate/hello-world:5c7d5dc6...")
                - A Model instance with owner and name attributes
                - A Version instance with id attribute
                - A ModelVersionIdentifier dictionary with owner, name, and/or version keys
            file_encoding_strategy: Strategy for encoding file inputs, options are "base64" or "url"
            use_file_output: If True (default), convert output URLs to FileOutput objects
            wait: If True (default), wait for the prediction to complete. If False, return immediately.
                  If an integer, wait up to that many seconds.
            **params: Additional parameters to pass to the prediction creation endpoint including
                      the required "input" dictionary with model-specific parameters

        Returns:
            The prediction output, which could be a basic type (str, int, etc.), a FileOutput object,
            a list of FileOutput objects, or a dictionary of FileOutput objects, depending on what
            the model returns.

        Raises:
            ModelError: If the model run fails
            ValueError: If the reference format is invalid
            TypeError: If both wait and prefer parameters are provided
        """
        from .lib._predictions_run import run

        return run(
            self,
            ref,
            wait=wait,
            use_file_output=use_file_output,
            file_encoding_strategy=file_encoding_strategy,
            **params,
        )

    @overload
    def use(
        self,
        ref: Union[str, "FunctionRef[Input, Output]"],
        *,
        hint: Optional[Callable["Input", "Output"]] = None,
        streaming: Literal[False] = False,
    ) -> "Function[Input, Output]": ...

    @overload
    def use(
        self,
        ref: Union[str, "FunctionRef[Input, Output]"],
        *,
        hint: Optional[Callable["Input", "Output"]] = None,
        streaming: Literal[True],
    ) -> "Function[Input, Iterator[Output]]": ...

    def use(
        self,
        ref: Union[str, "FunctionRef[Input, Output]"],
        *,
        hint: Optional[Callable["Input", "Output"]] = None,
        streaming: bool = False,
    ) -> Union["Function[Input, Output]", "Function[Input, Iterator[Output]]"]:
        """
        Use a Replicate model as a function.

        Example:
            flux_dev = replicate.use("black-forest-labs/flux-dev")
            output = flux_dev(prompt="make me a sandwich")
        """
        from .lib._predictions_use import use as _use

        # TODO: Fix mypy overload matching for streaming parameter
        return _use(self, ref, hint=hint, streaming=streaming)  # type: ignore[call-overload, no-any-return]

    def copy(
        self,
        *,
        bearer_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            bearer_token=bearer_token or self.bearer_token,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncReplicate(AsyncAPIClient):
    # client options
    bearer_token: str

    def __init__(
        self,
        *,
        bearer_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncReplicate client instance.

        This automatically infers the `bearer_token` argument from the `REPLICATE_API_TOKEN` environment variable if it is not provided.
        """
        if bearer_token is None:
            bearer_token = _get_api_token_from_environment()
        if bearer_token is None:
            raise ReplicateError(
                "The bearer_token client option must be set either by passing bearer_token to the client or by setting the REPLICATE_API_TOKEN environment variable"
            )
        self.bearer_token = bearer_token

        if base_url is None:
            base_url = os.environ.get("REPLICATE_BASE_URL")
        if base_url is None:
            base_url = f"https://api.replicate.com/v1"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

    @cached_property
    def collections(self) -> AsyncCollectionsResource:
        from .resources.collections import AsyncCollectionsResource

        return AsyncCollectionsResource(self)

    @cached_property
    def deployments(self) -> AsyncDeploymentsResource:
        from .resources.deployments import AsyncDeploymentsResource

        return AsyncDeploymentsResource(self)

    @cached_property
    def hardware(self) -> AsyncHardwareResource:
        from .resources.hardware import AsyncHardwareResource

        return AsyncHardwareResource(self)

    @cached_property
    def account(self) -> AsyncAccountResource:
        from .resources.account import AsyncAccountResource

        return AsyncAccountResource(self)

    @cached_property
    def models(self) -> AsyncModelsResource:
        from .resources.models import AsyncModelsResource

        return AsyncModelsResource(self)

    @cached_property
    def predictions(self) -> AsyncPredictionsResource:
        from .resources.predictions import AsyncPredictionsResource

        return AsyncPredictionsResource(self)

    @cached_property
    def trainings(self) -> AsyncTrainingsResource:
        from .resources.trainings import AsyncTrainingsResource

        return AsyncTrainingsResource(self)

    @cached_property
    def webhooks(self) -> AsyncWebhooksResource:
        from .resources.webhooks import AsyncWebhooksResource

        return AsyncWebhooksResource(self)

    @cached_property
    def files(self) -> AsyncFilesResource:
        from .resources.files import AsyncFilesResource

        return AsyncFilesResource(self)

    @cached_property
    def with_raw_response(self) -> AsyncReplicateWithRawResponse:
        return AsyncReplicateWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncReplicateWithStreamedResponse:
        return AsyncReplicateWithStreamedResponse(self)

    @cached_property
    def poll_interval(self) -> float:
        return float(os.environ.get("REPLICATE_POLL_INTERVAL", "0.5"))

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        bearer_token = self.bearer_token
        return {"Authorization": f"Bearer {bearer_token}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    async def run(
        self,
        ref: Union[Model, Version, ModelVersionIdentifier, str],
        *,
        use_file_output: bool = True,
        file_encoding_strategy: Optional["FileEncodingStrategy"] = None,
        wait: Union[int, bool, NotGiven] = NOT_GIVEN,
        **params: Unpack[PredictionCreateParamsWithoutVersion],
    ) -> Any:
        """
        Run a model prediction asynchronously.

        Args:
            ref: Reference to the model or version to run. Can be:
                - A string containing a version ID (e.g. "5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa")
                - A string with owner/name format (e.g. "replicate/hello-world")
                - A string with owner/name:version format (e.g. "replicate/hello-world:5c7d5dc6...")
                - A Model instance with owner and name attributes
                - A Version instance with id attribute
                - A ModelVersionIdentifier dictionary with owner, name, and/or version keys
            use_file_output: If True (default), convert output URLs to AsyncFileOutput objects
            file_encoding_strategy: Strategy for encoding file inputs, options are "base64" or "url"
            wait: If True (default), wait for the prediction to complete. If False, return immediately.
                  If an integer, wait up to that many seconds.
            **params: Additional parameters to pass to the prediction creation endpoint including
                      the required "input" dictionary with model-specific parameters

        Returns:
            The prediction output, which could be a basic type (str, int, etc.), an AsyncFileOutput object,
            a list of AsyncFileOutput objects, or a dictionary of AsyncFileOutput objects, depending on what
            the model returns.

        Raises:
            ModelError: If the model run fails
            ValueError: If the reference format is invalid
            TypeError: If both wait and prefer parameters are provided
        """
        from .lib._predictions_run import async_run

        return await async_run(
            self,
            ref,
            wait=wait,
            use_file_output=use_file_output,
            file_encoding_strategy=file_encoding_strategy,
            **params,
        )

    @overload
    def use(
        self,
        ref: Union[str, "FunctionRef[Input, Output]"],
        *,
        hint: Optional[Callable["Input", "Output"]] = None,
        streaming: Literal[False] = False,
    ) -> "AsyncFunction[Input, Output]": ...

    @overload
    def use(
        self,
        ref: Union[str, "FunctionRef[Input, Output]"],
        *,
        hint: Optional[Callable["Input", "Output"]] = None,
        streaming: Literal[True],
    ) -> "AsyncFunction[Input, AsyncIterator[Output]]": ...

    def use(
        self,
        ref: Union[str, "FunctionRef[Input, Output]"],
        *,
        hint: Optional[Callable["Input", "Output"]] = None,
        streaming: bool = False,
    ) -> Union["AsyncFunction[Input, Output]", "AsyncFunction[Input, AsyncIterator[Output]]"]:
        """
        Use a Replicate model as an async function.

        Example:
            flux_dev = replicate.use("black-forest-labs/flux-dev", use_async=True)
            output = await flux_dev(prompt="make me a sandwich")
        """
        from .lib._predictions_use import use as _use

        # TODO: Fix mypy overload matching for streaming parameter
        return _use(self, ref, hint=hint, streaming=streaming)  # type: ignore[call-overload, no-any-return]

    def copy(
        self,
        *,
        bearer_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            bearer_token=bearer_token or self.bearer_token,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class ReplicateWithRawResponse:
    _client: Replicate

    def __init__(self, client: Replicate) -> None:
        self._client = client

    @cached_property
    def collections(self) -> collections.CollectionsResourceWithRawResponse:
        from .resources.collections import CollectionsResourceWithRawResponse

        return CollectionsResourceWithRawResponse(self._client.collections)

    @cached_property
    def deployments(self) -> deployments.DeploymentsResourceWithRawResponse:
        from .resources.deployments import DeploymentsResourceWithRawResponse

        return DeploymentsResourceWithRawResponse(self._client.deployments)

    @cached_property
    def hardware(self) -> hardware.HardwareResourceWithRawResponse:
        from .resources.hardware import HardwareResourceWithRawResponse

        return HardwareResourceWithRawResponse(self._client.hardware)

    @cached_property
    def account(self) -> account.AccountResourceWithRawResponse:
        from .resources.account import AccountResourceWithRawResponse

        return AccountResourceWithRawResponse(self._client.account)

    @cached_property
    def models(self) -> models.ModelsResourceWithRawResponse:
        from .resources.models import ModelsResourceWithRawResponse

        return ModelsResourceWithRawResponse(self._client.models)

    @cached_property
    def predictions(self) -> predictions.PredictionsResourceWithRawResponse:
        from .resources.predictions import PredictionsResourceWithRawResponse

        return PredictionsResourceWithRawResponse(self._client.predictions)

    @cached_property
    def trainings(self) -> trainings.TrainingsResourceWithRawResponse:
        from .resources.trainings import TrainingsResourceWithRawResponse

        return TrainingsResourceWithRawResponse(self._client.trainings)

    @cached_property
    def webhooks(self) -> webhooks.WebhooksResourceWithRawResponse:
        from .resources.webhooks import WebhooksResourceWithRawResponse

        return WebhooksResourceWithRawResponse(self._client.webhooks)

    @cached_property
    def files(self) -> files.FilesResourceWithRawResponse:
        from .resources.files import FilesResourceWithRawResponse

        return FilesResourceWithRawResponse(self._client.files)


class AsyncReplicateWithRawResponse:
    _client: AsyncReplicate

    def __init__(self, client: AsyncReplicate) -> None:
        self._client = client

    @cached_property
    def collections(self) -> collections.AsyncCollectionsResourceWithRawResponse:
        from .resources.collections import AsyncCollectionsResourceWithRawResponse

        return AsyncCollectionsResourceWithRawResponse(self._client.collections)

    @cached_property
    def deployments(self) -> deployments.AsyncDeploymentsResourceWithRawResponse:
        from .resources.deployments import AsyncDeploymentsResourceWithRawResponse

        return AsyncDeploymentsResourceWithRawResponse(self._client.deployments)

    @cached_property
    def hardware(self) -> hardware.AsyncHardwareResourceWithRawResponse:
        from .resources.hardware import AsyncHardwareResourceWithRawResponse

        return AsyncHardwareResourceWithRawResponse(self._client.hardware)

    @cached_property
    def account(self) -> account.AsyncAccountResourceWithRawResponse:
        from .resources.account import AsyncAccountResourceWithRawResponse

        return AsyncAccountResourceWithRawResponse(self._client.account)

    @cached_property
    def models(self) -> models.AsyncModelsResourceWithRawResponse:
        from .resources.models import AsyncModelsResourceWithRawResponse

        return AsyncModelsResourceWithRawResponse(self._client.models)

    @cached_property
    def predictions(self) -> predictions.AsyncPredictionsResourceWithRawResponse:
        from .resources.predictions import AsyncPredictionsResourceWithRawResponse

        return AsyncPredictionsResourceWithRawResponse(self._client.predictions)

    @cached_property
    def trainings(self) -> trainings.AsyncTrainingsResourceWithRawResponse:
        from .resources.trainings import AsyncTrainingsResourceWithRawResponse

        return AsyncTrainingsResourceWithRawResponse(self._client.trainings)

    @cached_property
    def webhooks(self) -> webhooks.AsyncWebhooksResourceWithRawResponse:
        from .resources.webhooks import AsyncWebhooksResourceWithRawResponse

        return AsyncWebhooksResourceWithRawResponse(self._client.webhooks)

    @cached_property
    def files(self) -> files.AsyncFilesResourceWithRawResponse:
        from .resources.files import AsyncFilesResourceWithRawResponse

        return AsyncFilesResourceWithRawResponse(self._client.files)


class ReplicateWithStreamedResponse:
    _client: Replicate

    def __init__(self, client: Replicate) -> None:
        self._client = client

    @cached_property
    def collections(self) -> collections.CollectionsResourceWithStreamingResponse:
        from .resources.collections import CollectionsResourceWithStreamingResponse

        return CollectionsResourceWithStreamingResponse(self._client.collections)

    @cached_property
    def deployments(self) -> deployments.DeploymentsResourceWithStreamingResponse:
        from .resources.deployments import DeploymentsResourceWithStreamingResponse

        return DeploymentsResourceWithStreamingResponse(self._client.deployments)

    @cached_property
    def hardware(self) -> hardware.HardwareResourceWithStreamingResponse:
        from .resources.hardware import HardwareResourceWithStreamingResponse

        return HardwareResourceWithStreamingResponse(self._client.hardware)

    @cached_property
    def account(self) -> account.AccountResourceWithStreamingResponse:
        from .resources.account import AccountResourceWithStreamingResponse

        return AccountResourceWithStreamingResponse(self._client.account)

    @cached_property
    def models(self) -> models.ModelsResourceWithStreamingResponse:
        from .resources.models import ModelsResourceWithStreamingResponse

        return ModelsResourceWithStreamingResponse(self._client.models)

    @cached_property
    def predictions(self) -> predictions.PredictionsResourceWithStreamingResponse:
        from .resources.predictions import PredictionsResourceWithStreamingResponse

        return PredictionsResourceWithStreamingResponse(self._client.predictions)

    @cached_property
    def trainings(self) -> trainings.TrainingsResourceWithStreamingResponse:
        from .resources.trainings import TrainingsResourceWithStreamingResponse

        return TrainingsResourceWithStreamingResponse(self._client.trainings)

    @cached_property
    def webhooks(self) -> webhooks.WebhooksResourceWithStreamingResponse:
        from .resources.webhooks import WebhooksResourceWithStreamingResponse

        return WebhooksResourceWithStreamingResponse(self._client.webhooks)

    @cached_property
    def files(self) -> files.FilesResourceWithStreamingResponse:
        from .resources.files import FilesResourceWithStreamingResponse

        return FilesResourceWithStreamingResponse(self._client.files)


class AsyncReplicateWithStreamedResponse:
    _client: AsyncReplicate

    def __init__(self, client: AsyncReplicate) -> None:
        self._client = client

    @cached_property
    def collections(self) -> collections.AsyncCollectionsResourceWithStreamingResponse:
        from .resources.collections import AsyncCollectionsResourceWithStreamingResponse

        return AsyncCollectionsResourceWithStreamingResponse(self._client.collections)

    @cached_property
    def deployments(self) -> deployments.AsyncDeploymentsResourceWithStreamingResponse:
        from .resources.deployments import AsyncDeploymentsResourceWithStreamingResponse

        return AsyncDeploymentsResourceWithStreamingResponse(self._client.deployments)

    @cached_property
    def hardware(self) -> hardware.AsyncHardwareResourceWithStreamingResponse:
        from .resources.hardware import AsyncHardwareResourceWithStreamingResponse

        return AsyncHardwareResourceWithStreamingResponse(self._client.hardware)

    @cached_property
    def account(self) -> account.AsyncAccountResourceWithStreamingResponse:
        from .resources.account import AsyncAccountResourceWithStreamingResponse

        return AsyncAccountResourceWithStreamingResponse(self._client.account)

    @cached_property
    def models(self) -> models.AsyncModelsResourceWithStreamingResponse:
        from .resources.models import AsyncModelsResourceWithStreamingResponse

        return AsyncModelsResourceWithStreamingResponse(self._client.models)

    @cached_property
    def predictions(self) -> predictions.AsyncPredictionsResourceWithStreamingResponse:
        from .resources.predictions import AsyncPredictionsResourceWithStreamingResponse

        return AsyncPredictionsResourceWithStreamingResponse(self._client.predictions)

    @cached_property
    def trainings(self) -> trainings.AsyncTrainingsResourceWithStreamingResponse:
        from .resources.trainings import AsyncTrainingsResourceWithStreamingResponse

        return AsyncTrainingsResourceWithStreamingResponse(self._client.trainings)

    @cached_property
    def webhooks(self) -> webhooks.AsyncWebhooksResourceWithStreamingResponse:
        from .resources.webhooks import AsyncWebhooksResourceWithStreamingResponse

        return AsyncWebhooksResourceWithStreamingResponse(self._client.webhooks)

    @cached_property
    def files(self) -> files.AsyncFilesResourceWithStreamingResponse:
        from .resources.files import AsyncFilesResourceWithStreamingResponse

        return AsyncFilesResourceWithStreamingResponse(self._client.files)


Client = Replicate

AsyncClient = AsyncReplicate
