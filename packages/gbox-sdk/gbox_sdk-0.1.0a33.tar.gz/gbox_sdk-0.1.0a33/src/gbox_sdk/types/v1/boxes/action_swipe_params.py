# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ...._utils import PropertyInfo

__all__ = [
    "ActionSwipeParams",
    "SwipeSimple",
    "SwipeAdvanced",
    "SwipeAdvancedEnd",
    "SwipeAdvancedEndSwipePath",
    "SwipeAdvancedStart",
    "SwipeAdvancedStartSwipePath",
]


class SwipeSimple(TypedDict, total=False):
    direction: Required[Literal["up", "down", "left", "right", "upLeft", "upRight", "downLeft", "downRight"]]
    """Direction to swipe.

    The gesture will be performed from the center of the screen towards this
    direction.
    """

    distance: Union[float, Literal["tiny", "short", "medium", "long"]]
    """Distance of the swipe.

    Can be either a number (in pixels) or a predefined enum value (tiny, short,
    medium, long). If not provided, the swipe will be performed from the center of
    the screen to the screen edge
    """

    duration: str
    """Duration of the swipe

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms
    """

    include_screenshot: Annotated[bool, PropertyInfo(alias="includeScreenshot")]
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    location: str
    """Natural language description of the location where the swipe should originate.

    If not provided, the swipe will be performed from the center of the screen.
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


class SwipeAdvanced(TypedDict, total=False):
    end: Required[SwipeAdvancedEnd]
    """End point of the swipe path (coordinates or natural language)"""

    start: Required[SwipeAdvancedStart]
    """Start point of the swipe path (coordinates or natural language)"""

    duration: str
    """Duration of the swipe

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms
    """

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


class SwipeAdvancedEndSwipePath(TypedDict, total=False):
    x: Required[float]
    """Start/end x coordinate of the swipe path"""

    y: Required[float]
    """Start/end y coordinate of the swipe path"""


SwipeAdvancedEnd: TypeAlias = Union[SwipeAdvancedEndSwipePath, str]


class SwipeAdvancedStartSwipePath(TypedDict, total=False):
    x: Required[float]
    """Start/end x coordinate of the swipe path"""

    y: Required[float]
    """Start/end y coordinate of the swipe path"""


SwipeAdvancedStart: TypeAlias = Union[SwipeAdvancedStartSwipePath, str]

ActionSwipeParams: TypeAlias = Union[SwipeSimple, SwipeAdvanced]
