# TODO
# - [ ] Support text streaming
# - [ ] Support file streaming
import os
import copy
import hashlib
import tempfile
from typing import (
    Any,
    Dict,
    List,
    Tuple,
    Union,
    Generic,
    Literal,
    TypeVar,
    Callable,
    Iterator,
    Optional,
    Protocol,
    Generator,
    AsyncIterator,
    cast,
    overload,
)
from pathlib import Path
from functools import cached_property
from typing_extensions import ParamSpec, override

import httpx

from replicate.lib._schema import make_schema_backwards_compatible
from replicate.types.prediction import Prediction
from replicate.types.model_get_response import ModelGetResponse
from replicate.types.models.version_get_response import VersionGetResponse

from ._models import ModelVersionIdentifier
from .._client import Client, AsyncClient
from .._exceptions import ModelError, APIStatusError

__all__ = ["use", "get_path_url"]


def _has_concatenate_iterator_output_type(openapi_schema: Dict[str, Any]) -> bool:
    """
    Returns true if the model output type is ConcatenateIterator or
    AsyncConcatenateIterator.
    """
    output = openapi_schema.get("components", {}).get("schemas", {}).get("Output", {})

    if output.get("type") != "array":
        return False

    if output.get("items", {}).get("type") != "string":
        return False

    if output.get("x-cog-array-type") != "iterator":
        return False

    if output.get("x-cog-array-display") != "concatenate":
        return False

    return True


def _process_iterator_item(item: Any, openapi_schema: Dict[str, Any]) -> Any:
    """
    Process a single item from an iterator output based on schema.
    """
    output_schema = openapi_schema.get("components", {}).get("schemas", {}).get("Output", {})

    # For array/iterator types, check the items schema
    if output_schema.get("type") == "array" and output_schema.get("x-cog-array-type") == "iterator":
        items_schema = output_schema.get("items", {})
        # If items are file URLs, download them
        if items_schema.get("type") == "string" and items_schema.get("format") == "uri":
            if isinstance(item, str) and item.startswith(("http://", "https://")):
                return URLPath(item)

    return item


def _process_output_with_schema(output: Any, openapi_schema: Dict[str, Any]) -> Any:  # pylint: disable=too-many-branches,too-many-nested-blocks
    """
    Process output data, downloading files based on OpenAPI schema.
    """
    output_schema = openapi_schema.get("components", {}).get("schemas", {}).get("Output", {})

    # Handle direct string with format=uri
    if output_schema.get("type") == "string" and output_schema.get("format") == "uri":
        if isinstance(output, str) and output.startswith(("http://", "https://")):
            return URLPath(output)
        return output

    # Handle array of strings with format=uri
    if output_schema.get("type") == "array":
        items = output_schema.get("items", {})
        if items.get("type") == "string" and items.get("format") == "uri":
            if isinstance(output, list):
                return [
                    URLPath(url) if isinstance(url, str) and url.startswith(("http://", "https://")) else url
                    for url in cast(List[Any], output)
                ]
        return output

    # Handle object with properties
    if output_schema.get("type") == "object" and isinstance(output, dict):  # pylint: disable=too-many-nested-blocks
        properties = output_schema.get("properties", {})
        result: Dict[str, Any] = cast(Dict[str, Any], output).copy()

        for prop_name, prop_schema in properties.items():
            if prop_name in result:
                value: Any = result[prop_name]

                # Direct file property
                if prop_schema.get("type") == "string" and prop_schema.get("format") == "uri":
                    if isinstance(value, str) and value.startswith(("http://", "https://")):
                        result[prop_name] = URLPath(value)

                # Array of files property
                elif prop_schema.get("type") == "array":
                    items = prop_schema.get("items", {})
                    if items.get("type") == "string" and items.get("format") == "uri":
                        if isinstance(value, list):
                            result[prop_name] = [
                                URLPath(url)
                                if isinstance(url, str) and url.startswith(("http://", "https://"))
                                else url
                                # TODO: Fix type inference for comprehension variable
                                for url in value  # type: ignore[misc]
                            ]

        return result

    return output


