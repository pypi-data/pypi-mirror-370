from __future__ import annotations

import re
from typing import Any, Dict, Tuple, Union, Optional, NamedTuple


class Model:
    """A Replicate model."""

    def __init__(self, owner: str, name: str):
        self.owner = owner
        self.name = name


import datetime

from pydantic import BaseModel


class Version(BaseModel):
    """
    A version of a model.
    """

    id: str
    """The unique ID of the version."""

    created_at: datetime.datetime
    """When the version was created."""

    cog_version: str
    """The version of the Cog used to create the version."""

    openapi_schema: Dict[str, Any]
    """An OpenAPI description of the model inputs and outputs."""


class ModelVersionIdentifier(NamedTuple):
    """
    A reference to a model version in the format owner/name or owner/name:version.
    """

    owner: str
    name: str
    version: Optional[str] = None

    @classmethod
    def parse(cls, ref: str) -> "ModelVersionIdentifier":
        """
        Split a reference in the format owner/name:version into its components.
        """

        match = re.match(r"^(?P<owner>[^/]+)/(?P<name>[^/:]+)(:(?P<version>.+))?$", ref)
        if not match:
            raise ValueError(f"Invalid reference to model version: {ref}. Expected format: owner/name:version")

        return cls(match.group("owner"), match.group("name"), match.group("version"))


def resolve_reference(
    ref: Union[Model, Version, ModelVersionIdentifier, str],
) -> Tuple[Optional[Version], Optional[str], Optional[str], Optional[str]]:
    """
    Resolve a reference to a model or version to its components.

    Returns a tuple of (version, owner, name, version_id).
    """
    version = None
    owner = None
    name = None
    version_id = None

    if isinstance(ref, Model):
        owner, name = ref.owner, ref.name
    elif isinstance(ref, Version):
        version = ref
        version_id = ref.id
    elif isinstance(ref, ModelVersionIdentifier):
        owner, name, version_id = ref
    else:
        owner, name, version_id = ModelVersionIdentifier.parse(ref)

    return version, owner, name, version_id
