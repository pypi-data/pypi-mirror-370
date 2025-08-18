# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = [
    "ActionAIResponse",
    "AIActionScreenshotResult",
    "AIActionScreenshotResultAIResponse",
    "AIActionScreenshotResultAIResponseAction",
    "AIActionScreenshotResultAIResponseActionTypedClickAction",
    "AIActionScreenshotResultAIResponseActionTypedTouchAction",
    "AIActionScreenshotResultAIResponseActionTypedTouchActionPoint",
    "AIActionScreenshotResultAIResponseActionTypedTouchActionPointStart",
    "AIActionScreenshotResultAIResponseActionTypedTouchActionPointAction",
    "AIActionScreenshotResultAIResponseActionTypedTouchActionPointActionTouchPointMoveAction",
    "AIActionScreenshotResultAIResponseActionTypedTouchActionPointActionTouchPointWaitActionDto",
    "AIActionScreenshotResultAIResponseActionTypedDragAdvancedAction",
    "AIActionScreenshotResultAIResponseActionTypedDragAdvancedActionPath",
    "AIActionScreenshotResultAIResponseActionTypedDragSimpleAction",
    "AIActionScreenshotResultAIResponseActionTypedDragSimpleActionEnd",
    "AIActionScreenshotResultAIResponseActionTypedDragSimpleActionEndDragPathPoint",
    "AIActionScreenshotResultAIResponseActionTypedDragSimpleActionStart",
    "AIActionScreenshotResultAIResponseActionTypedDragSimpleActionStartDragPathPoint",
    "AIActionScreenshotResultAIResponseActionTypedScrollAction",
    "AIActionScreenshotResultAIResponseActionTypedScrollSimpleAction",
    "AIActionScreenshotResultAIResponseActionTypedSwipeSimpleAction",
    "AIActionScreenshotResultAIResponseActionTypedSwipeAdvancedAction",
    "AIActionScreenshotResultAIResponseActionTypedSwipeAdvancedActionEnd",
    "AIActionScreenshotResultAIResponseActionTypedSwipeAdvancedActionEndSwipePath",
    "AIActionScreenshotResultAIResponseActionTypedSwipeAdvancedActionStart",
    "AIActionScreenshotResultAIResponseActionTypedSwipeAdvancedActionStartSwipePath",
    "AIActionScreenshotResultAIResponseActionTypedPressKeyAction",
    "AIActionScreenshotResultAIResponseActionTypedPressButtonAction",
    "AIActionScreenshotResultAIResponseActionTypedLongPressAction",
    "AIActionScreenshotResultAIResponseActionTypedTypeAction",
    "AIActionScreenshotResultAIResponseActionTypedMoveAction",
    "AIActionScreenshotResultAIResponseActionTypedScreenRotationAction",
    "AIActionScreenshotResultAIResponseActionTypedScreenshotAction",
    "AIActionScreenshotResultAIResponseActionTypedScreenshotActionClip",
    "AIActionScreenshotResultAIResponseActionTypedWaitAction",
    "AIActionScreenshotResultScreenshot",
    "AIActionScreenshotResultScreenshotAfter",
    "AIActionScreenshotResultScreenshotBefore",
    "AIActionScreenshotResultScreenshotTrace",
    "AIActionResult",
    "AIActionResultAIResponse",
    "AIActionResultAIResponseAction",
    "AIActionResultAIResponseActionTypedClickAction",
    "AIActionResultAIResponseActionTypedTouchAction",
    "AIActionResultAIResponseActionTypedTouchActionPoint",
    "AIActionResultAIResponseActionTypedTouchActionPointStart",
    "AIActionResultAIResponseActionTypedTouchActionPointAction",
    "AIActionResultAIResponseActionTypedTouchActionPointActionTouchPointMoveAction",
    "AIActionResultAIResponseActionTypedTouchActionPointActionTouchPointWaitActionDto",
    "AIActionResultAIResponseActionTypedDragAdvancedAction",
    "AIActionResultAIResponseActionTypedDragAdvancedActionPath",
    "AIActionResultAIResponseActionTypedDragSimpleAction",
    "AIActionResultAIResponseActionTypedDragSimpleActionEnd",
    "AIActionResultAIResponseActionTypedDragSimpleActionEndDragPathPoint",
    "AIActionResultAIResponseActionTypedDragSimpleActionStart",
    "AIActionResultAIResponseActionTypedDragSimpleActionStartDragPathPoint",
    "AIActionResultAIResponseActionTypedScrollAction",
    "AIActionResultAIResponseActionTypedScrollSimpleAction",
    "AIActionResultAIResponseActionTypedSwipeSimpleAction",
    "AIActionResultAIResponseActionTypedSwipeAdvancedAction",
    "AIActionResultAIResponseActionTypedSwipeAdvancedActionEnd",
    "AIActionResultAIResponseActionTypedSwipeAdvancedActionEndSwipePath",
    "AIActionResultAIResponseActionTypedSwipeAdvancedActionStart",
    "AIActionResultAIResponseActionTypedSwipeAdvancedActionStartSwipePath",
    "AIActionResultAIResponseActionTypedPressKeyAction",
    "AIActionResultAIResponseActionTypedPressButtonAction",
    "AIActionResultAIResponseActionTypedLongPressAction",
    "AIActionResultAIResponseActionTypedTypeAction",
    "AIActionResultAIResponseActionTypedMoveAction",
    "AIActionResultAIResponseActionTypedScreenRotationAction",
    "AIActionResultAIResponseActionTypedScreenshotAction",
    "AIActionResultAIResponseActionTypedScreenshotActionClip",
    "AIActionResultAIResponseActionTypedWaitAction",
]


