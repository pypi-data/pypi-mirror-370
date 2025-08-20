# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import TypeAlias

from .._models import BaseModel

__all__ = ["HardwareListResponse", "HardwareListResponseItem"]


class HardwareListResponseItem(BaseModel):
    name: Optional[str] = None
    """The name of the hardware."""

    sku: Optional[str] = None
    """The SKU of the hardware."""


HardwareListResponse: TypeAlias = List[HardwareListResponseItem]