# TODO: Fix complex type inference issues in schema dereferencing
def _dereference_schema(schema: Dict[str, Any]) -> Dict[str, Any]:  # type: ignore[misc]
    """
    Performs basic dereferencing on an OpenAPI schema based on the current schemas generated
    by Replicate. This code assumes that:

    1) References will always point to a field within #/components/schemas and will error
       if the reference is more deeply nested.
    2) That the references when used can be discarded.

    Should something more in-depth be required we could consider using the jsonref package.
    """
    dereferenced = copy.deepcopy(schema)
    schemas = dereferenced.get("components", {}).get("schemas", {})
    dereferenced_refs: set[str] = set()

    def _resolve_ref(obj: Any) -> Any:
        if isinstance(obj, dict):
            if "$ref" in obj:
                ref_path = cast(str, obj["$ref"])
                if ref_path.startswith("#/components/schemas/"):
                    parts = ref_path.replace("#/components/schemas/", "").split("/", 2)

                    if len(parts) > 1:
                        raise NotImplementedError(f"Unexpected nested $ref found in schema: {ref_path}")

                    schema_name = parts[0]
                    if schema_name in schemas:
                        dereferenced_refs.add(schema_name)
                        return _resolve_ref(schemas[schema_name])
                    else:
                        # TODO: Fix return type for refs
                        return obj  # type: ignore[return-value]
                else:
                    # TODO: Fix return type for non-refs
                    return obj  # type: ignore[return-value]
            else:
                # TODO: Fix dict comprehension type inference
                return {key: _resolve_ref(value) for key, value in obj.items()}  # type: ignore[misc]
        elif isinstance(obj, list):
            # TODO: Fix list comprehension type inference
            return [_resolve_ref(item) for item in obj]  # type: ignore[misc]
        else:
            return obj

    result = _resolve_ref(dereferenced)

    # Remove "paths" as these aren't relevant to models.
    result["paths"] = {}

    # Retain Input and Output schemas as these are important.
    dereferenced_refs.discard("Input")
    dereferenced_refs.discard("Output")

    dereferenced_refs.discard("TrainingInput")
    dereferenced_refs.discard("TrainingOutput")

    # Filter out any remaining references that have been inlined.
    result["components"]["schemas"] = {
        k: v for k, v in result["components"]["schemas"].items() if k not in dereferenced_refs
    }

    # TODO: Fix mypy's understanding of the dereferenced schema return type
    return result  # type: ignore[no-any-return]


T = TypeVar("T")


class SyncOutputIterator(Generic[T]):
    """
    A synchronous iterator wrapper that handles both regular iteration and string conversion.
    """

    def __init__(
        self,
        iterator_factory: Callable[[], Iterator[T]],
        schema: Dict[str, Any],
        *,
        is_concatenate: bool,
    ) -> None:
        self.iterator_factory = iterator_factory
        self.schema = schema
        self.is_concatenate = is_concatenate

    def __iter__(self) -> Iterator[T]:
        """Iterate over output items synchronously."""
        for chunk in self.iterator_factory():
            if self.is_concatenate:
                yield chunk
            else:
                yield _process_iterator_item(chunk, self.schema)

    @override
    def __str__(self) -> str:
        """Convert to string by joining segments with empty string."""
        if self.is_concatenate:
            return "".join([str(segment) for segment in self.iterator_factory()])
        return str(list(self.iterator_factory()))


