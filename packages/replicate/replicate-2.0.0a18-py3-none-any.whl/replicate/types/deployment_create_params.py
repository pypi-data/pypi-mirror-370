# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["DeploymentCreateParams"]


class DeploymentCreateParams(TypedDict, total=False):
    hardware: Required[str]
    """The SKU for the hardware used to run the model.

    Possible values can be retrieved from the `hardware.list` endpoint.
    """

    max_instances: Required[int]
    """The maximum number of instances for scaling."""

    min_instances: Required[int]
    """The minimum number of instances for scaling."""

    model: Required[str]
    """The full name of the model that you want to deploy e.g. stability-ai/sdxl."""

    name: Required[str]
    """The name of the deployment."""

    version: Required[str]
    """The 64-character string ID of the model version that you want to deploy."""
