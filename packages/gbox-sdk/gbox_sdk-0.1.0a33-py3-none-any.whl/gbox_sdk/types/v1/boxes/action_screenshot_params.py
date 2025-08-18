# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["ActionScreenshotParams", "Clip"]


class ActionScreenshotParams(TypedDict, total=False):
    clip: Clip
    """Clipping region for screenshot capture"""

    output_format: Annotated[Literal["base64", "storageKey"], PropertyInfo(alias="outputFormat")]
    """Type of the URI. default is base64."""


class Clip(TypedDict, total=False):
    height: Required[float]
    """Height of the clip"""

    width: Required[float]
    """Width of the clip"""

    x: Required[float]
    """X coordinate of the clip"""

    y: Required[float]
    """Y coordinate of the clip"""