class AsyncOutputIterator(Generic[T]):
    """
    An asynchronous iterator wrapper that handles both regular iteration and string conversion.
    """

    def __init__(
        self,
        async_iterator_factory: Callable[[], AsyncIterator[T]],
        schema: Dict[str, Any],
        *,
        is_concatenate: bool,
    ) -> None:
        self.async_iterator_factory = async_iterator_factory
        self.schema = schema
        self.is_concatenate = is_concatenate

    async def __aiter__(self) -> AsyncIterator[T]:
        """Iterate over output items asynchronously."""
        async for chunk in self.async_iterator_factory():
            if self.is_concatenate:
                yield chunk
            else:
                yield _process_iterator_item(chunk, self.schema)

    def __await__(self) -> Generator[Any, None, Union[List[T], str]]:
        """Make AsyncOutputIterator awaitable, returning appropriate result based on concatenate mode."""

        async def _collect_result() -> Union[List[T], str]:
            if self.is_concatenate:
                # For concatenate iterators, return the joined string
                segments: List[str] = []
                async for segment in self:
                    segments.append(str(segment))
                return "".join(segments)
            # For regular iterators, return the list of items
            items: List[T] = []
            async for item in self:
                items.append(item)
            return items

        return _collect_result().__await__()  # pylint: disable=no-member # return type confuses pylint


class URLPath(os.PathLike[str]):
    """
    A PathLike that defers filesystem ops until first use. Can be used with
    most Python file interfaces like `open()` and `pathlib.Path()`.
    See: https://docs.python.org/3.12/library/os.html#os.PathLike
    """

    def __init__(self, url: str) -> None:
        # store the original URL
        self.__url__ = url

        # compute target path without touching the filesystem
        base = Path(tempfile.gettempdir())
        h = hashlib.sha256(self.__url__.encode("utf-8")).hexdigest()[:16]
        name = Path(httpx.URL(self.__url__).path).name or h
        self.__path__ = base / h / name

    @override
    def __fspath__(self) -> str:
        # on first access, create dirs and download if missing
        if not self.__path__.exists():
            subdir = self.__path__.parent
            subdir.mkdir(parents=True, exist_ok=True)
            if not os.access(subdir, os.W_OK):
                raise PermissionError(f"Cannot write to {subdir!r}")

            with httpx.Client() as client, client.stream("GET", self.__url__) as resp:
                resp.raise_for_status()
                with open(self.__path__, "wb") as f:
                    for chunk in resp.iter_bytes(chunk_size=16_384):
                        f.write(chunk)

        return str(self.__path__)

    @override
    def __str__(self) -> str:
        return self.__fspath__()

    @override
    def __repr__(self) -> str:
        return f"<URLPath url={self.__url__!r} path={self.__path__!r}>"


def get_path_url(path: Any) -> Optional[str]:
    """
    Return the remote URL (if any) for a Path output from a model.
    """
    try:
        # TODO: Fix mypy's understanding of object.__getattribute__ return type
        return object.__getattribute__(path, "__url__")  # type: ignore[no-any-return]
    except AttributeError:
        return None


Input = ParamSpec("Input")
Output = TypeVar("Output")
O = TypeVar("O")


class FunctionRef(Protocol, Generic[Input, Output]):
    """Represents a Replicate model, providing the model identifier and interface."""

    name: str

    __call__: Callable[Input, Output]