class AIActionScreenshotResultAIResponseActionTypedClickAction(BaseModel):
    x: float
    """X coordinate of the click"""

    y: float
    """Y coordinate of the click"""

    button: Optional[Literal["left", "right", "middle"]] = None
    """Mouse button to click"""

    double: Optional[bool] = None
    """Whether to perform a double click"""

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionScreenshotResultAIResponseActionTypedTouchActionPointStart(BaseModel):
    x: float
    """Starting X coordinate"""

    y: float
    """Starting Y coordinate"""


class AIActionScreenshotResultAIResponseActionTypedTouchActionPointActionTouchPointMoveAction(BaseModel):
    duration: str
    """Duration of the movement (e.g. "200ms")

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 200ms
    """

    type: str
    """Type of the action"""

    x: float
    """Target X coordinate"""

    y: float
    """Target Y coordinate"""


class AIActionScreenshotResultAIResponseActionTypedTouchActionPointActionTouchPointWaitActionDto(BaseModel):
    duration: str
    """Duration to wait (e.g. "500ms")

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms
    """

    type: str
    """Type of the action"""


AIActionScreenshotResultAIResponseActionTypedTouchActionPointAction: TypeAlias = Union[
    AIActionScreenshotResultAIResponseActionTypedTouchActionPointActionTouchPointMoveAction,
    AIActionScreenshotResultAIResponseActionTypedTouchActionPointActionTouchPointWaitActionDto,
]


class AIActionScreenshotResultAIResponseActionTypedTouchActionPoint(BaseModel):
    start: AIActionScreenshotResultAIResponseActionTypedTouchActionPointStart
    """Initial touch point position"""

    actions: Optional[List[AIActionScreenshotResultAIResponseActionTypedTouchActionPointAction]] = None
    """Sequence of actions to perform after initial touch"""


class AIActionScreenshotResultAIResponseActionTypedTouchAction(BaseModel):
    points: List[AIActionScreenshotResultAIResponseActionTypedTouchActionPoint]
    """Array of touch points and their actions"""

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionScreenshotResultAIResponseActionTypedDragAdvancedActionPath(BaseModel):
    x: float
    """X coordinate of a point in the drag path"""

    y: float
    """Y coordinate of a point in the drag path"""


class AIActionScreenshotResultAIResponseActionTypedDragAdvancedAction(BaseModel):
    path: List[AIActionScreenshotResultAIResponseActionTypedDragAdvancedActionPath]
    """Path of the drag action as a series of coordinates"""

    duration: Optional[str] = None
    """Time interval between points (e.g. "50ms")

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 50ms
    """

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionScreenshotResultAIResponseActionTypedDragSimpleActionEndDragPathPoint(BaseModel):
    x: float
    """X coordinate of a point in the drag path"""

    y: float
    """Y coordinate of a point in the drag path"""


