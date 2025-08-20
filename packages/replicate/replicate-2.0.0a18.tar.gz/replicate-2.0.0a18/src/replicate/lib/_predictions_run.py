from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Dict, List, Union, Iterable, Iterator, Optional
from collections.abc import AsyncIterator
from typing_extensions import Unpack

from replicate.lib._files import FileEncodingStrategy
from replicate.lib._schema import make_schema_backwards_compatible
from replicate.types.prediction import Prediction
from replicate.types.prediction_create_params import PredictionCreateParamsWithoutVersion

from ..types import PredictionCreateParams
from .._types import NOT_GIVEN, NotGiven
from .._utils import is_given
from ._models import Model, Version, ModelVersionIdentifier, resolve_reference
from .._exceptions import ModelError

if TYPE_CHECKING:
    from ._files import FileOutput
    from .._client import Replicate, AsyncReplicate


def run(
    client: "Replicate",
    ref: Union[Model, Version, ModelVersionIdentifier, str],
    *,
    wait: Union[int, bool, NotGiven] = NOT_GIVEN,
    use_file_output: Optional[bool] = True,
    file_encoding_strategy: Optional["FileEncodingStrategy"] = None,
    **params: Unpack[PredictionCreateParamsWithoutVersion],
) -> object | FileOutput | Iterable[FileOutput] | Dict[str, FileOutput]:
    from ._files import transform_output

    if is_given(wait) and "prefer" in params:
        raise TypeError("cannot mix and match prefer and wait")

    if not is_given(wait):
        wait = True

    is_blocking = wait != False

    if wait:
        if wait is True:
            params.setdefault("prefer", "wait")
        else:
            params.setdefault("prefer", f"wait={wait}")

    # Resolve ref to its components
    version, owner, name, version_id = resolve_reference(ref)

    prediction = None
    if version_id is not None:
        # Create prediction with the specific version ID
        params_with_version: PredictionCreateParams = {**params, "version": version_id}
        prediction = client.predictions.create(file_encoding_strategy=file_encoding_strategy, **params_with_version)
    elif owner and name:
        # Create prediction via models resource with owner/name
        prediction = client.models.predictions.create(
            file_encoding_strategy=file_encoding_strategy, model_owner=owner, model_name=name, **params
        )
    else:
        # If ref is a string but doesn't match expected patterns
        if isinstance(ref, str):
            params_with_version = {**params, "version": ref}
            prediction = client.predictions.create(file_encoding_strategy=file_encoding_strategy, **params_with_version)
        else:
            raise ValueError(
                f"Invalid reference format: {ref}. Expected a model name ('owner/name'), "
                "a version ID, a Model object, a Version object, or a ModelVersionIdentifier."
            )

    # Currently the "Prefer: wait" interface will return a prediction with a status
    # of "processing" rather than a terminal state because it returns before the
    # prediction has been fully processed. If request exceeds the wait time, even if
    # it is actually processing, the prediction will be in a "starting" state.
    #
    # We should fix this in the blocking API itself. Predictions that are done should
    # be in a terminal state and predictions that are processing should be in state
    # "processing".
    in_terminal_state = is_blocking and prediction.status != "starting"
    if not in_terminal_state:
        # Return a "polling" iterator if the model has an output iterator array type.
        if version and _has_output_iterator_array_type(version):
            return (transform_output(chunk, client) for chunk in output_iterator(prediction=prediction, client=client))

        prediction = client.predictions.wait(prediction.id)

    if prediction.status == "failed":
        raise ModelError(prediction)

    # Return an iterator for the completed prediction when needed.
    if version and _has_output_iterator_array_type(version) and prediction.output is not None:
        return (transform_output(chunk, client) for chunk in prediction.output)  # type: ignore

    if use_file_output:
        return transform_output(prediction.output, client)  # type: ignore[no-any-return]

    return prediction.output


