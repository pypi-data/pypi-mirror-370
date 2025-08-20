# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["DeploymentListResponse", "CurrentRelease", "CurrentReleaseConfiguration", "CurrentReleaseCreatedBy"]


class CurrentReleaseConfiguration(BaseModel):
    hardware: Optional[str] = None
    """The SKU for the hardware used to run the model."""

    max_instances: Optional[int] = None
    """The maximum number of instances for scaling."""

    min_instances: Optional[int] = None
    """The minimum number of instances for scaling."""


class CurrentReleaseCreatedBy(BaseModel):
    type: Literal["organization", "user"]
    """The account type of the creator. Can be a user or an organization."""

    username: str
    """The username of the account that created the release."""

    avatar_url: Optional[str] = None
    """The avatar URL for the account that created the release."""

    github_url: Optional[str] = None
    """The GitHub URL of the account that created the release."""

    name: Optional[str] = None
    """The name of the account that created the release."""


class CurrentRelease(BaseModel):
    configuration: Optional[CurrentReleaseConfiguration] = None

    created_at: Optional[datetime] = None
    """The time the release was created."""

    created_by: Optional[CurrentReleaseCreatedBy] = None

    model: Optional[str] = None
    """The model identifier string in the format of `{model_owner}/{model_name}`."""

    number: Optional[int] = None
    """The release number."""

    version: Optional[str] = None
    """The ID of the model version used in the release."""


class DeploymentListResponse(BaseModel):
    current_release: Optional[CurrentRelease] = None

    name: Optional[str] = None
    """The name of the deployment."""

    owner: Optional[str] = None
    """The owner of the deployment."""
