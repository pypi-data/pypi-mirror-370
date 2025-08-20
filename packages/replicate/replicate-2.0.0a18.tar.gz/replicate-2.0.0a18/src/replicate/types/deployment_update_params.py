# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["DeploymentUpdateParams"]


class DeploymentUpdateParams(TypedDict, total=False):
    deployment_owner: Required[str]

    deployment_name: Required[str]

    hardware: str
    """The SKU for the hardware used to run the model.

    Possible values can be retrieved from the `hardware.list` endpoint.
    """

    max_instances: int
    """The maximum number of instances for scaling."""

    min_instances: int
    """The minimum number of instances for scaling."""

    version: str
    """The ID of the model version that you want to deploy"""