async def async_run(
    client: "AsyncReplicate",
    ref: Union[Model, Version, ModelVersionIdentifier, str],
    *,
    file_encoding_strategy: Optional["FileEncodingStrategy"] = None,
    wait: Union[int, bool, NotGiven] = NOT_GIVEN,
    use_file_output: Optional[bool] = True,
    **params: Unpack[PredictionCreateParamsWithoutVersion],
) -> object | FileOutput | Iterable[FileOutput] | Dict[str, FileOutput]:
    from ._files import transform_output

    if is_given(wait) and "prefer" in params:
        raise TypeError("cannot mix and match prefer and wait")

    if not is_given(wait):
        wait = True

    is_blocking = wait != False

    if wait:
        if wait is True:
            params.setdefault("prefer", "wait")
        else:
            params.setdefault("prefer", f"wait={wait}")

    # Resolve ref to its components
    version, owner, name, version_id = resolve_reference(ref)

    prediction = None
    if version_id is not None:
        # Create prediction with the specific version ID
        params_with_version: PredictionCreateParams = {**params, "version": version_id}
        prediction = await client.predictions.create(
            file_encoding_strategy=file_encoding_strategy, **params_with_version
        )
    elif owner and name:
        # Create prediction via models resource with owner/name
        prediction = await client.models.predictions.create(
            model_owner=owner, model_name=name, file_encoding_strategy=file_encoding_strategy, **params
        )
    else:
        # If ref is a string but doesn't match expected patterns
        if isinstance(ref, str):
            params_with_version = {**params, "version": ref}
            prediction = await client.predictions.create(
                file_encoding_strategy=file_encoding_strategy, **params_with_version
            )
        else:
            raise ValueError(
                f"Invalid reference format: {ref}. Expected a model name ('owner/name'), "
                "a version ID, a Model object, a Version object, or a ModelVersionIdentifier."
            )

    # Currently the "Prefer: wait" interface will return a prediction with a status
    # of "processing" rather than a terminal state because it returns before the
    # prediction has been fully processed. If request exceeds the wait time, even if
    # it is actually processing, the prediction will be in a "starting" state.
    #
    # We should fix this in the blocking API itself. Predictions that are done should
    # be in a terminal state and predictions that are processing should be in state
    # "processing".
    in_terminal_state = is_blocking and prediction.status != "starting"
    if not in_terminal_state:
        # Return a "polling" iterator if the model has an output iterator array type.
        # if version and _has_output_iterator_array_type(version):
        #     return (
        #         transform_output(chunk, client)
        #         async for chunk in prediction.async_output_iterator()
        #     )

        prediction = await client.predictions.wait(prediction.id)

    if prediction.status == "failed":
        raise ModelError(prediction)

    # Return an iterator for completed output if the model has an output iterator array type.
    if version and _has_output_iterator_array_type(version) and prediction.output is not None:
        return (transform_output(chunk, client) async for chunk in _make_async_iterator(prediction.output))  # type: ignore
    if use_file_output:
        return transform_output(prediction.output, client)  # type: ignore[no-any-return]

    return prediction.output


def _has_output_iterator_array_type(version: Version) -> bool:
    schema = make_schema_backwards_compatible(version.openapi_schema, version.cog_version)
    output = schema.get("components", {}).get("schemas", {}).get("Output", {})
    return output.get("type") == "array" and output.get("x-cog-array-type") == "iterator"  # type: ignore[no-any-return]


async def _make_async_iterator(list: List[Any]) -> AsyncIterator[Any]:
    for item in list:
        yield item


def output_iterator(prediction: Prediction, client: Replicate) -> Iterator[Any]:
    """
    Return an iterator of the prediction output.
    """

    # output can really be anything, but if we hit this then we know
    # it should be a list of something!
    if not isinstance(prediction.output, list):
        raise TypeError(f"Expected prediction output to be a list, got {type(prediction.output)}")
    previous_output: list[Any] = prediction.output or []  # type: ignore[union-attr]
    while prediction.status not in ["succeeded", "failed", "canceled"]:
        output: list[Any] = prediction.output or []  # type: ignore[union-attr]
        new_output = output[len(previous_output) :]
        yield from new_output
        previous_output = output
        time.sleep(client.poll_interval)
        prediction = client.predictions.get(prediction_id=prediction.id)

    if prediction.status == "failed":
        raise ModelError(prediction=prediction)

    output: list[Any] = prediction.output or []  # type: ignore
    new_output = output[len(previous_output) :]
    yield from new_output