class Run(Generic[O]):
    """
    Represents a running prediction with access to the underlying schema.
    """

    _client: Client
    _prediction: Prediction
    _schema: Dict[str, Any]

    def __init__(self, *, client: Client, prediction: Prediction, schema: Dict[str, Any], streaming: bool) -> None:
        self._client = client
        self._prediction = prediction
        self._schema = schema
        self._streaming = streaming

    def output(self) -> O:
        """
        Return the output. For iterator types, returns immediately without waiting.
        For non-iterator types, waits for completion.
        """
        # Return a SyncOutputIterator immediately when streaming, we do this for all
        # model return types regardless of whether they return an iterator.
        if self._streaming:
            is_concatenate = _has_concatenate_iterator_output_type(self._schema)
            return cast(
                O,
                SyncOutputIterator(
                    self._output_iterator,
                    self._schema,
                    is_concatenate=is_concatenate,
                ),
            )

        # For non-streaming, wait for completion and process output
        self._prediction = self._client.predictions.wait(prediction_id=self._prediction.id)

        if self._prediction.status == "failed":
            raise ModelError(self._prediction)

        # Handle concatenate iterators - return joined string
        if _has_concatenate_iterator_output_type(self._schema):
            if isinstance(self._prediction.output, list):
                # TODO: Fix type inference for list comprehension in join
                return cast(O, "".join(str(item) for item in self._prediction.output))  # type: ignore[misc]
            return cast(O, self._prediction.output)

        # Process output for file downloads based on schema
        return cast(O, _process_output_with_schema(self._prediction.output, self._schema))

    def logs(self) -> Optional[str]:
        """
        Fetch and return the logs from the prediction.
        """
        self._prediction = self._client.predictions.get(prediction_id=self._prediction.id)

        return self._prediction.logs

    def _output_iterator(self) -> Iterator[Any]:
        """
        Return an iterator of the prediction output.
        """
        if self._prediction.status in ["succeeded", "failed", "canceled"] and self._prediction.output is not None:
            # TODO: check output is list - for now we assume streaming models return lists
            yield from cast(List[Any], self._prediction.output)

        # TODO: check output is list
        previous_output = cast(List[Any], self._prediction.output or [])
        while self._prediction.status not in ["succeeded", "failed", "canceled"]:
            output = cast(List[Any], self._prediction.output or [])
            new_output = output[len(previous_output) :]
            yield from new_output
            previous_output = output
            import time

            time.sleep(self._client.poll_interval)
            self._prediction = self._client.predictions.get(prediction_id=self._prediction.id)

        if self._prediction.status == "failed":
            raise ModelError(self._prediction)

        output = cast(List[Any], self._prediction.output or [])
        new_output = output[len(previous_output) :]
        yield from new_output


class Function(Generic[Input, Output]):
    """
    A wrapper for a Replicate model that can be called as a function.
    """

    _client: Client
    _ref: str
    _streaming: bool

    def __init__(self, client: Client, ref: str, *, streaming: bool) -> None:
        self._client = client
        self._ref = ref
        self._streaming = streaming

    def __call__(self, *args: Input.args, **inputs: Input.kwargs) -> Output:
        return self.create(*args, **inputs).output()

    def create(self, *_: Input.args, **inputs: Input.kwargs) -> Run[Output]:
        """
        Start a prediction with the specified inputs.
        """
        # Process inputs to convert concatenate SyncOutputIterators to strings and URLPath to URLs
        processed_inputs = {}
        for key, value in inputs.items():
            if isinstance(value, SyncOutputIterator):
                if value.is_concatenate:
                    # TODO: Fix type inference for str() conversion of generic iterator
                    processed_inputs[key] = str(value)  # type: ignore[arg-type]
                else:
                    # TODO: Fix type inference for SyncOutputIterator iteration
                    processed_inputs[key] = list(value)  # type: ignore[arg-type, misc, assignment]
            elif url := get_path_url(value):
                processed_inputs[key] = url
            else:
                # TODO: Fix type inference for generic value assignment
                processed_inputs[key] = value  # type: ignore[assignment]

        version = self._version

        if version:
            if isinstance(version, VersionGetResponse):
                version_id = version.id
            elif isinstance(version, dict) and "id" in version:
                # TODO: Fix type inference for dict access
                version_id = version["id"]  # type: ignore[assignment]
            else:
                # TODO: Fix type inference for str() conversion of version object
                version_id = str(version)  # type: ignore[arg-type]
            # TODO: Fix type inference for version_id
            prediction = self._client.predictions.create(version=version_id, input=processed_inputs)  # type: ignore[arg-type]
        else:
            model = self._model
            # TODO: Fix type inference for processed_inputs dict
            prediction = self._client.models.predictions.create(
                model_owner=model.owner or "",
                model_name=model.name or "",
                input=processed_inputs,  # type: ignore[arg-type]
            )

        return Run(
            client=self._client,
            prediction=prediction,
            schema=self.openapi_schema(),
            streaming=self._streaming,
        )

    @property
    def default_example(self) -> Optional[Dict[str, Any]]:
        """
        Get the default example for this model.
        """
        raise NotImplementedError("This property has not yet been implemented")

    def openapi_schema(self) -> Dict[str, Any]:
        """
        Get the OpenAPI schema for this model version.
        """
        return self._openapi_schema

    @cached_property
    def _openapi_schema(self) -> Dict[str, Any]:
        _, _, model_version = self._parsed_ref
        model = self._model

        version = (
            self._client.models.versions.get(
                model_owner=model.owner or "", model_name=model.name or "", version_id=model_version
            )
            if model_version
            else model.latest_version
        )
        if version is None:
            msg = f"Model {self._model.owner}/{self._model.name} has no version"
            raise ValueError(msg)

        # TODO: Fix type inference for openapi_schema access
        schema = version.openapi_schema  # type: ignore[misc]
        if cog_version := version.cog_version:
            # TODO: Fix type compatibility between version.openapi_schema and Dict[str, Any]
            schema = make_schema_backwards_compatible(schema, cog_version)  # type: ignore[arg-type]
        return _dereference_schema(schema)  # type: ignore[arg-type]

    @cached_property
    def _parsed_ref(self) -> Tuple[str, str, Optional[str]]:
        return ModelVersionIdentifier.parse(self._ref)

    @cached_property
    def _model(self) -> ModelGetResponse:
        model_owner, model_name, _ = self._parsed_ref
        return self._client.models.get(model_owner=model_owner, model_name=model_name)

    @cached_property
    def _version(self) -> Union[VersionGetResponse, object, None]:
        _, _, model_version = self._parsed_ref
        model = self._model
        try:
            versions = self._client.models.versions.list(model_owner=model.owner or "", model_name=model.name or "")
            if len(versions.results) == 0:
                # if we got an empty list when getting model versions, this
                # model is possibly a procedure instead and should be called via
                # the versionless API
                return None
        except APIStatusError as e:
            if e.status_code == 404:
                # if we get a 404 when getting model versions, this is an official
                # model and doesn't have addressable versions (despite what
                # latest_version might tell us)
                return None
            raise

        version = (
            self._client.models.versions.get(
                model_owner=model.owner or "", model_name=model.name or "", version_id=model_version
            )
            if model_version
            else model.latest_version
        )

        return version


