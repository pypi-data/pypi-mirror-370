# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, List, Union, Iterable, cast
from typing_extensions import Literal, overload

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ...._utils import required_args, maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v1.boxes import (
    action_ai_params,
    action_tap_params,
    action_drag_params,
    action_move_params,
    action_type_params,
    action_click_params,
    action_swipe_params,
    action_touch_params,
    action_scroll_params,
    action_extract_params,
    action_press_key_params,
    action_long_press_params,
    action_screenshot_params,
    action_press_button_params,
    action_recording_start_params,
    action_screen_rotation_params,
)
from ....types.v1.boxes.action_ai_response import ActionAIResponse
from ....types.v1.boxes.action_tap_response import ActionTapResponse
from ....types.v1.boxes.action_drag_response import ActionDragResponse
from ....types.v1.boxes.action_move_response import ActionMoveResponse
from ....types.v1.boxes.action_type_response import ActionTypeResponse
from ....types.v1.boxes.action_click_response import ActionClickResponse
from ....types.v1.boxes.action_swipe_response import ActionSwipeResponse
from ....types.v1.boxes.action_touch_response import ActionTouchResponse
from ....types.v1.boxes.action_scroll_response import ActionScrollResponse
from ....types.v1.boxes.action_extract_response import ActionExtractResponse
from ....types.v1.boxes.action_press_key_response import ActionPressKeyResponse
from ....types.v1.boxes.action_long_press_response import ActionLongPressResponse
from ....types.v1.boxes.action_screenshot_response import ActionScreenshotResponse
from ....types.v1.boxes.action_press_button_response import ActionPressButtonResponse
from ....types.v1.boxes.action_screen_layout_response import ActionScreenLayoutResponse
from ....types.v1.boxes.action_recording_stop_response import ActionRecordingStopResponse
from ....types.v1.boxes.action_screen_rotation_response import ActionScreenRotationResponse

__all__ = ["ActionsResource", "AsyncActionsResource"]


class ActionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ActionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return ActionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ActionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return ActionsResourceWithStreamingResponse(self)

    def ai(
        self,
        box_id: str,
        *,
        instruction: str,
        background: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        settings: action_ai_params.Settings | NotGiven = NOT_GIVEN,
        stream: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionAIResponse:
        """Use natural language instructions to perform UI operations on the box.

        The
        endpoint will stream progress events before and after the action is executed. If
        you don't need intermediate events, set stream to false.

        Args:
          instruction: Direct instruction of the UI action to perform (e.g., 'click the login button',
              'input username in the email field', 'scroll down', 'swipe left')

          background: The background of the UI action to perform. The purpose of background is to let
              the action executor to understand the context of why the instruction is given
              including important previous actions and observations

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

          settings: AI action settings

          stream: Whether to stream progress events using Server-Sent Events (SSE). When true, the
              API returns an event stream. When false or omitted, the API returns a normal
              JSON response.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionAIResponse,
            self._post(
                f"/boxes/{box_id}/actions/ai",
                body=maybe_transform(
                    {
                        "instruction": instruction,
                        "background": background,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                        "settings": settings,
                        "stream": stream,
                    },
                    action_ai_params.ActionAIParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, ActionAIResponse),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    @overload
    def click(
        self,
        box_id: str,
        *,
        x: float,
        y: float,
        button: Literal["left", "right", "middle"] | NotGiven = NOT_GIVEN,
        double: bool | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionClickResponse:
        """
        Click

        Args:
          x: X coordinate of the click

          y: Y coordinate of the click

          button: Mouse button to click

          double: Whether to perform a double click

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def click(
        self,
        box_id: str,
        *,
        target: str,
        button: Literal["left", "right", "middle"] | NotGiven = NOT_GIVEN,
        double: bool | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionClickResponse:
        """
        Click

        Args:
          target: Describe the target to operate using natural language, e.g., 'login button' or
              'Chrome'.

          button: Mouse button to click

          double: Whether to perform a double click

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["x", "y"], ["target"])
    def click(
        self,
        box_id: str,
        *,
        x: float | NotGiven = NOT_GIVEN,
        y: float | NotGiven = NOT_GIVEN,
        button: Literal["left", "right", "middle"] | NotGiven = NOT_GIVEN,
        double: bool | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        target: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionClickResponse:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionClickResponse,
            self._post(
                f"/boxes/{box_id}/actions/click",
                body=maybe_transform(
                    {
                        "x": x,
                        "y": y,
                        "button": button,
                        "double": double,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                        "target": target,
                    },
                    action_click_params.ActionClickParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionClickResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    @overload
    def drag(
        self,
        box_id: str,
        *,
        end: action_drag_params.DragSimpleEnd,
        start: action_drag_params.DragSimpleStart,
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionDragResponse:
        """
        Drag

        Args:
          end: End point of the drag path (coordinates or natural language)

          start: Start point of the drag path (coordinates or natural language)

          duration: Duration to complete the movement from start to end coordinates

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 500ms

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def drag(
        self,
        box_id: str,
        *,
        path: Iterable[action_drag_params.DragAdvancedPath],
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionDragResponse:
        """
        Drag

        Args:
          path: Path of the drag action as a series of coordinates

          duration: Time interval between points (e.g. "50ms")

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 50ms

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["end", "start"], ["path"])
    def drag(
        self,
        box_id: str,
        *,
        end: action_drag_params.DragSimpleEnd | NotGiven = NOT_GIVEN,
        start: action_drag_params.DragSimpleStart | NotGiven = NOT_GIVEN,
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        path: Iterable[action_drag_params.DragAdvancedPath] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionDragResponse:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionDragResponse,
            self._post(
                f"/boxes/{box_id}/actions/drag",
                body=maybe_transform(
                    {
                        "end": end,
                        "start": start,
                        "duration": duration,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                        "path": path,
                    },
                    action_drag_params.ActionDragParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionDragResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def extract(
        self,
        box_id: str,
        *,
        instruction: str,
        schema: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/extract",
            body=maybe_transform(
                {
                    "instruction": instruction,
                    "schema": schema,
                },
                action_extract_params.ActionExtractParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionExtractResponse,
        )

    @overload
    def long_press(
        self,
        box_id: str,
        *,
        x: float,
        y: float,
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def long_press(
        self,
        box_id: str,
        *,
        target: str,
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionLongPressResponse:
        """
        Perform a long press action at specified coordinates for a specified duration.
        Useful for triggering context menus, drag operations, or other long-press
        interactions.

        Args:
          target: Describe the target to operate using natural language, e.g., 'Chrome icon',
              'login button'

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["x", "y"], ["target"])
    def long_press(
        self,
        box_id: str,
        *,
        x: float | NotGiven = NOT_GIVEN,
        y: float | NotGiven = NOT_GIVEN,
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        target: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionLongPressResponse:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionLongPressResponse,
            self._post(
                f"/boxes/{box_id}/actions/long-press",
                body=maybe_transform(
                    {
                        "x": x,
                        "y": y,
                        "duration": duration,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                        "target": target,
                    },
                    action_long_press_params.ActionLongPressParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionLongPressResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def move(
        self,
        box_id: str,
        *,
        x: float,
        y: float,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionMoveResponse:
        """
        Move to position

        Args:
          x: X coordinate to move to

          y: Y coordinate to move to

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionMoveResponse,
            self._post(
                f"/boxes/{box_id}/actions/move",
                body=maybe_transform(
                    {
                        "x": x,
                        "y": y,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                    },
                    action_move_params.ActionMoveParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionMoveResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def press_button(
        self,
        box_id: str,
        *,
        buttons: List[Literal["power", "volumeUp", "volumeDown", "volumeMute", "home", "back", "menu", "appSwitch"]],
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionPressButtonResponse:
        """
        Press device buttons like power, volume, home, back, etc.

        Args:
          buttons: Button to press

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionPressButtonResponse,
            self._post(
                f"/boxes/{box_id}/actions/press-button",
                body=maybe_transform(
                    {
                        "buttons": buttons,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                    },
                    action_press_button_params.ActionPressButtonParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionPressButtonResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def press_key(
        self,
        box_id: str,
        *,
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
        ],
        combination: bool | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionPressKeyResponse:
        """
        Simulates pressing a specific key by triggering the complete keyboard key event
        chain (keydown, keypress, keyup). Use this to activate keyboard key event
        listeners such as shortcuts or form submissions.

        Args:
          keys: This is an array of keyboard keys to press. Supports cross-platform
              compatibility.

          combination: Whether to press keys as combination (simultaneously) or sequentially. When
              true, all keys are pressed together as a shortcut (e.g., Ctrl+C). When false,
              keys are pressed one by one in sequence.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionPressKeyResponse,
            self._post(
                f"/boxes/{box_id}/actions/press-key",
                body=maybe_transform(
                    {
                        "keys": keys,
                        "combination": combination,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                    },
                    action_press_key_params.ActionPressKeyParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionPressKeyResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def recording_start(
        self,
        box_id: str,
        *,
        duration: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Start recording the box screen.

        Only one recording can be active at a time. If a
        recording is already in progress, starting a new recording will stop the
        previous one and keep only the latest recording.

        Args:
          duration: Duration of the recording. Default is 30m, max is 30m. The recording will
              automatically stop when the duration time is reached.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Maximum allowed: 30m

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/boxes/{box_id}/actions/recording/start",
            body=maybe_transform({"duration": duration}, action_recording_start_params.ActionRecordingStartParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def recording_stop(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionRecordingStopResponse:
        """
        Stop recording the box screen

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/recording/stop",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionRecordingStopResponse,
        )

    def screen_layout(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionScreenLayoutResponse:
        """Get the current structured screen layout information.

        This endpoint returns
        detailed structural information about the UI elements currently displayed on the
        screen, which can be used for UI automation, element analysis, and accessibility
        purposes. The format varies by box type: Android boxes return XML format with
        detailed UI hierarchy information including element bounds, text content,
        resource IDs, and properties, while other box types may return different
        structured formats.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._get(
            f"/boxes/{box_id}/actions/screen-layout",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionScreenLayoutResponse,
        )

    def screen_rotation(
        self,
        box_id: str,
        *,
        orientation: Literal["portrait", "landscapeLeft", "portraitUpsideDown", "landscapeRight"],
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionScreenRotationResponse:
        """Rotate the screen orientation.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionScreenRotationResponse,
            self._post(
                f"/boxes/{box_id}/actions/screen-rotation",
                body=maybe_transform(
                    {
                        "orientation": orientation,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                    },
                    action_screen_rotation_params.ActionScreenRotationParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionScreenRotationResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def screenshot(
        self,
        box_id: str,
        *,
        clip: action_screenshot_params.Clip | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionScreenshotResponse:
        """
        Take screenshot

        Args:
          clip: Clipping region for screenshot capture

          output_format: Type of the URI. default is base64.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/screenshot",
            body=maybe_transform(
                {
                    "clip": clip,
                    "output_format": output_format,
                },
                action_screenshot_params.ActionScreenshotParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionScreenshotResponse,
        )

    @overload
    def scroll(
        self,
        box_id: str,
        *,
        scroll_x: float,
        scroll_y: float,
        x: float,
        y: float,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionScrollResponse:
        """Performs a scroll action.

        Supports both advanced scroll with coordinates and
        simple scroll with direction.

        Args:
          scroll_x: Horizontal scroll amount. Positive values scroll content rightward (reveals
              content on the left), negative values scroll content leftward (reveals content
              on the right).

          scroll_y: Vertical scroll amount. Positive values scroll content downward (reveals content
              above), negative values scroll content upward (reveals content below).

          x: X coordinate of the scroll position

          y: Y coordinate of the scroll position

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def scroll(
        self,
        box_id: str,
        *,
        direction: Literal["up", "down", "left", "right"],
        distance: Union[float, Literal["tiny", "short", "medium", "long"]] | NotGiven = NOT_GIVEN,
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionScrollResponse:
        """Performs a scroll action.

        Supports both advanced scroll with coordinates and
        simple scroll with direction.

        Args:
          direction: Direction to scroll. The scroll will be performed from the center of the screen
              towards this direction. 'up' scrolls content upward (reveals content below),
              'down' scrolls content downward (reveals content above), 'left' scrolls content
              leftward (reveals content on the right), 'right' scrolls content rightward
              (reveals content on the left).

          distance: Distance of the scroll. Can be either a number (in pixels) or a predefined enum
              value (tiny, short, medium, long). If not provided, the scroll will be performed
              from the center of the screen to the screen edge

          duration: Duration of the scroll

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 500ms

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["scroll_x", "scroll_y", "x", "y"], ["direction"])
    def scroll(
        self,
        box_id: str,
        *,
        scroll_x: float | NotGiven = NOT_GIVEN,
        scroll_y: float | NotGiven = NOT_GIVEN,
        x: float | NotGiven = NOT_GIVEN,
        y: float | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        direction: Literal["up", "down", "left", "right"] | NotGiven = NOT_GIVEN,
        distance: Union[float, Literal["tiny", "short", "medium", "long"]] | NotGiven = NOT_GIVEN,
        duration: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionScrollResponse:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionScrollResponse,
            self._post(
                f"/boxes/{box_id}/actions/scroll",
                body=maybe_transform(
                    {
                        "scroll_x": scroll_x,
                        "scroll_y": scroll_y,
                        "x": x,
                        "y": y,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                        "direction": direction,
                        "distance": distance,
                        "duration": duration,
                    },
                    action_scroll_params.ActionScrollParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionScrollResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    @overload
    def swipe(
        self,
        box_id: str,
        *,
        direction: Literal["up", "down", "left", "right", "upLeft", "upRight", "downLeft", "downRight"],
        distance: Union[float, Literal["tiny", "short", "medium", "long"]] | NotGiven = NOT_GIVEN,
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionSwipeResponse:
        """
        Performs a swipe in the specified direction

        Args:
          direction: Direction to swipe. The gesture will be performed from the center of the screen
              towards this direction.

          distance: Distance of the swipe. Can be either a number (in pixels) or a predefined enum
              value (tiny, short, medium, long). If not provided, the swipe will be performed
              from the center of the screen to the screen edge

          duration: Duration of the swipe

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 500ms

          include_screenshot: Whether to include screenshots in the action response. If false, the screenshot
              object will still be returned but with empty URIs. Default is false.

          location: Natural language description of the location where the swipe should originate.
              If not provided, the swipe will be performed from the center of the screen.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def swipe(
        self,
        box_id: str,
        *,
        end: action_swipe_params.SwipeAdvancedEnd,
        start: action_swipe_params.SwipeAdvancedStart,
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionSwipeResponse:
        """
        Performs a swipe in the specified direction

        Args:
          end: End point of the swipe path (coordinates or natural language)

          start: Start point of the swipe path (coordinates or natural language)

          duration: Duration of the swipe

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 500ms

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["direction"], ["end", "start"])
    def swipe(
        self,
        box_id: str,
        *,
        direction: Literal["up", "down", "left", "right", "upLeft", "upRight", "downLeft", "downRight"]
        | NotGiven = NOT_GIVEN,
        distance: Union[float, Literal["tiny", "short", "medium", "long"]] | NotGiven = NOT_GIVEN,
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        end: action_swipe_params.SwipeAdvancedEnd | NotGiven = NOT_GIVEN,
        start: action_swipe_params.SwipeAdvancedStart | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionSwipeResponse:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionSwipeResponse,
            self._post(
                f"/boxes/{box_id}/actions/swipe",
                body=maybe_transform(
                    {
                        "direction": direction,
                        "distance": distance,
                        "duration": duration,
                        "include_screenshot": include_screenshot,
                        "location": location,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                        "end": end,
                        "start": start,
                    },
                    action_swipe_params.ActionSwipeParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionSwipeResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    @overload
    def tap(
        self,
        box_id: str,
        *,
        x: float,
        y: float,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def tap(
        self,
        box_id: str,
        *,
        target: str,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTapResponse:
        """
        Tap action for Android devices using ADB input tap command

        Args:
          target: Describe the target to operate using natural language, e.g., 'login button' or
              'Chrome'.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["x", "y"], ["target"])
    def tap(
        self,
        box_id: str,
        *,
        x: float | NotGiven = NOT_GIVEN,
        y: float | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        target: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTapResponse:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionTapResponse,
            self._post(
                f"/boxes/{box_id}/actions/tap",
                body=maybe_transform(
                    {
                        "x": x,
                        "y": y,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                        "target": target,
                    },
                    action_tap_params.ActionTapParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, ActionTapResponse),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def touch(
        self,
        box_id: str,
        *,
        points: Iterable[action_touch_params.Point],
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTouchResponse:
        """
        Touch

        Args:
          points: Array of touch points and their actions

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionTouchResponse,
            self._post(
                f"/boxes/{box_id}/actions/touch",
                body=maybe_transform(
                    {
                        "points": points,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                    },
                    action_touch_params.ActionTouchParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionTouchResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def type(
        self,
        box_id: str,
        *,
        text: str,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        mode: Literal["append", "replace"] | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        press_enter: bool | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeResponse:
        """
        Directly inputs text content without triggering physical key events (keydown,
        etc.), ideal for quickly filling large amounts of text when intermediate input
        events aren't needed.

        Args:
          text: Text to type

          include_screenshot: Whether to include screenshots in the action response. If false, the screenshot
              object will still be returned but with empty URIs. Default is false.

          mode: Text input mode: 'append' to add text to existing content, 'replace' to replace
              all existing text

          output_format: Type of the URI. default is base64.

          presigned_expires_in: Presigned url expires in. Only takes effect when outputFormat is storageKey.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          press_enter: Whether to press Enter after typing the text

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionTypeResponse,
            self._post(
                f"/boxes/{box_id}/actions/type",
                body=maybe_transform(
                    {
                        "text": text,
                        "include_screenshot": include_screenshot,
                        "mode": mode,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "press_enter": press_enter,
                        "screenshot_delay": screenshot_delay,
                    },
                    action_type_params.ActionTypeParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionTypeResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class AsyncActionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncActionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncActionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncActionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return AsyncActionsResourceWithStreamingResponse(self)

    async def ai(
        self,
        box_id: str,
        *,
        instruction: str,
        background: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        settings: action_ai_params.Settings | NotGiven = NOT_GIVEN,
        stream: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionAIResponse:
        """Use natural language instructions to perform UI operations on the box.

        The
        endpoint will stream progress events before and after the action is executed. If
        you don't need intermediate events, set stream to false.

        Args:
          instruction: Direct instruction of the UI action to perform (e.g., 'click the login button',
              'input username in the email field', 'scroll down', 'swipe left')

          background: The background of the UI action to perform. The purpose of background is to let
              the action executor to understand the context of why the instruction is given
              including important previous actions and observations

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

          settings: AI action settings

          stream: Whether to stream progress events using Server-Sent Events (SSE). When true, the
              API returns an event stream. When false or omitted, the API returns a normal
              JSON response.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionAIResponse,
            await self._post(
                f"/boxes/{box_id}/actions/ai",
                body=await async_maybe_transform(
                    {
                        "instruction": instruction,
                        "background": background,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                        "settings": settings,
                        "stream": stream,
                    },
                    action_ai_params.ActionAIParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, ActionAIResponse),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    @overload
    async def click(
        self,
        box_id: str,
        *,
        x: float,
        y: float,
        button: Literal["left", "right", "middle"] | NotGiven = NOT_GIVEN,
        double: bool | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionClickResponse:
        """
        Click

        Args:
          x: X coordinate of the click

          y: Y coordinate of the click

          button: Mouse button to click

          double: Whether to perform a double click

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def click(
        self,
        box_id: str,
        *,
        target: str,
        button: Literal["left", "right", "middle"] | NotGiven = NOT_GIVEN,
        double: bool | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionClickResponse:
        """
        Click

        Args:
          target: Describe the target to operate using natural language, e.g., 'login button' or
              'Chrome'.

          button: Mouse button to click

          double: Whether to perform a double click

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["x", "y"], ["target"])
    async def click(
        self,
        box_id: str,
        *,
        x: float | NotGiven = NOT_GIVEN,
        y: float | NotGiven = NOT_GIVEN,
        button: Literal["left", "right", "middle"] | NotGiven = NOT_GIVEN,
        double: bool | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        target: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionClickResponse:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionClickResponse,
            await self._post(
                f"/boxes/{box_id}/actions/click",
                body=await async_maybe_transform(
                    {
                        "x": x,
                        "y": y,
                        "button": button,
                        "double": double,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                        "target": target,
                    },
                    action_click_params.ActionClickParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionClickResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    @overload
    async def drag(
        self,
        box_id: str,
        *,
        end: action_drag_params.DragSimpleEnd,
        start: action_drag_params.DragSimpleStart,
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionDragResponse:
        """
        Drag

        Args:
          end: End point of the drag path (coordinates or natural language)

          start: Start point of the drag path (coordinates or natural language)

          duration: Duration to complete the movement from start to end coordinates

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 500ms

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def drag(
        self,
        box_id: str,
        *,
        path: Iterable[action_drag_params.DragAdvancedPath],
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionDragResponse:
        """
        Drag

        Args:
          path: Path of the drag action as a series of coordinates

          duration: Time interval between points (e.g. "50ms")

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 50ms

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["end", "start"], ["path"])
    async def drag(
        self,
        box_id: str,
        *,
        end: action_drag_params.DragSimpleEnd | NotGiven = NOT_GIVEN,
        start: action_drag_params.DragSimpleStart | NotGiven = NOT_GIVEN,
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        path: Iterable[action_drag_params.DragAdvancedPath] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionDragResponse:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionDragResponse,
            await self._post(
                f"/boxes/{box_id}/actions/drag",
                body=await async_maybe_transform(
                    {
                        "end": end,
                        "start": start,
                        "duration": duration,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                        "path": path,
                    },
                    action_drag_params.ActionDragParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionDragResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def extract(
        self,
        box_id: str,
        *,
        instruction: str,
        schema: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/extract",
            body=await async_maybe_transform(
                {
                    "instruction": instruction,
                    "schema": schema,
                },
                action_extract_params.ActionExtractParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionExtractResponse,
        )

    @overload
    async def long_press(
        self,
        box_id: str,
        *,
        x: float,
        y: float,
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def long_press(
        self,
        box_id: str,
        *,
        target: str,
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionLongPressResponse:
        """
        Perform a long press action at specified coordinates for a specified duration.
        Useful for triggering context menus, drag operations, or other long-press
        interactions.

        Args:
          target: Describe the target to operate using natural language, e.g., 'Chrome icon',
              'login button'

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["x", "y"], ["target"])
    async def long_press(
        self,
        box_id: str,
        *,
        x: float | NotGiven = NOT_GIVEN,
        y: float | NotGiven = NOT_GIVEN,
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        target: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionLongPressResponse:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionLongPressResponse,
            await self._post(
                f"/boxes/{box_id}/actions/long-press",
                body=await async_maybe_transform(
                    {
                        "x": x,
                        "y": y,
                        "duration": duration,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                        "target": target,
                    },
                    action_long_press_params.ActionLongPressParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionLongPressResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def move(
        self,
        box_id: str,
        *,
        x: float,
        y: float,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionMoveResponse:
        """
        Move to position

        Args:
          x: X coordinate to move to

          y: Y coordinate to move to

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionMoveResponse,
            await self._post(
                f"/boxes/{box_id}/actions/move",
                body=await async_maybe_transform(
                    {
                        "x": x,
                        "y": y,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                    },
                    action_move_params.ActionMoveParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionMoveResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def press_button(
        self,
        box_id: str,
        *,
        buttons: List[Literal["power", "volumeUp", "volumeDown", "volumeMute", "home", "back", "menu", "appSwitch"]],
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionPressButtonResponse:
        """
        Press device buttons like power, volume, home, back, etc.

        Args:
          buttons: Button to press

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionPressButtonResponse,
            await self._post(
                f"/boxes/{box_id}/actions/press-button",
                body=await async_maybe_transform(
                    {
                        "buttons": buttons,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                    },
                    action_press_button_params.ActionPressButtonParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionPressButtonResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def press_key(
        self,
        box_id: str,
        *,
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
        ],
        combination: bool | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionPressKeyResponse:
        """
        Simulates pressing a specific key by triggering the complete keyboard key event
        chain (keydown, keypress, keyup). Use this to activate keyboard key event
        listeners such as shortcuts or form submissions.

        Args:
          keys: This is an array of keyboard keys to press. Supports cross-platform
              compatibility.

          combination: Whether to press keys as combination (simultaneously) or sequentially. When
              true, all keys are pressed together as a shortcut (e.g., Ctrl+C). When false,
              keys are pressed one by one in sequence.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionPressKeyResponse,
            await self._post(
                f"/boxes/{box_id}/actions/press-key",
                body=await async_maybe_transform(
                    {
                        "keys": keys,
                        "combination": combination,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                    },
                    action_press_key_params.ActionPressKeyParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionPressKeyResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def recording_start(
        self,
        box_id: str,
        *,
        duration: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Start recording the box screen.

        Only one recording can be active at a time. If a
        recording is already in progress, starting a new recording will stop the
        previous one and keep only the latest recording.

        Args:
          duration: Duration of the recording. Default is 30m, max is 30m. The recording will
              automatically stop when the duration time is reached.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Maximum allowed: 30m

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/boxes/{box_id}/actions/recording/start",
            body=await async_maybe_transform(
                {"duration": duration}, action_recording_start_params.ActionRecordingStartParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def recording_stop(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionRecordingStopResponse:
        """
        Stop recording the box screen

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/recording/stop",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionRecordingStopResponse,
        )

    async def screen_layout(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionScreenLayoutResponse:
        """Get the current structured screen layout information.

        This endpoint returns
        detailed structural information about the UI elements currently displayed on the
        screen, which can be used for UI automation, element analysis, and accessibility
        purposes. The format varies by box type: Android boxes return XML format with
        detailed UI hierarchy information including element bounds, text content,
        resource IDs, and properties, while other box types may return different
        structured formats.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._get(
            f"/boxes/{box_id}/actions/screen-layout",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionScreenLayoutResponse,
        )

    async def screen_rotation(
        self,
        box_id: str,
        *,
        orientation: Literal["portrait", "landscapeLeft", "portraitUpsideDown", "landscapeRight"],
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionScreenRotationResponse:
        """Rotate the screen orientation.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionScreenRotationResponse,
            await self._post(
                f"/boxes/{box_id}/actions/screen-rotation",
                body=await async_maybe_transform(
                    {
                        "orientation": orientation,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                    },
                    action_screen_rotation_params.ActionScreenRotationParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionScreenRotationResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def screenshot(
        self,
        box_id: str,
        *,
        clip: action_screenshot_params.Clip | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionScreenshotResponse:
        """
        Take screenshot

        Args:
          clip: Clipping region for screenshot capture

          output_format: Type of the URI. default is base64.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/screenshot",
            body=await async_maybe_transform(
                {
                    "clip": clip,
                    "output_format": output_format,
                },
                action_screenshot_params.ActionScreenshotParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionScreenshotResponse,
        )

    @overload
    async def scroll(
        self,
        box_id: str,
        *,
        scroll_x: float,
        scroll_y: float,
        x: float,
        y: float,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionScrollResponse:
        """Performs a scroll action.

        Supports both advanced scroll with coordinates and
        simple scroll with direction.

        Args:
          scroll_x: Horizontal scroll amount. Positive values scroll content rightward (reveals
              content on the left), negative values scroll content leftward (reveals content
              on the right).

          scroll_y: Vertical scroll amount. Positive values scroll content downward (reveals content
              above), negative values scroll content upward (reveals content below).

          x: X coordinate of the scroll position

          y: Y coordinate of the scroll position

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def scroll(
        self,
        box_id: str,
        *,
        direction: Literal["up", "down", "left", "right"],
        distance: Union[float, Literal["tiny", "short", "medium", "long"]] | NotGiven = NOT_GIVEN,
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionScrollResponse:
        """Performs a scroll action.

        Supports both advanced scroll with coordinates and
        simple scroll with direction.

        Args:
          direction: Direction to scroll. The scroll will be performed from the center of the screen
              towards this direction. 'up' scrolls content upward (reveals content below),
              'down' scrolls content downward (reveals content above), 'left' scrolls content
              leftward (reveals content on the right), 'right' scrolls content rightward
              (reveals content on the left).

          distance: Distance of the scroll. Can be either a number (in pixels) or a predefined enum
              value (tiny, short, medium, long). If not provided, the scroll will be performed
              from the center of the screen to the screen edge

          duration: Duration of the scroll

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 500ms

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["scroll_x", "scroll_y", "x", "y"], ["direction"])
    async def scroll(
        self,
        box_id: str,
        *,
        scroll_x: float | NotGiven = NOT_GIVEN,
        scroll_y: float | NotGiven = NOT_GIVEN,
        x: float | NotGiven = NOT_GIVEN,
        y: float | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        direction: Literal["up", "down", "left", "right"] | NotGiven = NOT_GIVEN,
        distance: Union[float, Literal["tiny", "short", "medium", "long"]] | NotGiven = NOT_GIVEN,
        duration: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionScrollResponse:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionScrollResponse,
            await self._post(
                f"/boxes/{box_id}/actions/scroll",
                body=await async_maybe_transform(
                    {
                        "scroll_x": scroll_x,
                        "scroll_y": scroll_y,
                        "x": x,
                        "y": y,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                        "direction": direction,
                        "distance": distance,
                        "duration": duration,
                    },
                    action_scroll_params.ActionScrollParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionScrollResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    @overload
    async def swipe(
        self,
        box_id: str,
        *,
        direction: Literal["up", "down", "left", "right", "upLeft", "upRight", "downLeft", "downRight"],
        distance: Union[float, Literal["tiny", "short", "medium", "long"]] | NotGiven = NOT_GIVEN,
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionSwipeResponse:
        """
        Performs a swipe in the specified direction

        Args:
          direction: Direction to swipe. The gesture will be performed from the center of the screen
              towards this direction.

          distance: Distance of the swipe. Can be either a number (in pixels) or a predefined enum
              value (tiny, short, medium, long). If not provided, the swipe will be performed
              from the center of the screen to the screen edge

          duration: Duration of the swipe

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 500ms

          include_screenshot: Whether to include screenshots in the action response. If false, the screenshot
              object will still be returned but with empty URIs. Default is false.

          location: Natural language description of the location where the swipe should originate.
              If not provided, the swipe will be performed from the center of the screen.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def swipe(
        self,
        box_id: str,
        *,
        end: action_swipe_params.SwipeAdvancedEnd,
        start: action_swipe_params.SwipeAdvancedStart,
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionSwipeResponse:
        """
        Performs a swipe in the specified direction

        Args:
          end: End point of the swipe path (coordinates or natural language)

          start: Start point of the swipe path (coordinates or natural language)

          duration: Duration of the swipe

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 500ms

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["direction"], ["end", "start"])
    async def swipe(
        self,
        box_id: str,
        *,
        direction: Literal["up", "down", "left", "right", "upLeft", "upRight", "downLeft", "downRight"]
        | NotGiven = NOT_GIVEN,
        distance: Union[float, Literal["tiny", "short", "medium", "long"]] | NotGiven = NOT_GIVEN,
        duration: str | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        end: action_swipe_params.SwipeAdvancedEnd | NotGiven = NOT_GIVEN,
        start: action_swipe_params.SwipeAdvancedStart | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionSwipeResponse:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionSwipeResponse,
            await self._post(
                f"/boxes/{box_id}/actions/swipe",
                body=await async_maybe_transform(
                    {
                        "direction": direction,
                        "distance": distance,
                        "duration": duration,
                        "include_screenshot": include_screenshot,
                        "location": location,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                        "end": end,
                        "start": start,
                    },
                    action_swipe_params.ActionSwipeParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionSwipeResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    @overload
    async def tap(
        self,
        box_id: str,
        *,
        x: float,
        y: float,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def tap(
        self,
        box_id: str,
        *,
        target: str,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTapResponse:
        """
        Tap action for Android devices using ADB input tap command

        Args:
          target: Describe the target to operate using natural language, e.g., 'login button' or
              'Chrome'.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["x", "y"], ["target"])
    async def tap(
        self,
        box_id: str,
        *,
        x: float | NotGiven = NOT_GIVEN,
        y: float | NotGiven = NOT_GIVEN,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        target: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTapResponse:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionTapResponse,
            await self._post(
                f"/boxes/{box_id}/actions/tap",
                body=await async_maybe_transform(
                    {
                        "x": x,
                        "y": y,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                        "target": target,
                    },
                    action_tap_params.ActionTapParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, ActionTapResponse),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def touch(
        self,
        box_id: str,
        *,
        points: Iterable[action_touch_params.Point],
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTouchResponse:
        """
        Touch

        Args:
          points: Array of touch points and their actions

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionTouchResponse,
            await self._post(
                f"/boxes/{box_id}/actions/touch",
                body=await async_maybe_transform(
                    {
                        "points": points,
                        "include_screenshot": include_screenshot,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "screenshot_delay": screenshot_delay,
                    },
                    action_touch_params.ActionTouchParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionTouchResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def type(
        self,
        box_id: str,
        *,
        text: str,
        include_screenshot: bool | NotGiven = NOT_GIVEN,
        mode: Literal["append", "replace"] | NotGiven = NOT_GIVEN,
        output_format: Literal["base64", "storageKey"] | NotGiven = NOT_GIVEN,
        presigned_expires_in: str | NotGiven = NOT_GIVEN,
        press_enter: bool | NotGiven = NOT_GIVEN,
        screenshot_delay: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeResponse:
        """
        Directly inputs text content without triggering physical key events (keydown,
        etc.), ideal for quickly filling large amounts of text when intermediate input
        events aren't needed.

        Args:
          text: Text to type

          include_screenshot: Whether to include screenshots in the action response. If false, the screenshot
              object will still be returned but with empty URIs. Default is false.

          mode: Text input mode: 'append' to add text to existing content, 'replace' to replace
              all existing text

          output_format: Type of the URI. default is base64.

          presigned_expires_in: Presigned url expires in. Only takes effect when outputFormat is storageKey.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          press_enter: Whether to press Enter after typing the text

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            ActionTypeResponse,
            await self._post(
                f"/boxes/{box_id}/actions/type",
                body=await async_maybe_transform(
                    {
                        "text": text,
                        "include_screenshot": include_screenshot,
                        "mode": mode,
                        "output_format": output_format,
                        "presigned_expires_in": presigned_expires_in,
                        "press_enter": press_enter,
                        "screenshot_delay": screenshot_delay,
                    },
                    action_type_params.ActionTypeParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ActionTypeResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class ActionsResourceWithRawResponse:
    def __init__(self, actions: ActionsResource) -> None:
        self._actions = actions

        self.ai = to_raw_response_wrapper(
            actions.ai,
        )
        self.click = to_raw_response_wrapper(
            actions.click,
        )
        self.drag = to_raw_response_wrapper(
            actions.drag,
        )
        self.extract = to_raw_response_wrapper(
            actions.extract,
        )
        self.long_press = to_raw_response_wrapper(
            actions.long_press,
        )
        self.move = to_raw_response_wrapper(
            actions.move,
        )
        self.press_button = to_raw_response_wrapper(
            actions.press_button,
        )
        self.press_key = to_raw_response_wrapper(
            actions.press_key,
        )
        self.recording_start = to_raw_response_wrapper(
            actions.recording_start,
        )
        self.recording_stop = to_raw_response_wrapper(
            actions.recording_stop,
        )
        self.screen_layout = to_raw_response_wrapper(
            actions.screen_layout,
        )
        self.screen_rotation = to_raw_response_wrapper(
            actions.screen_rotation,
        )
        self.screenshot = to_raw_response_wrapper(
            actions.screenshot,
        )
        self.scroll = to_raw_response_wrapper(
            actions.scroll,
        )
        self.swipe = to_raw_response_wrapper(
            actions.swipe,
        )
        self.tap = to_raw_response_wrapper(
            actions.tap,
        )
        self.touch = to_raw_response_wrapper(
            actions.touch,
        )
        self.type = to_raw_response_wrapper(
            actions.type,
        )


class AsyncActionsResourceWithRawResponse:
    def __init__(self, actions: AsyncActionsResource) -> None:
        self._actions = actions

        self.ai = async_to_raw_response_wrapper(
            actions.ai,
        )
        self.click = async_to_raw_response_wrapper(
            actions.click,
        )
        self.drag = async_to_raw_response_wrapper(
            actions.drag,
        )
        self.extract = async_to_raw_response_wrapper(
            actions.extract,
        )
        self.long_press = async_to_raw_response_wrapper(
            actions.long_press,
        )
        self.move = async_to_raw_response_wrapper(
            actions.move,
        )
        self.press_button = async_to_raw_response_wrapper(
            actions.press_button,
        )
        self.press_key = async_to_raw_response_wrapper(
            actions.press_key,
        )
        self.recording_start = async_to_raw_response_wrapper(
            actions.recording_start,
        )
        self.recording_stop = async_to_raw_response_wrapper(
            actions.recording_stop,
        )
        self.screen_layout = async_to_raw_response_wrapper(
            actions.screen_layout,
        )
        self.screen_rotation = async_to_raw_response_wrapper(
            actions.screen_rotation,
        )
        self.screenshot = async_to_raw_response_wrapper(
            actions.screenshot,
        )
        self.scroll = async_to_raw_response_wrapper(
            actions.scroll,
        )
        self.swipe = async_to_raw_response_wrapper(
            actions.swipe,
        )
        self.tap = async_to_raw_response_wrapper(
            actions.tap,
        )
        self.touch = async_to_raw_response_wrapper(
            actions.touch,
        )
        self.type = async_to_raw_response_wrapper(
            actions.type,
        )


class ActionsResourceWithStreamingResponse:
    def __init__(self, actions: ActionsResource) -> None:
        self._actions = actions

        self.ai = to_streamed_response_wrapper(
            actions.ai,
        )
        self.click = to_streamed_response_wrapper(
            actions.click,
        )
        self.drag = to_streamed_response_wrapper(
            actions.drag,
        )
        self.extract = to_streamed_response_wrapper(
            actions.extract,
        )
        self.long_press = to_streamed_response_wrapper(
            actions.long_press,
        )
        self.move = to_streamed_response_wrapper(
            actions.move,
        )
        self.press_button = to_streamed_response_wrapper(
            actions.press_button,
        )
        self.press_key = to_streamed_response_wrapper(
            actions.press_key,
        )
        self.recording_start = to_streamed_response_wrapper(
            actions.recording_start,
        )
        self.recording_stop = to_streamed_response_wrapper(
            actions.recording_stop,
        )
        self.screen_layout = to_streamed_response_wrapper(
            actions.screen_layout,
        )
        self.screen_rotation = to_streamed_response_wrapper(
            actions.screen_rotation,
        )
        self.screenshot = to_streamed_response_wrapper(
            actions.screenshot,
        )
        self.scroll = to_streamed_response_wrapper(
            actions.scroll,
        )
        self.swipe = to_streamed_response_wrapper(
            actions.swipe,
        )
        self.tap = to_streamed_response_wrapper(
            actions.tap,
        )
        self.touch = to_streamed_response_wrapper(
            actions.touch,
        )
        self.type = to_streamed_response_wrapper(
            actions.type,
        )


class AsyncActionsResourceWithStreamingResponse:
    def __init__(self, actions: AsyncActionsResource) -> None:
        self._actions = actions

        self.ai = async_to_streamed_response_wrapper(
            actions.ai,
        )
        self.click = async_to_streamed_response_wrapper(
            actions.click,
        )
        self.drag = async_to_streamed_response_wrapper(
            actions.drag,
        )
        self.extract = async_to_streamed_response_wrapper(
            actions.extract,
        )
        self.long_press = async_to_streamed_response_wrapper(
            actions.long_press,
        )
        self.move = async_to_streamed_response_wrapper(
            actions.move,
        )
        self.press_button = async_to_streamed_response_wrapper(
            actions.press_button,
        )
        self.press_key = async_to_streamed_response_wrapper(
            actions.press_key,
        )
        self.recording_start = async_to_streamed_response_wrapper(
            actions.recording_start,
        )
        self.recording_stop = async_to_streamed_response_wrapper(
            actions.recording_stop,
        )
        self.screen_layout = async_to_streamed_response_wrapper(
            actions.screen_layout,
        )
        self.screen_rotation = async_to_streamed_response_wrapper(
            actions.screen_rotation,
        )
        self.screenshot = async_to_streamed_response_wrapper(
            actions.screenshot,
        )
        self.scroll = async_to_streamed_response_wrapper(
            actions.scroll,
        )
        self.swipe = async_to_streamed_response_wrapper(
            actions.swipe,
        )
        self.tap = async_to_streamed_response_wrapper(
            actions.tap,
        )
        self.touch = async_to_streamed_response_wrapper(
            actions.touch,
        )
        self.type = async_to_streamed_response_wrapper(
            actions.type,
        )
