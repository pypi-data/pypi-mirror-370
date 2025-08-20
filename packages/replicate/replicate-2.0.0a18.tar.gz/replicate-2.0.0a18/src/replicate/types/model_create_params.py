# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ModelCreateParams"]


class ModelCreateParams(TypedDict, total=False):
    hardware: Required[str]
    """The SKU for the hardware used to run the model.

    Possible values can be retrieved from the `hardware.list` endpoint.
    """

    name: Required[str]
    """The name of the model.

    This must be unique among all models owned by the user or organization.
    """

    owner: Required[str]
    """The name of the user or organization that will own the model.

    This must be the same as the user or organization that is making the API
    request. In other words, the API token used in the request must belong to this
    user or organization.
    """

    visibility: Required[Literal["public", "private"]]
    """Whether the model should be public or private.

    A public model can be viewed and run by anyone, whereas a private model can be
    viewed and run only by the user or organization members that own the model.
    """

    cover_image_url: str
    """A URL for the model's cover image. This should be an image file."""

    description: str
    """A description of the model."""

    github_url: str
    """A URL for the model's source code on GitHub."""

    license_url: str
    """A URL for the model's license."""

    paper_url: str
    """A URL for the model's paper."""
