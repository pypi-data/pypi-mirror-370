# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["ActionAIParams", "Settings"]


class ActionAIParams(TypedDict, total=False):
    instruction: Required[str]
    """
    Direct instruction of the UI action to perform (e.g., 'click the login button',
    'input username in the email field', 'scroll down', 'swipe left')
    """

    background: str
    """The background of the UI action to perform.

    The purpose of background is to let the action executor to understand the
    context of why the instruction is given including important previous actions and
    observations
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

    settings: Settings
    """AI action settings"""

    stream: bool
    """Whether to stream progress events using Server-Sent Events (SSE).

    When true, the API returns an event stream. When false or omitted, the API
    returns a normal JSON response.
    """


class Settings(TypedDict, total=False):
    disable_actions: Annotated[List[str], PropertyInfo(alias="disableActions")]
    """Whether disable actions"""

    system_prompt: Annotated[str, PropertyInfo(alias="systemPrompt")]
    """
    System prompt that defines the AI's behavior and capabilities when executing UI
    actions. This prompt instructs the AI on how to interpret the screen, understand
    user instructions, and determine the appropriate UI actions to take. A
    well-crafted system prompt can significantly improve the accuracy and
    reliability of AI-driven UI automation. If not provided, uses the default
    computer use instruction template that includes basic screen interaction
    guidelines.
    """
