# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["BatchCreateParams", "Job", "JobPolygon"]


class BatchCreateParams(TypedDict, total=False):
    jobs: Required[Iterable[Job]]
    """List of prediction jobs"""

    metadata: Optional[Dict[str, object]]
    """Optional metadata for the batch"""

    webhook_url: Optional[str]
    """Optional webhook URL for batch completion"""

    webhook_secret: Annotated[str, PropertyInfo(alias="Webhook-Secret")]
    """Secret token for authenticating webhook callbacks.

    Required if webhook_url is provided.
    """


class JobPolygon(TypedDict, total=False):
    coordinates: Required[Iterable[Iterable[Iterable[float]]]]
    """Array of linear rings, first is exterior, rest are holes"""

    type: Literal["Polygon"]
    """GeoJSON geometry type - must be 'Polygon'"""


class Job(TypedDict, total=False):
    polygon: Required[JobPolygon]
    """GeoJSON polygon for the area"""

    year: Required[int]
    """Year for prediction"""
