import os
import json
import base64
from typing import List, Union, Callable, Optional
from typing_extensions import Literal, Iterable, cast

from gbox_sdk._types import NOT_GIVEN, NotGiven
from gbox_sdk._client import GboxClient
from gbox_sdk.types.v1.boxes.action_ai_params import Settings
from gbox_sdk.types.v1.boxes.action_ai_response import ActionAIResponse
from gbox_sdk.types.v1.boxes.action_drag_params import DragSimpleEnd, DragSimpleStart, DragAdvancedPath
from gbox_sdk.types.v1.boxes.action_swipe_params import SwipeAdvancedEnd, SwipeAdvancedStart
from gbox_sdk.types.v1.boxes.action_tap_response import ActionTapResponse
from gbox_sdk.types.v1.boxes.action_touch_params import Point
from gbox_sdk.types.v1.boxes.action_drag_response import ActionDragResponse
from gbox_sdk.types.v1.boxes.action_move_response import ActionMoveResponse
from gbox_sdk.types.v1.boxes.action_type_response import ActionTypeResponse
from gbox_sdk.types.v1.boxes.action_click_response import ActionClickResponse
from gbox_sdk.types.v1.boxes.action_swipe_response import ActionSwipeResponse
from gbox_sdk.types.v1.boxes.action_touch_response import ActionTouchResponse
from gbox_sdk.types.v1.boxes.action_scroll_response import ActionScrollResponse
from gbox_sdk.types.v1.boxes.action_extract_response import ActionExtractResponse
from gbox_sdk.types.v1.boxes.action_press_key_params import KeysType
from gbox_sdk.types.v1.boxes.action_screenshot_params import Clip, ActionScreenshotParams
from gbox_sdk.types.v1.boxes.action_press_key_response import ActionPressKeyResponse
from gbox_sdk.types.v1.boxes.action_long_press_response import ActionLongPressResponse
from gbox_sdk.types.v1.boxes.action_screenshot_response import ActionScreenshotResponse
from gbox_sdk.types.v1.boxes.action_press_button_response import ActionPressButtonResponse
from gbox_sdk.types.v1.boxes.action_screen_layout_response import ActionScreenLayoutResponse
from gbox_sdk.types.v1.boxes.action_recording_stop_response import ActionRecordingStopResponse
from gbox_sdk.types.v1.boxes.action_screen_rotation_response import ActionScreenRotationResponse


class ActionScreenshot(ActionScreenshotParams, total=False):
    """
    Extends ActionScreenshotParams to optionally include a file path for saving the screenshot.

    Attributes:
        path (Optional[str]): The file path where the screenshot will be saved.
    """

    path: Optional[str]