class AsyncRun(Generic[O]):
    """
    Represents a running prediction with access to its version (async version).
    """

    _client: AsyncClient
    _prediction: Prediction
    _schema: Dict[str, Any]

    def __init__(self, *, client: AsyncClient, prediction: Prediction, schema: Dict[str, Any], streaming: bool) -> None:
        self._client = client
        self._prediction = prediction
        self._schema = schema
        self._streaming = streaming

    async def output(self) -> O:
        """
        Return the output. For iterator types, returns immediately without waiting.
        For non-iterator types, waits for completion.
        """
        # Return an AsyncOutputIterator immediately when streaming, we do this for all
        # model return types regardless of whether they return an iterator.
        if self._streaming:
            is_concatenate = _has_concatenate_iterator_output_type(self._schema)
            return cast(
                O,
                AsyncOutputIterator(
                    self._async_output_iterator,
                    self._schema,
                    is_concatenate=is_concatenate,
                ),
            )

        # For non-streaming, wait for completion and process output
        self._prediction = await self._client.predictions.wait(prediction_id=self._prediction.id)

        if self._prediction.status == "failed":
            raise ModelError(self._prediction)

        # Handle concatenate iterators - return joined string
        if _has_concatenate_iterator_output_type(self._schema):
            if isinstance(self._prediction.output, list):
                # TODO: Fix type inference for list comprehension in join
                return cast(O, "".join(str(item) for item in self._prediction.output))  # type: ignore[misc]
            return cast(O, self._prediction.output)

        # Process output for file downloads based on schema
        return cast(O, _process_output_with_schema(self._prediction.output, self._schema))

    async def logs(self) -> Optional[str]:
        """
        Fetch and return the logs from the prediction asynchronously.
        """
        self._prediction = await self._client.predictions.get(prediction_id=self._prediction.id)

        return self._prediction.logs

    async def _async_output_iterator(self) -> AsyncIterator[Any]:
        """
        Return an asynchronous iterator of the prediction output.
        """
        if self._prediction.status in ["succeeded", "failed", "canceled"] and self._prediction.output is not None:
            # TODO: check output is list - for now we assume streaming models return lists
            for item in cast(List[Any], self._prediction.output):
                yield item

        # TODO: check output is list
        previous_output = cast(List[Any], self._prediction.output or [])
        while self._prediction.status not in ["succeeded", "failed", "canceled"]:
            output = cast(List[Any], self._prediction.output or [])
            new_output = output[len(previous_output) :]
            for item in new_output:
                yield item
            previous_output = output
            import asyncio

            await asyncio.sleep(self._client.poll_interval)
            self._prediction = await self._client.predictions.get(prediction_id=self._prediction.id)

        if self._prediction.status == "failed":
            raise ModelError(self._prediction)

        output = cast(List[Any], self._prediction.output or [])
        new_output = output[len(previous_output) :]

        for item in new_output:
            yield item