AIActionScreenshotResultAIResponseActionTypedDragSimpleActionEnd: TypeAlias = Union[
    AIActionScreenshotResultAIResponseActionTypedDragSimpleActionEndDragPathPoint, str
]


class AIActionScreenshotResultAIResponseActionTypedDragSimpleActionStartDragPathPoint(BaseModel):
    x: float
    """X coordinate of a point in the drag path"""

    y: float
    """Y coordinate of a point in the drag path"""


AIActionScreenshotResultAIResponseActionTypedDragSimpleActionStart: TypeAlias = Union[
    AIActionScreenshotResultAIResponseActionTypedDragSimpleActionStartDragPathPoint, str
]


class AIActionScreenshotResultAIResponseActionTypedDragSimpleAction(BaseModel):
    end: AIActionScreenshotResultAIResponseActionTypedDragSimpleActionEnd
    """End point of the drag path (coordinates or natural language)"""

    start: AIActionScreenshotResultAIResponseActionTypedDragSimpleActionStart
    """Start point of the drag path (coordinates or natural language)"""

    duration: Optional[str] = None
    """Duration to complete the movement from start to end coordinates

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms
    """

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionScreenshotResultAIResponseActionTypedScrollAction(BaseModel):
    scroll_x: float = FieldInfo(alias="scrollX")
    """Horizontal scroll amount.

    Positive values scroll content rightward (reveals content on the left), negative
    values scroll content leftward (reveals content on the right).
    """

    scroll_y: float = FieldInfo(alias="scrollY")
    """Vertical scroll amount.

    Positive values scroll content downward (reveals content above), negative values
    scroll content upward (reveals content below).
    """

    x: float
    """X coordinate of the scroll position"""

    y: float
    """Y coordinate of the scroll position"""

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionScreenshotResultAIResponseActionTypedScrollSimpleAction(BaseModel):
    direction: Literal["up", "down", "left", "right"]
    """Direction to scroll.

    The scroll will be performed from the center of the screen towards this
    direction. 'up' scrolls content upward (reveals content below), 'down' scrolls
    content downward (reveals content above), 'left' scrolls content leftward
    (reveals content on the right), 'right' scrolls content rightward (reveals
    content on the left).
    """

    distance: Union[float, Literal["tiny", "short", "medium", "long"], None] = None
    """Distance of the scroll.

    Can be either a number (in pixels) or a predefined enum value (tiny, short,
    medium, long). If not provided, the scroll will be performed from the center of
    the screen to the screen edge
    """

    duration: Optional[str] = None
    """Duration of the scroll

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms
    """

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionScreenshotResultAIResponseActionTypedSwipeSimpleAction(BaseModel):
    direction: Literal["up", "down", "left", "right", "upLeft", "upRight", "downLeft", "downRight"]
    """Direction to swipe.

    The gesture will be performed from the center of the screen towards this
    direction.
    """

    distance: Union[float, Literal["tiny", "short", "medium", "long"], None] = None
    """Distance of the swipe.

    Can be either a number (in pixels) or a predefined enum value (tiny, short,
    medium, long). If not provided, the swipe will be performed from the center of
    the screen to the screen edge
    """

    duration: Optional[str] = None
    """Duration of the swipe

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms
    """

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    location: Optional[str] = None
    """Natural language description of the location where the swipe should originate.

    If not provided, the swipe will be performed from the center of the screen.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionScreenshotResultAIResponseActionTypedSwipeAdvancedActionEndSwipePath(BaseModel):
    x: float
    """Start/end x coordinate of the swipe path"""

    y: float
    """Start/end y coordinate of the swipe path"""


AIActionScreenshotResultAIResponseActionTypedSwipeAdvancedActionEnd: TypeAlias = Union[
    AIActionScreenshotResultAIResponseActionTypedSwipeAdvancedActionEndSwipePath, str
]


class AIActionScreenshotResultAIResponseActionTypedSwipeAdvancedActionStartSwipePath(BaseModel):
    x: float
    """Start/end x coordinate of the swipe path"""

    y: float
    """Start/end y coordinate of the swipe path"""


AIActionScreenshotResultAIResponseActionTypedSwipeAdvancedActionStart: TypeAlias = Union[
    AIActionScreenshotResultAIResponseActionTypedSwipeAdvancedActionStartSwipePath, str
]


class AIActionScreenshotResultAIResponseActionTypedSwipeAdvancedAction(BaseModel):
    end: AIActionScreenshotResultAIResponseActionTypedSwipeAdvancedActionEnd
    """End point of the swipe path (coordinates or natural language)"""

    start: AIActionScreenshotResultAIResponseActionTypedSwipeAdvancedActionStart
    """Start point of the swipe path (coordinates or natural language)"""

    duration: Optional[str] = None
    """Duration of the swipe

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms
    """

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionScreenshotResultAIResponseActionTypedPressKeyAction(BaseModel):
    keys: List[
        Literal[
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "w",
            "x",
            "y",
            "z",
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "f1",
            "f2",
            "f3",
            "f4",
            "f5",
            "f6",
            "f7",
            "f8",
            "f9",
            "f10",
            "f11",
            "f12",
            "control",
            "alt",
            "shift",
            "meta",
            "win",
            "cmd",
            "option",
            "arrowUp",
            "arrowDown",
            "arrowLeft",
            "arrowRight",
            "home",
            "end",
            "pageUp",
            "pageDown",
            "enter",
            "space",
            "tab",
            "escape",
            "backspace",
            "delete",
            "insert",
            "capsLock",
            "numLock",
            "scrollLock",
            "pause",
            "printScreen",
            ";",
            "=",
            ",",
            "-",
            ".",
            "/",
            "`",
            "[",
            "\\",
            "]",
            "'",
            "numpad0",
            "numpad1",
            "numpad2",
            "numpad3",
            "numpad4",
            "numpad5",
            "numpad6",
            "numpad7",
            "numpad8",
            "numpad9",
            "numpadAdd",
            "numpadSubtract",
            "numpadMultiply",
            "numpadDivide",
            "numpadDecimal",
            "numpadEnter",
            "numpadEqual",
            "volumeUp",
            "volumeDown",
            "volumeMute",
            "mediaPlayPause",
            "mediaStop",
            "mediaNextTrack",
            "mediaPreviousTrack",
        ]
    ]
    """This is an array of keyboard keys to press.

    Supports cross-platform compatibility.
    """

    combination: Optional[bool] = None
    """Whether to press keys as combination (simultaneously) or sequentially.

    When true, all keys are pressed together as a shortcut (e.g., Ctrl+C). When
    false, keys are pressed one by one in sequence.
    """

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionScreenshotResultAIResponseActionTypedPressButtonAction(BaseModel):
    buttons: List[Literal["power", "volumeUp", "volumeDown", "volumeMute", "home", "back", "menu", "appSwitch"]]
    """Button to press"""

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionScreenshotResultAIResponseActionTypedLongPressAction(BaseModel):
    x: float
    """X coordinate of the long press"""

    y: float
    """Y coordinate of the long press"""

    duration: Optional[str] = None
    """Duration to hold the press (e.g. '1s', '500ms')

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 1s
    """

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionScreenshotResultAIResponseActionTypedTypeAction(BaseModel):
    text: str
    """Text to type"""

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    mode: Optional[Literal["append", "replace"]] = None
    """
    Text input mode: 'append' to add text to existing content, 'replace' to replace
    all existing text
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    press_enter: Optional[bool] = FieldInfo(alias="pressEnter", default=None)
    """Whether to press Enter after typing the text"""

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionScreenshotResultAIResponseActionTypedMoveAction(BaseModel):
    x: float
    """X coordinate to move to"""

    y: float
    """Y coordinate to move to"""

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionScreenshotResultAIResponseActionTypedScreenRotationAction(BaseModel):
    orientation: Literal["portrait", "landscapeLeft", "portraitUpsideDown", "landscapeRight"]
    """Target screen orientation"""

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionScreenshotResultAIResponseActionTypedScreenshotActionClip(BaseModel):
    height: float
    """Height of the clip"""

    width: float
    """Width of the clip"""

    x: float
    """X coordinate of the clip"""

    y: float
    """Y coordinate of the clip"""


