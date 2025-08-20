# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["PredictionListParams"]


class PredictionListParams(TypedDict, total=False):
    created_after: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """
    Include only predictions created at or after this date-time, in ISO 8601 format.
    """

    created_before: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Include only predictions created before this date-time, in ISO 8601 format."""
