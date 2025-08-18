# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ...._utils import PropertyInfo

__all__ = [
    "ActionTouchParams",
    "Point",
    "PointStart",
    "PointAction",
    "PointActionTouchPointMoveAction",
    "PointActionTouchPointWaitActionDto",
]


class ActionTouchParams(TypedDict, total=False):
    points: Required[Iterable[Point]]
    """Array of touch points and their actions"""

    include_screenshot: Annotated[bool, PropertyInfo(alias="includeScreenshot")]
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Annotated[Literal["base64", "storageKey"], PropertyInfo(alias="outputFormat")]
    """Type of the URI. default is base64."""

    presigned_expires_in: Annotated[str, PropertyInfo(alias="presignedExpiresIn")]
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Annotated[str, PropertyInfo(alias="screenshotDelay")]
    """Delay after performing the action, before taking the final screenshot.

    Execution flow:

    1. Take screenshot before action
    2. Perform the action
    3. Wait for screenshotDelay (this parameter)
    4. Take screenshot after action

    Example: '500ms' means wait 500ms after the action before capturing the final
    screenshot.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s
    """


class PointStart(TypedDict, total=False):
    x: Required[float]
    """Starting X coordinate"""

    y: Required[float]
    """Starting Y coordinate"""


class PointActionTouchPointMoveAction(TypedDict, total=False):
    duration: Required[str]
    """Duration of the movement (e.g. "200ms")

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 200ms
    """

    type: Required[str]
    """Type of the action"""

    x: Required[float]
    """Target X coordinate"""

    y: Required[float]
    """Target Y coordinate"""


class PointActionTouchPointWaitActionDto(TypedDict, total=False):
    duration: Required[str]
    """Duration to wait (e.g. "500ms")

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms
    """

    type: Required[str]
    """Type of the action"""


PointAction: TypeAlias = Union[PointActionTouchPointMoveAction, PointActionTouchPointWaitActionDto]


class Point(TypedDict, total=False):
    start: Required[PointStart]
    """Initial touch point position"""

    actions: Iterable[PointAction]
    """Sequence of actions to perform after initial touch"""