class AIActionScreenshotResultAIResponseActionTypedScreenshotAction(BaseModel):
    clip: Optional[AIActionScreenshotResultAIResponseActionTypedScreenshotActionClip] = None
    """Clipping region for screenshot capture"""

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""


class AIActionScreenshotResultAIResponseActionTypedWaitAction(BaseModel):
    duration: str
    """Duration of the wait (e.g. '3s')

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 3s
    """

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


AIActionScreenshotResultAIResponseAction: TypeAlias = Union[
    AIActionScreenshotResultAIResponseActionTypedClickAction,
    AIActionScreenshotResultAIResponseActionTypedTouchAction,
    AIActionScreenshotResultAIResponseActionTypedDragAdvancedAction,
    AIActionScreenshotResultAIResponseActionTypedDragSimpleAction,
    AIActionScreenshotResultAIResponseActionTypedScrollAction,
    AIActionScreenshotResultAIResponseActionTypedScrollSimpleAction,
    AIActionScreenshotResultAIResponseActionTypedSwipeSimpleAction,
    AIActionScreenshotResultAIResponseActionTypedSwipeAdvancedAction,
    AIActionScreenshotResultAIResponseActionTypedPressKeyAction,
    AIActionScreenshotResultAIResponseActionTypedPressButtonAction,
    AIActionScreenshotResultAIResponseActionTypedLongPressAction,
    AIActionScreenshotResultAIResponseActionTypedTypeAction,
    AIActionScreenshotResultAIResponseActionTypedMoveAction,
    AIActionScreenshotResultAIResponseActionTypedScreenRotationAction,
    AIActionScreenshotResultAIResponseActionTypedScreenshotAction,
    AIActionScreenshotResultAIResponseActionTypedDragSimpleAction,
    AIActionScreenshotResultAIResponseActionTypedDragAdvancedAction,
    AIActionScreenshotResultAIResponseActionTypedWaitAction,
]


