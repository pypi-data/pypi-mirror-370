# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["TrainingListResponse", "Metrics", "Output", "URLs"]


class Metrics(BaseModel):
    predict_time: Optional[float] = None
    """The amount of CPU or GPU time, in seconds, that the training used while running"""


class Output(BaseModel):
    version: Optional[str] = None
    """The version of the model created by the training"""

    weights: Optional[str] = None
    """The weights of the trained model"""


class URLs(BaseModel):
    cancel: Optional[str] = None
    """URL to cancel the training"""

    get: Optional[str] = None
    """URL to get the training details"""


class TrainingListResponse(BaseModel):
    id: Optional[str] = None
    """The unique ID of the training"""

    completed_at: Optional[datetime] = None
    """The time when the training completed"""

    created_at: Optional[datetime] = None
    """The time when the training was created"""

    error: Optional[str] = None
    """Error message if the training failed"""

    input: Optional[Dict[str, object]] = None
    """The input parameters used for the training"""

    logs: Optional[str] = None
    """The logs from the training process"""

    metrics: Optional[Metrics] = None
    """Metrics about the training process"""

    model: Optional[str] = None
    """The name of the model in the format owner/name"""

    output: Optional[Output] = None
    """The output of the training process"""

    source: Optional[Literal["web", "api"]] = None
    """How the training was created"""

    started_at: Optional[datetime] = None
    """The time when the training started"""

    status: Optional[Literal["starting", "processing", "succeeded", "failed", "canceled"]] = None
    """The current status of the training"""

    urls: Optional[URLs] = None
    """URLs for interacting with the training"""

    version: Optional[str] = None
    """The ID of the model version used for training"""