class AsyncFunction(Generic[Input, Output]):
    """
    An async wrapper for a Replicate model that can be called as a function.
    """

    _client: AsyncClient
    _ref: str
    _streaming: bool
    _openapi_schema: Optional[Dict[str, Any]] = None

    def __init__(self, client: AsyncClient, ref: str, *, streaming: bool) -> None:
        self._client = client
        self._ref = ref
        self._streaming = streaming

    @cached_property
    def _parsed_ref(self) -> Tuple[str, str, Optional[str]]:
        return ModelVersionIdentifier.parse(self._ref)

    async def _model(self) -> ModelGetResponse:
        model_owner, model_name, _ = self._parsed_ref
        return await self._client.models.get(model_owner=model_owner, model_name=model_name)

    async def _version(self) -> Union[VersionGetResponse, object, None]:
        _, _, model_version = self._parsed_ref
        model = await self._model()
        try:
            versions = await self._client.models.versions.list(
                model_owner=model.owner or "", model_name=model.name or ""
            )
            if len(versions.results) == 0:
                # if we got an empty list when getting model versions, this
                # model is possibly a procedure instead and should be called via
                # the versionless API
                return None
        except APIStatusError as e:
            if e.status_code == 404:
                # if we get a 404 when getting model versions, this is an official
                # model and doesn't have addressable versions (despite what
                # latest_version might tell us)
                return None
            raise

        if model_version:
            version = await self._client.models.versions.get(
                model_owner=model.owner or "", model_name=model.name or "", version_id=model_version
            )
        else:
            # TODO: Fix type mismatch - latest_version can be None
            version = model.latest_version  # type: ignore[assignment]

        return version

    async def __call__(self, *args: Input.args, **inputs: Input.kwargs) -> Output:
        run = await self.create(*args, **inputs)
        return await run.output()

    async def create(self, *_: Input.args, **inputs: Input.kwargs) -> AsyncRun[Output]:
        """
        Start a prediction with the specified inputs asynchronously.
        """
        # Process inputs to convert concatenate AsyncOutputIterators to strings and URLPath to URLs
        processed_inputs = {}
        for key, value in inputs.items():
            if isinstance(value, AsyncOutputIterator):
                # TODO: Fix type inference for AsyncOutputIterator await
                processed_inputs[key] = await value  # type: ignore[misc]
            elif url := get_path_url(value):
                processed_inputs[key] = url
            else:
                # TODO: Fix type inference for generic value assignment
                processed_inputs[key] = value  # type: ignore[assignment]

        version = await self._version()

        if version:
            if isinstance(version, VersionGetResponse):
                version_id = version.id
            elif isinstance(version, dict) and "id" in version:
                # TODO: Fix type inference for dict access
                version_id = version["id"]  # type: ignore[assignment]
            else:
                # TODO: Fix type inference for str() conversion of version object
                version_id = str(version)  # type: ignore[arg-type]
            # TODO: Fix type inference for version_id
            prediction = await self._client.predictions.create(version=version_id, input=processed_inputs)  # type: ignore[arg-type]
        else:
            model = await self._model()
            # TODO: Fix type inference for processed_inputs dict
            prediction = await self._client.models.predictions.create(
                model_owner=model.owner or "",
                model_name=model.name or "",
                input=processed_inputs,  # type: ignore[arg-type]
            )

        return AsyncRun(
            client=self._client,
            prediction=prediction,
            schema=await self.openapi_schema(),
            streaming=self._streaming,
        )

    @property
    def default_example(self) -> Optional[Dict[str, Any]]:
        """
        Get the default example for this model.
        """
        raise NotImplementedError("This property has not yet been implemented")

    async def openapi_schema(self) -> Dict[str, Any]:
        """
        Get the OpenAPI schema for this model version asynchronously.
        """
        if not self._openapi_schema:
            _, _, model_version = self._parsed_ref

            model = await self._model()
            if model_version:
                version = await self._client.models.versions.get(
                    model_owner=model.owner or "", model_name=model.name or "", version_id=model_version
                )
            else:
                # TODO: Fix type mismatch - latest_version can be None
                version = model.latest_version  # type: ignore[assignment]

            # TODO: Fix mypy's type narrowing - version can be None from latest_version
            if version is None:
                msg = f"Model {model.owner}/{model.name} has no version"  # type: ignore[unreachable]
                raise ValueError(msg)

            # TODO: Fix type inference for openapi_schema access
            schema = version.openapi_schema  # type: ignore[misc]
            if cog_version := version.cog_version:
                # TODO: Fix type compatibility between version.openapi_schema and Dict[str, Any]
                schema = make_schema_backwards_compatible(schema, cog_version)  # type: ignore[arg-type]

            self._openapi_schema = _dereference_schema(schema)  # type: ignore[arg-type]

        return self._openapi_schema