class AIActionScreenshotResultAIResponse(BaseModel):
    actions: List[AIActionScreenshotResultAIResponseAction]
    """Actions to be executed by the AI with type identifier"""

    messages: List[str]
    """messages returned by the model"""

    model: str
    """The name of the model that processed this request"""

    reasoning: Optional[str] = None
    """reasoning"""


class AIActionScreenshotResultScreenshotAfter(BaseModel):
    uri: str
    """URI of the screenshot after the action"""

    presigned_url: Optional[str] = FieldInfo(alias="presignedUrl", default=None)
    """Presigned url of the screenshot before the action"""


class AIActionScreenshotResultScreenshotBefore(BaseModel):
    uri: str
    """URI of the screenshot before the action"""

    presigned_url: Optional[str] = FieldInfo(alias="presignedUrl", default=None)
    """Presigned url of the screenshot before the action"""


class AIActionScreenshotResultScreenshotTrace(BaseModel):
    uri: str
    """URI of the screenshot with operation trace"""


class AIActionScreenshotResultScreenshot(BaseModel):
    after: AIActionScreenshotResultScreenshotAfter
    """Screenshot taken after action execution"""

    before: AIActionScreenshotResultScreenshotBefore
    """Screenshot taken before action execution"""

    trace: AIActionScreenshotResultScreenshotTrace
    """Screenshot with action operation trace"""


class AIActionScreenshotResult(BaseModel):
    ai_response: AIActionScreenshotResultAIResponse = FieldInfo(alias="aiResponse")
    """Response of AI action execution"""

    output: str
    """output"""

    screenshot: AIActionScreenshotResultScreenshot
    """Complete screenshot result with operation trace, before and after images"""


class AIActionResultAIResponseActionTypedClickAction(BaseModel):
    x: float
    """X coordinate of the click"""

    y: float
    """Y coordinate of the click"""

    button: Optional[Literal["left", "right", "middle"]] = None
    """Mouse button to click"""

    double: Optional[bool] = None
    """Whether to perform a double click"""

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionResultAIResponseActionTypedTouchActionPointStart(BaseModel):
    x: float
    """Starting X coordinate"""

    y: float
    """Starting Y coordinate"""


