# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ...._utils import PropertyInfo

__all__ = ["ActionScrollParams", "Scroll", "ScrollSimple"]


class Scroll(TypedDict, total=False):
    scroll_x: Required[Annotated[float, PropertyInfo(alias="scrollX")]]
    """Horizontal scroll amount.

    Positive values scroll content rightward (reveals content on the left), negative
    values scroll content leftward (reveals content on the right).
    """

    scroll_y: Required[Annotated[float, PropertyInfo(alias="scrollY")]]
    """Vertical scroll amount.

    Positive values scroll content downward (reveals content above), negative values
    scroll content upward (reveals content below).
    """

    x: Required[float]
    """X coordinate of the scroll position"""

    y: Required[float]
    """Y coordinate of the scroll position"""

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


class ScrollSimple(TypedDict, total=False):
    direction: Required[Literal["up", "down", "left", "right"]]
    """Direction to scroll.

    The scroll will be performed from the center of the screen towards this
    direction. 'up' scrolls content upward (reveals content below), 'down' scrolls
    content downward (reveals content above), 'left' scrolls content leftward
    (reveals content on the right), 'right' scrolls content rightward (reveals
    content on the left).
    """

    distance: Union[float, Literal["tiny", "short", "medium", "long"]]
    """Distance of the scroll.

    Can be either a number (in pixels) or a predefined enum value (tiny, short,
    medium, long). If not provided, the scroll will be performed from the center of
    the screen to the screen edge
    """

    duration: str
    """Duration of the scroll

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


ActionScrollParams: TypeAlias = Union[Scroll, ScrollSimple]