class ActionOperator:
    """
    Provides high-level action operations for a specific box using the GboxClient.

    Methods correspond to various box actions such as click, drag, swipe, type, screenshot, etc.
    """

    def __init__(self, client: GboxClient, box_id: str):
        """
        Initialize the ActionOperator.

        Args:
            client (GboxClient): The GboxClient instance to use for API calls.
            box_id (str): The ID of the box to operate on.
        """
        self.client = client
        self.box_id = box_id

    def ai(
        self,
        instruction: str,
        *,
        background: Union[str, NotGiven] = NOT_GIVEN,
        include_screenshot: Union[bool, NotGiven] = NOT_GIVEN,
        output_format: Union[Literal["base64", "storageKey"], NotGiven] = NOT_GIVEN,
        screenshot_delay: Union[str, NotGiven] = NOT_GIVEN,
        settings: Union[Settings, NotGiven] = NOT_GIVEN,
        on_action_start: Optional[Callable[[], None]] = None,
        on_action_end: Optional[Callable[[], None]] = None,
    ) -> ActionAIResponse:
        """
        Perform an AI-powered action on the box.

        Args:
            instruction: Direct instruction of the UI action to perform (e.g., 'click the login button',
                'input username in the email field', 'scroll down', 'swipe left')

            background: The background of the UI action to perform. The purpose of background is to let
                the action executor to understand the context of why the instruction is given
                including important previous actions and observations

            include_screenshot: Whether to include screenshots in the action response. If false, the screenshot
                object will still be returned but with empty URIs. Default is false.

            output_format: Type of the URI. default is base64.

            screenshot_delay: Delay after performing the action, before taking the final screenshot.

                Execution flow:

                1. Take screenshot before action
                2. Perform the action
                3. Wait for screenshotDelay (this parameter)
                4. Take screenshot after action

                Example: '500ms' means wait 500ms after the action before capturing the final
                screenshot.

                Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
                Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s

            settings: AI action settings

            on_action_start: Callback function called when action starts
            on_action_end: Callback function called when action ends

        Returns:
            ActionAIResponse: The response from the AI action.

        Example:
            >>> response = myBox.action.ai("Click on the login button")
            >>> response = myBox.action.ai(
            ...     instruction="Click on the login button",
            ...     background="The background of the action",
            ...     include_screenshot=True,
            ...     output_format="base64",
            ...     screenshot_delay="500ms",
            ...     settings={"disableActions": ["click"], "systemPrompt": "You are a helpful assistant"},
            ... )
        """
        if on_action_start is not None or on_action_end is not None:
            return self.ai_stream(
                instruction=instruction,
                background=background,
                include_screenshot=include_screenshot,
                output_format=output_format,
                screenshot_delay=screenshot_delay,
                settings=settings,
                on_action_start=on_action_start,
                on_action_end=on_action_end,
            )

        return self.client.v1.boxes.actions.ai(
            box_id=self.box_id,
            instruction=instruction,
            background=background,
            include_screenshot=include_screenshot,
            output_format=output_format,
            screenshot_delay=screenshot_delay,
            settings=settings,
        )

    def ai_stream(
        self,
        instruction: str,
        *,
        background: Union[str, NotGiven] = NOT_GIVEN,
        include_screenshot: Union[bool, NotGiven] = NOT_GIVEN,
        output_format: Union[Literal["base64", "storageKey"], NotGiven] = NOT_GIVEN,
        screenshot_delay: Union[str, NotGiven] = NOT_GIVEN,
        settings: Union[Settings, NotGiven] = NOT_GIVEN,
        on_action_start: Optional[Callable[[], None]] = None,
        on_action_end: Optional[Callable[[], None]] = None,
    ) -> ActionAIResponse:
        """
        Perform an AI-powered action on the box with streaming support.

        Args:
            instruction: Direct instruction of the UI action to perform (e.g., 'click the login button',
                'input username in the email field', 'scroll down', 'swipe left')

            background: The background of the UI action to perform. The purpose of background is to let
                the action executor to understand the context of why the instruction is given
                including important previous actions and observations

            include_screenshot: Whether to include screenshots in the action response. If false, the screenshot
                object will still be returned but with empty URIs. Default is false.

            output_format: Type of the URI. default is base64.

            screenshot_delay: Delay after performing the action, before taking the final screenshot.

                Execution flow:

                1. Take screenshot before action
                2. Perform the action
                3. Wait for screenshotDelay (this parameter)
                4. Take screenshot after action

                Example: '500ms' means wait 500ms after the action before capturing the final
                screenshot.

                Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
                Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s

            settings: AI action settings

            on_action_start: Callback function called when action starts
            on_action_end: Callback function called when action ends

        Returns:
            ActionAIResponse: The response from the AI action.

        Example:
            >>> response = myBox.action.ai_stream(
            ...     instruction="Click on the login button",
            ...     on_action_start=lambda: print("Action started"),
            ...     on_action_end=lambda: print("Action ended"),
            ... )
        """
        try:
            # Use SDK streaming response wrapper to get SSE stream
            resp_ctx = self.client.v1.boxes.actions.with_streaming_response.ai(
                box_id=self.box_id,
                instruction=instruction,
                background=background,
                include_screenshot=include_screenshot,
                output_format=output_format,
                screenshot_delay=screenshot_delay,
                settings=settings,
                stream=True,
                timeout=None,
            )
            result: Optional[ActionAIResponse] = None
            buffer: str = ""

            # Enter the response context to get APIResponse and iterate
            with resp_ctx as api_response:
                for chunk in api_response.iter_bytes():
                    chunk_text: str = chunk.decode("utf-8")
                    buffer += chunk_text

                    while "\n\n" in buffer:
                        event_end: int = buffer.find("\n\n")
                        raw_event: str = buffer[:event_end].strip()
                        buffer = buffer[event_end + 2 :]

                        if not raw_event:
                            continue

                        event_name: str = ""
                        data_lines: List[str] = []

                        for line in raw_event.split("\n"):
                            if line.startswith("event:"):
                                event_name = line[6:].strip()
                            elif line.startswith("data:"):
                                data_lines.append(line[5:].strip())

                        data_str: str = "\n".join(data_lines)

                        if event_name == "before":
                            if on_action_start:
                                on_action_start()
                        elif event_name == "after":
                            if on_action_end:
                                on_action_end()
                        elif event_name == "result":
                            parsed: ActionAIResponse = json.loads(data_str)
                            result = parsed
                        elif event_name == "error":
                            error_data = json.loads(data_str)
                            raise RuntimeError(f"AI action error: {error_data.get('message', 'Unknown error')}")

            if result is None:
                raise RuntimeError("No result event received from stream")

            return result
        except Exception as e:
            raise RuntimeError(f"Failed to execute AI action via stream: {e}") from e

    def click(
        self,
        *,
        x: float,
        y: float,
        button: Union[Literal["left", "right", "middle"], NotGiven] = NOT_GIVEN,
        double: Union[bool, NotGiven] = NOT_GIVEN,
        include_screenshot: Union[bool, NotGiven] = NOT_GIVEN,
        output_format: Union[Literal["base64", "storageKey"], NotGiven] = NOT_GIVEN,
        screenshot_delay: Union[str, NotGiven] = NOT_GIVEN,
    ) -> ActionClickResponse:
        """
        Perform a click action on the box.

        Args:
          x: X coordinate of the click

          y: Y coordinate of the click

          button: Mouse button to click

          double: Whether to perform a double click

          include_screenshot: Whether to include screenshots in the action response. If false, the screenshot
              object will still be returned but with empty URIs. Default is false.

          output_format: Type of the URI. default is base64.

          screenshot_delay: Delay after performing the action, before taking the final screenshot.

              Execution flow:

              1. Take screenshot before action
              2. Perform the action
              3. Wait for screenshotDelay (this parameter)
              4. Take screenshot after action

              Example: '500ms' means wait 500ms after the action before capturing the final
              screenshot.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s

        Returns:
            ActionClickResponse: The response from the click action.

        Example:
            >>> response = myBox.action.click(x=100, y=100)
        """
        return self.client.v1.boxes.actions.click(
            box_id=self.box_id,
            x=x,
            y=y,
            button=button,
            double=double,
            include_screenshot=include_screenshot,
            output_format=output_format,
            screenshot_delay=screenshot_delay,
        )

    def drag(
        self,
        *,
        path: Union[Iterable[DragAdvancedPath], NotGiven] = NOT_GIVEN,
        start: Union[DragSimpleStart, NotGiven] = NOT_GIVEN,
        end: Union[DragSimpleEnd, NotGiven] = NOT_GIVEN,
        duration: Union[str, NotGiven] = NOT_GIVEN,
        include_screenshot: Union[bool, NotGiven] = NOT_GIVEN,
        output_format: Union[Literal["base64", "storageKey"], NotGiven] = NOT_GIVEN,
        screenshot_delay: Union[str, NotGiven] = NOT_GIVEN,
    ) -> ActionDragResponse:
        """
        Perform a drag action on the box.

        Args:
            path: Path of the drag action as a series of coordinates

            end: Single point in a drag path

            start: Single point in a drag path

            duration: Duration to complete the movement from start to end coordinates

                Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
                Example formats: "500ms", "30s", "5m", "1h" Default: 500ms

            include_screenshot: Whether to include screenshots in the action response. If false, the screenshot
                object will still be returned but with empty URIs. Default is false.

            output_format: Type of the URI. default is base64.

            screenshot_delay: Delay after performing the action, before taking the final screenshot.

                Execution flow:

                1. Take screenshot before action
                2. Perform the action
                3. Wait for screenshotDelay (this parameter)
                4. Take screenshot after action

                Example: '500ms' means wait 500ms after the action before capturing the final
                screenshot.

                Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
                Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s
        Returns:
            ActionDragResponse: The response from the drag action.

        Examples:
            Simple drag from start to end:
            >>> response = myBox.action.drag(start={"x": 100, "y": 100}, end={"x": 200, "y": 200})

            Advanced drag with path:
            >>> response = myBox.action.drag(
            ...     path=[
            ...         {"x": 100, "y": 100},
            ...         {"x": 150, "y": 150},
            ...         {"x": 200, "y": 200},
            ...     ]
            ... )
        """
        if path is not NOT_GIVEN:
            return self.client.v1.boxes.actions.drag(
                box_id=self.box_id,
                path=cast(Iterable[DragAdvancedPath], path),
                duration=duration,
                include_screenshot=include_screenshot,
                output_format=output_format,
                screenshot_delay=screenshot_delay,
            )
        elif start is not NOT_GIVEN and end is not NOT_GIVEN:
            return self.client.v1.boxes.actions.drag(
                box_id=self.box_id,
                start=cast(DragSimpleStart, start),
                end=cast(DragSimpleEnd, end),
                duration=duration,
                include_screenshot=include_screenshot,
                output_format=output_format,
                screenshot_delay=screenshot_delay,
            )
        else:
            raise ValueError(
                "Either 'path' (for advanced drag) or both 'start' and 'end' (for simple drag) must be provided"
            )

    def swipe(
        self,
        *,
        direction: Union[
            Literal["up", "down", "left", "right", "upLeft", "upRight", "downLeft", "downRight"], NotGiven
        ] = NOT_GIVEN,
        distance: Union[float, NotGiven] = NOT_GIVEN,
        start: Union[SwipeAdvancedStart, NotGiven] = NOT_GIVEN,
        end: Union[SwipeAdvancedEnd, NotGiven] = NOT_GIVEN,
        duration: Union[str, NotGiven] = NOT_GIVEN,
        include_screenshot: Union[bool, NotGiven] = NOT_GIVEN,
        output_format: Union[Literal["base64", "storageKey"], NotGiven] = NOT_GIVEN,
        screenshot_delay: Union[str, NotGiven] = NOT_GIVEN,
    ) -> ActionSwipeResponse:
        """
        Perform a swipe action on the box.

        Args:
            direction: Direction to swipe. The gesture will be performed from the center of the screen
                towards this direction.

            distance: Distance of the swipe in pixels. If not provided, the swipe will be performed
                from the center of the screen to the screen edge

            duration: Duration of the swipe

                Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
                Example formats: "500ms", "30s", "5m", "1h" Default: 500ms

            include_screenshot: Whether to include screenshots in the action response. If false, the screenshot
                object will still be returned but with empty URIs. Default is false.

            output_format: Type of the URI. default is base64.

            screenshot_delay: Delay after performing the action, before taking the final screenshot.

                Execution flow:

                1. Take screenshot before action
                2. Perform the action
                3. Wait for screenshotDelay (this parameter)
                4. Take screenshot after action

                Example: '500ms' means wait 500ms after the action before capturing the final
                screenshot.

                Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
                Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s

        Returns:
            ActionSwipeResponse: The response from the swipe action.

        Example:
            >>> response = myBox.action.swipe({"direction": "up"})
        """
        if direction is not NOT_GIVEN:
            return self.client.v1.boxes.actions.swipe(
                box_id=self.box_id,
                direction=cast(
                    Literal["up", "down", "left", "right", "upLeft", "upRight", "downLeft", "downRight"], direction
                ),
                distance=distance,
                duration=duration,
                include_screenshot=include_screenshot,
                output_format=output_format,
                screenshot_delay=screenshot_delay,
            )
        elif start is not NOT_GIVEN and end is not NOT_GIVEN:
            return self.client.v1.boxes.actions.swipe(
                box_id=self.box_id,
                start=cast(SwipeAdvancedStart, start),
                end=cast(SwipeAdvancedEnd, end),
                duration=duration,
                include_screenshot=include_screenshot,
                output_format=output_format,
                screenshot_delay=screenshot_delay,
            )
        else:
            raise ValueError(
                "Either 'direction' and 'distance' (for simple swipe) or both 'start' and 'end' (for advanced swipe) must be provided"
            )

    def press_key(
        self,
        *,
        keys: KeysType,
        combination: Union[bool, NotGiven] = NOT_GIVEN,
        include_screenshot: Union[bool, NotGiven] = NOT_GIVEN,
        output_format: Union[Literal["base64", "storageKey"], NotGiven] = NOT_GIVEN,
        screenshot_delay: Union[str, NotGiven] = NOT_GIVEN,
    ) -> ActionPressKeyResponse:
        """
        Simulate a key press on the box.

        Args:
            keys: This is an array of keyboard keys to press. Supports cross-platform
                compatibility.

            combination: Whether to press keys as combination (simultaneously) or sequentially. When
                true, all keys are pressed together as a shortcut (e.g., Ctrl+C). When false,
                keys are pressed one by one in sequence.

            include_screenshot: Whether to include screenshots in the action response. If false, the screenshot
                object will still be returned but with empty URIs. Default is false.

            output_format: Type of the URI. default is base64.

            screenshot_delay: Delay after performing the action, before taking the final screenshot.

                Execution flow:

                1. Take screenshot before action
                2. Perform the action
                3. Wait for screenshotDelay (this parameter)
                4. Take screenshot after action

                Example: '500ms' means wait 500ms after the action before capturing the final
                screenshot.

                Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
                Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s

        Returns:
            ActionPressKeyResponse: The response from the key press action.

        Example:
            >>> response = myBox.action.press_key(keys=["enter"])
            >>> response = myBox.action.press_key(keys=["control", "c"], combination=True)
        """
        return self.client.v1.boxes.actions.press_key(
            box_id=self.box_id,
            keys=keys,
            combination=combination,
            include_screenshot=include_screenshot,
            output_format=output_format,
            screenshot_delay=screenshot_delay,
        )

    def press_button(
        self,
        *,
        buttons: List[Literal["power", "volumeUp", "volumeDown", "volumeMute", "home", "back", "menu", "appSwitch"]],
        include_screenshot: Union[bool, NotGiven] = NOT_GIVEN,
        output_format: Union[Literal["base64", "storageKey"], NotGiven] = NOT_GIVEN,
        screenshot_delay: Union[str, NotGiven] = NOT_GIVEN,
    ) -> ActionPressButtonResponse:
        """
        Simulate a button press on the box.

        Args:
          buttons: Button to press

          include_screenshot: Whether to include screenshots in the action response. If false, the screenshot
              object will still be returned but with empty URIs. Default is false.

          output_format: Type of the URI. default is base64.

          screenshot_delay: Delay after performing the action, before taking the final screenshot.

              Execution flow:

              1. Take screenshot before action
              2. Perform the action
              3. Wait for screenshotDelay (this parameter)
              4. Take screenshot after action

              Example: '500ms' means wait 500ms after the action before capturing the final
              screenshot.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s

        Returns:
            ActionPressButtonResponse: The response from the button press action.

        Example:
            >>> response = myBox.action.press_button(buttons=["power"])
        """
        return self.client.v1.boxes.actions.press_button(
            box_id=self.box_id,
            buttons=buttons,
            include_screenshot=include_screenshot,
            output_format=output_format,
            screenshot_delay=screenshot_delay,
        )

    def move(
        self,
        *,
        x: float,
        y: float,
        include_screenshot: Union[bool, NotGiven] = NOT_GIVEN,
        output_format: Union[Literal["base64", "storageKey"], NotGiven] = NOT_GIVEN,
        screenshot_delay: Union[str, NotGiven] = NOT_GIVEN,
    ) -> ActionMoveResponse:
        """
        Move an element or pointer on the box.

        Args:
            x: X coordinate to move to

            y: Y coordinate to move to

            include_screenshot: Whether to include screenshots in the action response. If false, the screenshot
                object will still be returned but with empty URIs. Default is false.

            output_format: Type of the URI. default is base64.

            screenshot_delay: Delay after performing the action, before taking the final screenshot.

                Execution flow:

                1. Take screenshot before action
                2. Perform the action
                3. Wait for screenshotDelay (this parameter)
                4. Take screenshot after action

                Example: '500ms' means wait 500ms after the action before capturing the final
                screenshot.

                Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
                Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s

        Returns:
            ActionMoveResponse: The response from the move action.

        Example:
            >>> response = myBox.action.move(x=200, y=300)
        """
        return self.client.v1.boxes.actions.move(
            box_id=self.box_id,
            x=x,
            y=y,
            include_screenshot=include_screenshot,
            output_format=output_format,
            screenshot_delay=screenshot_delay,
        )

    def tap(
        self,
        *,
        x: float,
        y: float,
        include_screenshot: Union[bool, NotGiven] = NOT_GIVEN,
        output_format: Union[Literal["base64", "storageKey"], NotGiven] = NOT_GIVEN,
        presigned_expires_in: Union[str, NotGiven] = NOT_GIVEN,
        screenshot_delay: Union[str, NotGiven] = NOT_GIVEN,
    ) -> ActionTapResponse:
        """
        Tap action for Android devices using ADB input tap command

        Args:
          x: X coordinate of the tap

          y: Y coordinate of the tap

          include_screenshot: Whether to include screenshots in the action response. If false, the screenshot
              object will still be returned but with empty URIs. Default is false.

          output_format: Type of the URI. default is base64.

          presigned_expires_in: Presigned url expires in. Only takes effect when outputFormat is storageKey.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: Delay after performing the action, before taking the final screenshot.

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
        return self.client.v1.boxes.actions.tap(
            box_id=self.box_id,
            x=x,
            y=y,
            include_screenshot=include_screenshot,
            output_format=output_format,
            presigned_expires_in=presigned_expires_in,
            screenshot_delay=screenshot_delay,
        )

    def long_press(
        self,
        *,
        x: float,
        y: float,
        duration: Union[str, NotGiven] = NOT_GIVEN,
        include_screenshot: Union[bool, NotGiven] = NOT_GIVEN,
        output_format: Union[Literal["base64", "storageKey"], NotGiven] = NOT_GIVEN,
        presigned_expires_in: Union[str, NotGiven] = NOT_GIVEN,
        screenshot_delay: Union[str, NotGiven] = NOT_GIVEN,
    ) -> ActionLongPressResponse:
        """
        Perform a long press action at specified coordinates for a specified duration.
        Useful for triggering context menus, drag operations, or other long-press
        interactions.

        Args:
          x: X coordinate of the long press

          y: Y coordinate of the long press

          duration: Duration to hold the press (e.g. '1s', '500ms')

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 1s

          include_screenshot: Whether to include screenshots in the action response. If false, the screenshot
              object will still be returned but with empty URIs. Default is false.

          output_format: Type of the URI. default is base64.

          presigned_expires_in: Presigned url expires in. Only takes effect when outputFormat is storageKey.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: Delay after performing the action, before taking the final screenshot.

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
        return self.client.v1.boxes.actions.long_press(
            box_id=self.box_id,
            x=x,
            y=y,
            duration=duration,
            include_screenshot=include_screenshot,
            output_format=output_format,
            presigned_expires_in=presigned_expires_in,
            screenshot_delay=screenshot_delay,
        )

    def scroll(
        self,
        *,
        scroll_x: float,
        scroll_y: float,
        x: float,
        y: float,
        include_screenshot: Union[bool, NotGiven] = NOT_GIVEN,
        output_format: Union[Literal["base64", "storageKey"], NotGiven] = NOT_GIVEN,
        screenshot_delay: Union[str, NotGiven] = NOT_GIVEN,
    ) -> ActionScrollResponse:
        """
        Perform a scroll action on the box.

        Args:
            scroll_x: Horizontal scroll amount

            scroll_y: Vertical scroll amount

            x: X coordinate of the scroll position

            y: Y coordinate of the scroll position

            include_screenshot: Whether to include screenshots in the action response. If false, the screenshot
                object will still be returned but with empty URIs. Default is false.

            output_format: Type of the URI. default is base64.

            screenshot_delay: Delay after performing the action, before taking the final screenshot.

                Execution flow:

                1. Take screenshot before action
                2. Perform the action
                3. Wait for screenshotDelay (this parameter)
                4. Take screenshot after action

                Example: '500ms' means wait 500ms after the action before capturing the final
                screenshot.

                Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
                Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s

        Returns:
            ActionScrollResponse: The response from the scroll action.

        Example:
            >>> response = myBox.action.scroll(scroll_x=0, scroll_y=100, x=100, y=100)
        """
        return self.client.v1.boxes.actions.scroll(
            box_id=self.box_id,
            scroll_x=scroll_x,
            scroll_y=scroll_y,
            x=x,
            y=y,
            include_screenshot=include_screenshot,
            output_format=output_format,
            screenshot_delay=screenshot_delay,
        )

    def touch(
        self,
        *,
        points: Iterable[Point],
        include_screenshot: Union[bool, NotGiven] = NOT_GIVEN,
        output_format: Union[Literal["base64", "storageKey"], NotGiven] = NOT_GIVEN,
        screenshot_delay: Union[str, NotGiven] = NOT_GIVEN,
    ) -> ActionTouchResponse:
        """
        Simulate a touch action on the box.

        Args:
            points: Array of touch points and their actions

            include_screenshot: Whether to include screenshots in the action response. If false, the screenshot
                object will still be returned but with empty URIs. Default is false.

            output_format: Type of the URI. default is base64.

            screenshot_delay: Delay after performing the action, before taking the final screenshot.

                Execution flow:

                1. Take screenshot before action
                2. Perform the action
                3. Wait for screenshotDelay (this parameter)
                4. Take screenshot after action

                Example: '500ms' means wait 500ms after the action before capturing the final
                screenshot.

                Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
                Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s

        Returns:
            ActionTouchResponse: The response from the touch action.

        Example:
            >>> response = myBox.action.touch(points=[{"start": {"x": 0, "y": 0}}])
        """
        return self.client.v1.boxes.actions.touch(
            box_id=self.box_id,
            points=points,
            include_screenshot=include_screenshot,
            output_format=output_format,
            screenshot_delay=screenshot_delay,
        )

    def type(
        self,
        *,
        text: str,
        include_screenshot: Union[bool, NotGiven] = NOT_GIVEN,
        mode: Union[Literal["append", "replace"], NotGiven] = NOT_GIVEN,
        output_format: Union[Literal["base64", "storageKey"], NotGiven] = NOT_GIVEN,
        screenshot_delay: Union[str, NotGiven] = NOT_GIVEN,
    ) -> ActionTypeResponse:
        """
        Simulate typing text on the box.

        Args:
            text: Text to type

            include_screenshot: Whether to include screenshots in the action response. If false, the screenshot
                object will still be returned but with empty URIs. Default is false.

            mode: Text input mode: 'append' to add text to existing content, 'replace' to replace
                all existing text

            output_format: Type of the URI. default is base64.

            screenshot_delay: Delay after performing the action, before taking the final screenshot.

                Execution flow:

                1. Take screenshot before action
                2. Perform the action
                3. Wait for screenshotDelay (this parameter)
                4. Take screenshot after action

                Example: '500ms' means wait 500ms after the action before capturing the final
                screenshot.

                Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
                Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s

        Returns:
            ActionTypeResponse: The response from the type action.

        Example:
            >>> response = myBox.action.type(text="Hello, World!")
        """
        return self.client.v1.boxes.actions.type(
            box_id=self.box_id,
            text=text,
            include_screenshot=include_screenshot,
            mode=mode,
            output_format=output_format,
            screenshot_delay=screenshot_delay,
        )

    def extract(
        self,
        *,
        instruction: str,
        schema: Union[object, NotGiven] = NOT_GIVEN,
    ) -> ActionExtractResponse:
        """
        Extract data from the UI interface using a JSON schema.

        Args:
          instruction: The instruction of the action to extract data from the UI interface

          schema: JSON Schema defining the structure of data to extract. Supports object, array,
              string, number, boolean types with validation rules.

              Common use cases:

              - Extract text content: { "type": "string" }
              - Extract structured data: { "type": "object", "properties": {...} }
              - Extract lists: { "type": "array", "items": {...} }
              - Extract with validation: Add constraints like "required", "enum", "pattern",
                etc.

        Returns:
            ActionExtractResponse: The response containing the extracted data.

        Example:
            >>> response = myBox.action.extract(
            ...     instruction="Extract the user name from the profile",
            ...     schema={"type": "string"},
            ... )
        """
        return self.client.v1.boxes.actions.extract(
            box_id=self.box_id,
            instruction=instruction,
            schema=schema,
        )

    def screenshot(
        self,
        *,
        path: Union[str, NotGiven] = NOT_GIVEN,
        clip: Union[Clip, NotGiven] = NOT_GIVEN,
        output_format: Union[Literal["base64", "storageKey"], NotGiven] = NOT_GIVEN,
    ) -> ActionScreenshotResponse:
        """
        Take a screenshot of the box.

        Args:
            path: The path to save the screenshot to.

            clip: Clipping region for screenshot capture

            output_format: Type of the URI. default is base64.

        Returns:
            ActionScreenshotResponse: The response containing the screenshot data.

        Examples:
            Take a screenshot and return base64 data:
            >>> response = action_operator.screenshot()

            Take a screenshot and save to file:
            >>> response = action_operator.screenshot(path="/path/to/screenshot.png")

            Take a screenshot with specific format:
            >>> response = action_operator.screenshot(output_format="base64")
        """
        if path is not NOT_GIVEN:
            file_path = path
        else:
            file_path = None

        response = self.client.v1.boxes.actions.screenshot(
            box_id=self.box_id,
            clip=clip,
            output_format=output_format,
        )

        if file_path:
            self._save_data_url_to_file(response.uri, file_path)

        return response

    def screen_layout(self) -> ActionScreenLayoutResponse:
        """
        Get the current structured screen layout information.

        Returns:
            ActionScreenLayoutResponse: The response containing the screen layout data.

        Example:
            >>> response = myBox.action.screen_layout()
        """
        return self.client.v1.boxes.actions.screen_layout(box_id=self.box_id)

    def screen_rotation(
        self,
        orientation: Literal["portrait", "landscapeLeft", "portraitUpsideDown", "landscapeRight"],
        *,
        include_screenshot: Union[bool, NotGiven] = NOT_GIVEN,
        output_format: Union[Literal["base64", "storageKey"], NotGiven] = NOT_GIVEN,
        presigned_expires_in: Union[str, NotGiven] = NOT_GIVEN,
        screenshot_delay: Union[str, NotGiven] = NOT_GIVEN,
    ) -> ActionScreenRotationResponse:
        """
        Rotate the screen orientation.

        Note that even after rotating the screen,
        applications or system layouts may not automatically adapt to the gravity sensor
        changes, so visual changes may not always occur.

        Args:
            orientation: Target screen orientation

            include_screenshot: Whether to include screenshots in the action response. If false, the screenshot
                object will still be returned but with empty URIs. Default is false.

            output_format: Type of the URI. default is base64.

            presigned_expires_in: Presigned url expires in. Only takes effect when outputFormat is storageKey.

                Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
                Example formats: "500ms", "30s", "5m", "1h" Default: 30m

            screenshot_delay: Delay after performing the action, before taking the final screenshot.

                Execution flow:

                1. Take screenshot before action
                2. Perform the action
                3. Wait for screenshotDelay (this parameter)
                4. Take screenshot after action

                Example: '500ms' means wait 500ms after the action before capturing the final
                screenshot.

                Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
                Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s


        Returns:
            ActionScreenRotationResponse: The response from the screen rotation action.

        Example:
            >>> response = myBox.action.screen_rotation("landscapeLeft")
            >>> response = myBox.action.screen_rotation(
            ...     orientation="landscapeLeft",
            ...     include_screenshot=True,
            ...     output_format="storageKey",
            ...     presigned_expires_in="30m",
            ...     screenshot_delay="500ms",
            ... )
        """
        return self.client.v1.boxes.actions.screen_rotation(
            box_id=self.box_id,
            orientation=orientation,
            include_screenshot=include_screenshot,
            output_format=output_format,
            presigned_expires_in=presigned_expires_in,
            screenshot_delay=screenshot_delay,
        )

    def screen_recording_start(self, duration: str) -> None:
        """
        Start recording the box screen.

        Only one recording can be active at a time. If a
        recording is already in progress, starting a new recording will stop the
        previous one and keep only the latest recording.

        Args:
          duration: Duration of the recording. Default is 30m, max is 30m. The recording will
              automatically stop when the duration time is reached.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Maximum allowed: 30m

        Example:
            >>> response = myBox.action.screen_recording_start(duration="30m")
        """
        return self.client.v1.boxes.actions.recording_start(box_id=self.box_id, duration=duration)

    def screen_recording_stop(self) -> ActionRecordingStopResponse:
        """
        Stop recording the screen.

        Returns:
            ActionRecordingStopResponse: The response from the screen recording stop action.

        Example:
            >>> response = myBox.action.screen_recording_stop()
        """
        return self.client.v1.boxes.actions.recording_stop(box_id=self.box_id)

    def _save_data_url_to_file(self, data_url: str, file_path: str) -> None:
        """
        Save a base64-encoded data URL to a file.

        Args:
            data_url (str): The data URL containing base64-encoded data.
            file_path (str): The file path where the decoded data will be saved.
        Raises:
            ValueError: If the data URL format is invalid.
        """
        if not data_url.startswith("data:"):
            raise ValueError("Invalid data URL format")
        parts = data_url.split(",")
        if len(parts) != 2:
            raise ValueError("Invalid data URL format")
        base64_data = parts[1]

        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(base64.b64decode(base64_data))