class AIActionResultAIResponseActionTypedTouchActionPointActionTouchPointMoveAction(BaseModel):
    duration: str
    """Duration of the movement (e.g. "200ms")

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 200ms
    """

    type: str
    """Type of the action"""

    x: float
    """Target X coordinate"""

    y: float
    """Target Y coordinate"""


class AIActionResultAIResponseActionTypedTouchActionPointActionTouchPointWaitActionDto(BaseModel):
    duration: str
    """Duration to wait (e.g. "500ms")

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms
    """

    type: str
    """Type of the action"""


AIActionResultAIResponseActionTypedTouchActionPointAction: TypeAlias = Union[
    AIActionResultAIResponseActionTypedTouchActionPointActionTouchPointMoveAction,
    AIActionResultAIResponseActionTypedTouchActionPointActionTouchPointWaitActionDto,
]


class AIActionResultAIResponseActionTypedTouchActionPoint(BaseModel):
    start: AIActionResultAIResponseActionTypedTouchActionPointStart
    """Initial touch point position"""

    actions: Optional[List[AIActionResultAIResponseActionTypedTouchActionPointAction]] = None
    """Sequence of actions to perform after initial touch"""


class AIActionResultAIResponseActionTypedTouchAction(BaseModel):
    points: List[AIActionResultAIResponseActionTypedTouchActionPoint]
    """Array of touch points and their actions"""

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionResultAIResponseActionTypedDragAdvancedActionPath(BaseModel):
    x: float
    """X coordinate of a point in the drag path"""

    y: float
    """Y coordinate of a point in the drag path"""


class AIActionResultAIResponseActionTypedDragAdvancedAction(BaseModel):
    path: List[AIActionResultAIResponseActionTypedDragAdvancedActionPath]
    """Path of the drag action as a series of coordinates"""

    duration: Optional[str] = None
    """Time interval between points (e.g. "50ms")

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 50ms
    """

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionResultAIResponseActionTypedDragSimpleActionEndDragPathPoint(BaseModel):
    x: float
    """X coordinate of a point in the drag path"""

    y: float
    """Y coordinate of a point in the drag path"""


AIActionResultAIResponseActionTypedDragSimpleActionEnd: TypeAlias = Union[
    AIActionResultAIResponseActionTypedDragSimpleActionEndDragPathPoint, str
]


class AIActionResultAIResponseActionTypedDragSimpleActionStartDragPathPoint(BaseModel):
    x: float
    """X coordinate of a point in the drag path"""

    y: float
    """Y coordinate of a point in the drag path"""


AIActionResultAIResponseActionTypedDragSimpleActionStart: TypeAlias = Union[
    AIActionResultAIResponseActionTypedDragSimpleActionStartDragPathPoint, str
]