@overload
def use(
    client: Client,
    ref: Union[str, FunctionRef[Input, Output]],
    *,
    hint: Optional[Callable[Input, Output]] = None,
    streaming: Literal[False] = False,
) -> Function[Input, Output]: ...


@overload
def use(
    client: Client,
    ref: Union[str, FunctionRef[Input, Output]],
    *,
    hint: Optional[Callable[Input, Output]] = None,
    streaming: Literal[True],
) -> Function[Input, Iterator[Output]]: ...


@overload
def use(
    client: AsyncClient,
    ref: Union[str, FunctionRef[Input, Output]],
    *,
    hint: Optional[Callable[Input, Output]] = None,
    streaming: Literal[False] = False,
) -> AsyncFunction[Input, Output]: ...


@overload
def use(
    client: AsyncClient,
    ref: Union[str, FunctionRef[Input, Output]],
    *,
    hint: Optional[Callable[Input, Output]] = None,
    streaming: Literal[True],
) -> AsyncFunction[Input, AsyncIterator[Output]]: ...


def use(
    client: Union[Client, AsyncClient],
    ref: Union[str, FunctionRef[Input, Output]],
    *,
    hint: Optional[Callable[Input, Output]] = None,  # pylint: disable=unused-argument # noqa: ARG001 # required for type inference
    streaming: bool = False,
) -> Union[
    Function[Input, Output],
    AsyncFunction[Input, Output],
    Function[Input, Iterator[Output]],
    AsyncFunction[Input, AsyncIterator[Output]],
]:
    """
    Use a Replicate model as a function.

    Example:

        flux_dev = replicate.use("black-forest-labs/flux-dev")
        output = flux_dev(prompt="make me a sandwich")

    """
    try:
        ref = ref.name  # type: ignore
    except AttributeError:
        pass

    if isinstance(client, AsyncClient):
        # TODO: Fix type inference for AsyncFunction return type
        return AsyncFunction(client, str(ref), streaming=streaming)  # type: ignore[return-value]

    # TODO: Fix type inference for Function return type
    return Function(client, str(ref), streaming=streaming)  # type: ignore[return-value]