class AIActionResultAIResponseActionTypedDragSimpleAction(BaseModel):
    end: AIActionResultAIResponseActionTypedDragSimpleActionEnd
    """End point of the drag path (coordinates or natural language)"""

    start: AIActionResultAIResponseActionTypedDragSimpleActionStart
    """Start point of the drag path (coordinates or natural language)"""

    duration: Optional[str] = None
    """Duration to complete the movement from start to end coordinates

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms
    """

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionResultAIResponseActionTypedScrollAction(BaseModel):
    scroll_x: float = FieldInfo(alias="scrollX")
    """Horizontal scroll amount.

    Positive values scroll content rightward (reveals content on the left), negative
    values scroll content leftward (reveals content on the right).
    """

    scroll_y: float = FieldInfo(alias="scrollY")
    """Vertical scroll amount.

    Positive values scroll content downward (reveals content above), negative values
    scroll content upward (reveals content below).
    """

    x: float
    """X coordinate of the scroll position"""

    y: float
    """Y coordinate of the scroll position"""

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionResultAIResponseActionTypedScrollSimpleAction(BaseModel):
    direction: Literal["up", "down", "left", "right"]
    """Direction to scroll.

    The scroll will be performed from the center of the screen towards this
    direction. 'up' scrolls content upward (reveals content below), 'down' scrolls
    content downward (reveals content above), 'left' scrolls content leftward
    (reveals content on the right), 'right' scrolls content rightward (reveals
    content on the left).
    """

    distance: Union[float, Literal["tiny", "short", "medium", "long"], None] = None
    """Distance of the scroll.

    Can be either a number (in pixels) or a predefined enum value (tiny, short,
    medium, long). If not provided, the scroll will be performed from the center of
    the screen to the screen edge
    """

    duration: Optional[str] = None
    """Duration of the scroll

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms
    """

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionResultAIResponseActionTypedSwipeSimpleAction(BaseModel):
    direction: Literal["up", "down", "left", "right", "upLeft", "upRight", "downLeft", "downRight"]
    """Direction to swipe.

    The gesture will be performed from the center of the screen towards this
    direction.
    """

    distance: Union[float, Literal["tiny", "short", "medium", "long"], None] = None
    """Distance of the swipe.

    Can be either a number (in pixels) or a predefined enum value (tiny, short,
    medium, long). If not provided, the swipe will be performed from the center of
    the screen to the screen edge
    """

    duration: Optional[str] = None
    """Duration of the swipe

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms
    """

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    location: Optional[str] = None
    """Natural language description of the location where the swipe should originate.

    If not provided, the swipe will be performed from the center of the screen.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionResultAIResponseActionTypedSwipeAdvancedActionEndSwipePath(BaseModel):
    x: float
    """Start/end x coordinate of the swipe path"""

    y: float
    """Start/end y coordinate of the swipe path"""


AIActionResultAIResponseActionTypedSwipeAdvancedActionEnd: TypeAlias = Union[
    AIActionResultAIResponseActionTypedSwipeAdvancedActionEndSwipePath, str
]


class AIActionResultAIResponseActionTypedSwipeAdvancedActionStartSwipePath(BaseModel):
    x: float
    """Start/end x coordinate of the swipe path"""

    y: float
    """Start/end y coordinate of the swipe path"""


AIActionResultAIResponseActionTypedSwipeAdvancedActionStart: TypeAlias = Union[
    AIActionResultAIResponseActionTypedSwipeAdvancedActionStartSwipePath, str
]


class AIActionResultAIResponseActionTypedSwipeAdvancedAction(BaseModel):
    end: AIActionResultAIResponseActionTypedSwipeAdvancedActionEnd
    """End point of the swipe path (coordinates or natural language)"""

    start: AIActionResultAIResponseActionTypedSwipeAdvancedActionStart
    """Start point of the swipe path (coordinates or natural language)"""

    duration: Optional[str] = None
    """Duration of the swipe

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms
    """

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionResultAIResponseActionTypedPressKeyAction(BaseModel):
    keys: List[
        Literal[
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "w",
            "x",
            "y",
            "z",
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "f1",
            "f2",
            "f3",
            "f4",
            "f5",
            "f6",
            "f7",
            "f8",
            "f9",
            "f10",
            "f11",
            "f12",
            "control",
            "alt",
            "shift",
            "meta",
            "win",
            "cmd",
            "option",
            "arrowUp",
            "arrowDown",
            "arrowLeft",
            "arrowRight",
            "home",
            "end",
            "pageUp",
            "pageDown",
            "enter",
            "space",
            "tab",
            "escape",
            "backspace",
            "delete",
            "insert",
            "capsLock",
            "numLock",
            "scrollLock",
            "pause",
            "printScreen",
            ";",
            "=",
            ",",
            "-",
            ".",
            "/",
            "`",
            "[",
            "\\",
            "]",
            "'",
            "numpad0",
            "numpad1",
            "numpad2",
            "numpad3",
            "numpad4",
            "numpad5",
            "numpad6",
            "numpad7",
            "numpad8",
            "numpad9",
            "numpadAdd",
            "numpadSubtract",
            "numpadMultiply",
            "numpadDivide",
            "numpadDecimal",
            "numpadEnter",
            "numpadEqual",
            "volumeUp",
            "volumeDown",
            "volumeMute",
            "mediaPlayPause",
            "mediaStop",
            "mediaNextTrack",
            "mediaPreviousTrack",
        ]
    ]
    """This is an array of keyboard keys to press.

    Supports cross-platform compatibility.
    """

    combination: Optional[bool] = None
    """Whether to press keys as combination (simultaneously) or sequentially.

    When true, all keys are pressed together as a shortcut (e.g., Ctrl+C). When
    false, keys are pressed one by one in sequence.
    """

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionResultAIResponseActionTypedPressButtonAction(BaseModel):
    buttons: List[Literal["power", "volumeUp", "volumeDown", "volumeMute", "home", "back", "menu", "appSwitch"]]
    """Button to press"""

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionResultAIResponseActionTypedLongPressAction(BaseModel):
    x: float
    """X coordinate of the long press"""

    y: float
    """Y coordinate of the long press"""

    duration: Optional[str] = None
    """Duration to hold the press (e.g. '1s', '500ms')

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 1s
    """

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionResultAIResponseActionTypedTypeAction(BaseModel):
    text: str
    """Text to type"""

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    mode: Optional[Literal["append", "replace"]] = None
    """
    Text input mode: 'append' to add text to existing content, 'replace' to replace
    all existing text
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    press_enter: Optional[bool] = FieldInfo(alias="pressEnter", default=None)
    """Whether to press Enter after typing the text"""

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionResultAIResponseActionTypedMoveAction(BaseModel):
    x: float
    """X coordinate to move to"""

    y: float
    """Y coordinate to move to"""

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionResultAIResponseActionTypedScreenRotationAction(BaseModel):
    orientation: Literal["portrait", "landscapeLeft", "portraitUpsideDown", "landscapeRight"]
    """Target screen orientation"""

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


class AIActionResultAIResponseActionTypedScreenshotActionClip(BaseModel):
    height: float
    """Height of the clip"""

    width: float
    """Width of the clip"""

    x: float
    """X coordinate of the clip"""

    y: float
    """Y coordinate of the clip"""


class AIActionResultAIResponseActionTypedScreenshotAction(BaseModel):
    clip: Optional[AIActionResultAIResponseActionTypedScreenshotActionClip] = None
    """Clipping region for screenshot capture"""

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""


class AIActionResultAIResponseActionTypedWaitAction(BaseModel):
    duration: str
    """Duration of the wait (e.g. '3s')

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 3s
    """

    include_screenshot: Optional[bool] = FieldInfo(alias="includeScreenshot", default=None)
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Optional[str] = FieldInfo(alias="screenshotDelay", default=None)
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


AIActionResultAIResponseAction: TypeAlias = Union[
    AIActionResultAIResponseActionTypedClickAction,
    AIActionResultAIResponseActionTypedTouchAction,
    AIActionResultAIResponseActionTypedDragAdvancedAction,
    AIActionResultAIResponseActionTypedDragSimpleAction,
    AIActionResultAIResponseActionTypedScrollAction,
    AIActionResultAIResponseActionTypedScrollSimpleAction,
    AIActionResultAIResponseActionTypedSwipeSimpleAction,
    AIActionResultAIResponseActionTypedSwipeAdvancedAction,
    AIActionResultAIResponseActionTypedPressKeyAction,
    AIActionResultAIResponseActionTypedPressButtonAction,
    AIActionResultAIResponseActionTypedLongPressAction,
    AIActionResultAIResponseActionTypedTypeAction,
    AIActionResultAIResponseActionTypedMoveAction,
    AIActionResultAIResponseActionTypedScreenRotationAction,
    AIActionResultAIResponseActionTypedScreenshotAction,
    AIActionResultAIResponseActionTypedDragSimpleAction,
    AIActionResultAIResponseActionTypedDragAdvancedAction,
    AIActionResultAIResponseActionTypedWaitAction,
]


class AIActionResultAIResponse(BaseModel):
    actions: List[AIActionResultAIResponseAction]
    """Actions to be executed by the AI with type identifier"""

    messages: List[str]
    """messages returned by the model"""

    model: str
    """The name of the model that processed this request"""

    reasoning: Optional[str] = None
    """reasoning"""


class AIActionResult(BaseModel):
    ai_response: AIActionResultAIResponse = FieldInfo(alias="aiResponse")
    """Response of AI action execution"""

    output: str
    """output"""


ActionAIResponse: TypeAlias = Union[AIActionScreenshotResult, AIActionResult]
