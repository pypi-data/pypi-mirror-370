# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, List, Union, cast
from typing_extensions import Literal

import httpx

from .fs import (
    FsResource,
    AsyncFsResource,
    FsResourceWithRawResponse,
    AsyncFsResourceWithRawResponse,
    FsResourceWithStreamingResponse,
    AsyncFsResourceWithStreamingResponse,
)
from .media import (
    MediaResource,
    AsyncMediaResource,
    MediaResourceWithRawResponse,
    AsyncMediaResourceWithRawResponse,
    MediaResourceWithStreamingResponse,
    AsyncMediaResourceWithStreamingResponse,
)
from .proxy import (
    ProxyResource,
    AsyncProxyResource,
    ProxyResourceWithRawResponse,
    AsyncProxyResourceWithRawResponse,
    ProxyResourceWithStreamingResponse,
    AsyncProxyResourceWithStreamingResponse,
)
from .actions import (
    ActionsResource,
    AsyncActionsResource,
    ActionsResourceWithRawResponse,
    AsyncActionsResourceWithRawResponse,
    ActionsResourceWithStreamingResponse,
    AsyncActionsResourceWithStreamingResponse,
)
from .android import (
    AndroidResource,
    AsyncAndroidResource,
    AndroidResourceWithRawResponse,
    AsyncAndroidResourceWithRawResponse,
    AndroidResourceWithStreamingResponse,
    AsyncAndroidResourceWithStreamingResponse,
)
from .browser import (
    BrowserResource,
    AsyncBrowserResource,
    BrowserResourceWithRawResponse,
    AsyncBrowserResourceWithRawResponse,
    BrowserResourceWithStreamingResponse,
    AsyncBrowserResourceWithStreamingResponse,
)
from .storage import (
    StorageResource,
    AsyncStorageResource,
    StorageResourceWithRawResponse,
    AsyncStorageResourceWithRawResponse,
    StorageResourceWithStreamingResponse,
    AsyncStorageResourceWithStreamingResponse,
)
from ...._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ....types.v1 import (
    box_list_params,
    box_stop_params,
    box_start_params,
    box_run_code_params,
    box_terminate_params,
    box_create_linux_params,
    box_live_view_url_params,
    box_create_android_params,
    box_execute_commands_params,
    box_web_terminal_url_params,
)
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v1.linux_box import LinuxBox
from ....types.v1.android_box import AndroidBox
from ....types.v1.box_list_response import BoxListResponse
from ....types.v1.box_stop_response import BoxStopResponse
from ....types.v1.box_start_response import BoxStartResponse
from ....types.v1.box_display_response import BoxDisplayResponse
from ....types.v1.box_retrieve_response import BoxRetrieveResponse
from ....types.v1.box_run_code_response import BoxRunCodeResponse
from ....types.v1.box_live_view_url_response import BoxLiveViewURLResponse
from ....types.v1.box_websocket_url_response import BoxWebsocketURLResponse
from ....types.v1.box_execute_commands_response import BoxExecuteCommandsResponse
from ....types.v1.box_web_terminal_url_response import BoxWebTerminalURLResponse

__all__ = ["BoxesResource", "AsyncBoxesResource"]


class BoxesResource(SyncAPIResource):
    @cached_property
    def storage(self) -> StorageResource:
        return StorageResource(self._client)

    @cached_property
    def actions(self) -> ActionsResource:
        return ActionsResource(self._client)

    @cached_property
    def proxy(self) -> ProxyResource:
        return ProxyResource(self._client)

    @cached_property
    def media(self) -> MediaResource:
        return MediaResource(self._client)

    @cached_property
    def fs(self) -> FsResource:
        return FsResource(self._client)

    @cached_property
    def browser(self) -> BrowserResource:
        return BrowserResource(self._client)

    @cached_property
    def android(self) -> AndroidResource:
        return AndroidResource(self._client)

    @cached_property
    def with_raw_response(self) -> BoxesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return BoxesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BoxesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return BoxesResourceWithStreamingResponse(self)

    def retrieve(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxRetrieveResponse:
        """
        Get box

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            BoxRetrieveResponse,
            self._get(
                f"/boxes/{box_id}",
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, BoxRetrieveResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def list(
        self,
        *,
        device_type: str | NotGiven = NOT_GIVEN,
        labels: object | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        status: List[Literal["all", "pending", "running", "error", "terminated"]] | NotGiven = NOT_GIVEN,
        type: List[Literal["all", "linux", "android"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxListResponse:
        """
        List box

        Args:
          device_type: Filter boxes by their device type (virtual, physical)

          labels: Filter boxes by their labels. Labels are key-value pairs that help identify and
              categorize boxes. Use this to filter boxes that match specific label criteria.
              For example, you can filter by project, environment, team, or any custom labels
              you've added to your boxes.

          page: Page number

          page_size: Page size

          status: Filter boxes by their current status (pending, running, stopped, error,
              terminated, all). Must be an array of statuses. Use 'all' to get boxes with any
              status.

          type: Filter boxes by their type (linux, android, all). Must be an array of types. Use
              'all' to get boxes of any type.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/boxes",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "device_type": device_type,
                        "labels": labels,
                        "page": page,
                        "page_size": page_size,
                        "status": status,
                        "type": type,
                    },
                    box_list_params.BoxListParams,
                ),
            ),
            cast_to=BoxListResponse,
        )

    def create_android(
        self,
        *,
        config: box_create_android_params.Config | NotGiven = NOT_GIVEN,
        api_timeout: str | NotGiven = NOT_GIVEN,
        wait: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidBox:
        """
        Create android box

        Args:
          config: Configuration for a Android box instance

          api_timeout: Timeout for waiting the box to transition from pending to running state, default
              is 30s. If the box doesn't reach running state within this timeout, the API will
              return HTTP status code 408. The timed-out box will be automatically deleted and
              will not count towards your quota.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30s Maximum allowed: 5m

          wait: Wait for the box operation to be completed, default is true

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/boxes/android",
            body=maybe_transform(
                {
                    "config": config,
                    "api_timeout": api_timeout,
                    "wait": wait,
                },
                box_create_android_params.BoxCreateAndroidParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AndroidBox,
        )

    def create_linux(
        self,
        *,
        config: box_create_linux_params.Config | NotGiven = NOT_GIVEN,
        api_timeout: str | NotGiven = NOT_GIVEN,
        wait: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LinuxBox:
        """
        Create linux box

        Args:
          config: Configuration for a Linux box instance

          api_timeout: Timeout for waiting the box to transition from pending to running state, default
              is 30s. If the box doesn't reach running state within this timeout, the API will
              return HTTP status code 408. The timed-out box will be automatically deleted and
              will not count towards your quota.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30s Maximum allowed: 5m

          wait: Wait for the box operation to be completed, default is true

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/boxes/linux",
            body=maybe_transform(
                {
                    "config": config,
                    "api_timeout": api_timeout,
                    "wait": wait,
                },
                box_create_linux_params.BoxCreateLinuxParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LinuxBox,
        )

    def display(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxDisplayResponse:
        """Retrieve the current display properties for a running box.

        This endpoint
        provides details about the box's screen resolution, orientation, and other
        visual properties

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._get(
            f"/boxes/{box_id}/display",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BoxDisplayResponse,
        )

    def execute_commands(
        self,
        box_id: str,
        *,
        commands: Union[str, List[str]],
        envs: object | NotGiven = NOT_GIVEN,
        api_timeout: str | NotGiven = NOT_GIVEN,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxExecuteCommandsResponse:
        """Execute a command on a running box.

        This endpoint allows you to send commands to
        the box and receive the output

        Args:
          commands: The command to run. Can be a single string or an array of strings

          envs: The environment variables to run the command

          api_timeout: The timeout of the command. If the command times out, the exit code will be 124.
              For example: 'timeout 5s sleep 10s' will result in exit code 124.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30s

          working_dir: The working directory of the command. It not provided, the command will be run
              in the `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/commands",
            body=maybe_transform(
                {
                    "commands": commands,
                    "envs": envs,
                    "api_timeout": api_timeout,
                    "working_dir": working_dir,
                },
                box_execute_commands_params.BoxExecuteCommandsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BoxExecuteCommandsResponse,
        )

    def live_view_url(
        self,
        box_id: str,
        *,
        expires_in: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxLiveViewURLResponse:
        """
        This endpoint allows you to generate a pre-signed URL for accessing the live
        view of a running box. The URL is valid for a limited time and can be used to
        view the box's live stream

        Args:
          expires_in: The live view will be alive for the given duration

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 180m

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/live-view-url",
            body=maybe_transform({"expires_in": expires_in}, box_live_view_url_params.BoxLiveViewURLParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BoxLiveViewURLResponse,
        )

    def run_code(
        self,
        box_id: str,
        *,
        code: str,
        argv: List[str] | NotGiven = NOT_GIVEN,
        envs: object | NotGiven = NOT_GIVEN,
        language: Literal["bash", "python", "typescript"] | NotGiven = NOT_GIVEN,
        api_timeout: str | NotGiven = NOT_GIVEN,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxRunCodeResponse:
        """
        Run code on the box

        Args:
          code: The code to run

          argv: The arguments to run the code. For example, if you want to run "python index.py
              --help", you should pass ["--help"] as arguments.

          envs: The environment variables to run the code

          language: The language of the code.

          api_timeout: The timeout of the code execution. If the code execution times out, the exit
              code will be 124.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30s

          working_dir: The working directory of the code. It not provided, the code will be run in the
              `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/run-code",
            body=maybe_transform(
                {
                    "code": code,
                    "argv": argv,
                    "envs": envs,
                    "language": language,
                    "api_timeout": api_timeout,
                    "working_dir": working_dir,
                },
                box_run_code_params.BoxRunCodeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BoxRunCodeResponse,
        )

    def start(
        self,
        box_id: str,
        *,
        wait: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxStartResponse:
        """
        Start box

        Args:
          wait: Wait for the box operation to be completed, default is true

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            BoxStartResponse,
            self._post(
                f"/boxes/{box_id}/start",
                body=maybe_transform({"wait": wait}, box_start_params.BoxStartParams),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, BoxStartResponse),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def stop(
        self,
        box_id: str,
        *,
        wait: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxStopResponse:
        """
        Stop box

        Args:
          wait: Wait for the box operation to be completed, default is true

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            BoxStopResponse,
            self._post(
                f"/boxes/{box_id}/stop",
                body=maybe_transform({"wait": wait}, box_stop_params.BoxStopParams),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, BoxStopResponse),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def terminate(
        self,
        box_id: str,
        *,
        wait: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Terminate a running box.

        This action will stop the box and release its resources

        Args:
          wait: Wait for the box operation to be completed, default is true

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/boxes/{box_id}/terminate",
            body=maybe_transform({"wait": wait}, box_terminate_params.BoxTerminateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def web_terminal_url(
        self,
        box_id: str,
        *,
        expires_in: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxWebTerminalURLResponse:
        """
        This endpoint allows you to generate a pre-signed URL for accessing the web
        terminal of a running box. The URL is valid for a limited time and can be used
        to access the box's terminal interface

        Args:
          expires_in: The web terminal will be alive for the given duration

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 180m

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/web-terminal-url",
            body=maybe_transform({"expires_in": expires_in}, box_web_terminal_url_params.BoxWebTerminalURLParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BoxWebTerminalURLResponse,
        )

    def websocket_url(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxWebsocketURLResponse:
        """Get the websocket url for the box.

        This endpoint provides the WebSocket URLs for
        executing shell commands and running code snippets in the box environment. These
        URLs allow real-time communication and data exchange with the box, enabling
        interactive terminal sessions and code execution.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._get(
            f"/boxes/{box_id}/websocket-url",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BoxWebsocketURLResponse,
        )


class AsyncBoxesResource(AsyncAPIResource):
    @cached_property
    def storage(self) -> AsyncStorageResource:
        return AsyncStorageResource(self._client)

    @cached_property
    def actions(self) -> AsyncActionsResource:
        return AsyncActionsResource(self._client)

    @cached_property
    def proxy(self) -> AsyncProxyResource:
        return AsyncProxyResource(self._client)

    @cached_property
    def media(self) -> AsyncMediaResource:
        return AsyncMediaResource(self._client)

    @cached_property
    def fs(self) -> AsyncFsResource:
        return AsyncFsResource(self._client)

    @cached_property
    def browser(self) -> AsyncBrowserResource:
        return AsyncBrowserResource(self._client)

    @cached_property
    def android(self) -> AsyncAndroidResource:
        return AsyncAndroidResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncBoxesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncBoxesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBoxesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return AsyncBoxesResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxRetrieveResponse:
        """
        Get box

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            BoxRetrieveResponse,
            await self._get(
                f"/boxes/{box_id}",
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, BoxRetrieveResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def list(
        self,
        *,
        device_type: str | NotGiven = NOT_GIVEN,
        labels: object | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        status: List[Literal["all", "pending", "running", "error", "terminated"]] | NotGiven = NOT_GIVEN,
        type: List[Literal["all", "linux", "android"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxListResponse:
        """
        List box

        Args:
          device_type: Filter boxes by their device type (virtual, physical)

          labels: Filter boxes by their labels. Labels are key-value pairs that help identify and
              categorize boxes. Use this to filter boxes that match specific label criteria.
              For example, you can filter by project, environment, team, or any custom labels
              you've added to your boxes.

          page: Page number

          page_size: Page size

          status: Filter boxes by their current status (pending, running, stopped, error,
              terminated, all). Must be an array of statuses. Use 'all' to get boxes with any
              status.

          type: Filter boxes by their type (linux, android, all). Must be an array of types. Use
              'all' to get boxes of any type.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/boxes",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "device_type": device_type,
                        "labels": labels,
                        "page": page,
                        "page_size": page_size,
                        "status": status,
                        "type": type,
                    },
                    box_list_params.BoxListParams,
                ),
            ),
            cast_to=BoxListResponse,
        )

    async def create_android(
        self,
        *,
        config: box_create_android_params.Config | NotGiven = NOT_GIVEN,
        api_timeout: str | NotGiven = NOT_GIVEN,
        wait: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidBox:
        """
        Create android box

        Args:
          config: Configuration for a Android box instance

          api_timeout: Timeout for waiting the box to transition from pending to running state, default
              is 30s. If the box doesn't reach running state within this timeout, the API will
              return HTTP status code 408. The timed-out box will be automatically deleted and
              will not count towards your quota.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30s Maximum allowed: 5m

          wait: Wait for the box operation to be completed, default is true

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/boxes/android",
            body=await async_maybe_transform(
                {
                    "config": config,
                    "api_timeout": api_timeout,
                    "wait": wait,
                },
                box_create_android_params.BoxCreateAndroidParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AndroidBox,
        )

    async def create_linux(
        self,
        *,
        config: box_create_linux_params.Config | NotGiven = NOT_GIVEN,
        api_timeout: str | NotGiven = NOT_GIVEN,
        wait: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LinuxBox:
        """
        Create linux box

        Args:
          config: Configuration for a Linux box instance

          api_timeout: Timeout for waiting the box to transition from pending to running state, default
              is 30s. If the box doesn't reach running state within this timeout, the API will
              return HTTP status code 408. The timed-out box will be automatically deleted and
              will not count towards your quota.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30s Maximum allowed: 5m

          wait: Wait for the box operation to be completed, default is true

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/boxes/linux",
            body=await async_maybe_transform(
                {
                    "config": config,
                    "api_timeout": api_timeout,
                    "wait": wait,
                },
                box_create_linux_params.BoxCreateLinuxParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LinuxBox,
        )

    async def display(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxDisplayResponse:
        """Retrieve the current display properties for a running box.

        This endpoint
        provides details about the box's screen resolution, orientation, and other
        visual properties

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._get(
            f"/boxes/{box_id}/display",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BoxDisplayResponse,
        )

    async def execute_commands(
        self,
        box_id: str,
        *,
        commands: Union[str, List[str]],
        envs: object | NotGiven = NOT_GIVEN,
        api_timeout: str | NotGiven = NOT_GIVEN,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxExecuteCommandsResponse:
        """Execute a command on a running box.

        This endpoint allows you to send commands to
        the box and receive the output

        Args:
          commands: The command to run. Can be a single string or an array of strings

          envs: The environment variables to run the command

          api_timeout: The timeout of the command. If the command times out, the exit code will be 124.
              For example: 'timeout 5s sleep 10s' will result in exit code 124.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30s

          working_dir: The working directory of the command. It not provided, the command will be run
              in the `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/commands",
            body=await async_maybe_transform(
                {
                    "commands": commands,
                    "envs": envs,
                    "api_timeout": api_timeout,
                    "working_dir": working_dir,
                },
                box_execute_commands_params.BoxExecuteCommandsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BoxExecuteCommandsResponse,
        )

    async def live_view_url(
        self,
        box_id: str,
        *,
        expires_in: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxLiveViewURLResponse:
        """
        This endpoint allows you to generate a pre-signed URL for accessing the live
        view of a running box. The URL is valid for a limited time and can be used to
        view the box's live stream

        Args:
          expires_in: The live view will be alive for the given duration

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 180m

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/live-view-url",
            body=await async_maybe_transform({"expires_in": expires_in}, box_live_view_url_params.BoxLiveViewURLParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BoxLiveViewURLResponse,
        )

    async def run_code(
        self,
        box_id: str,
        *,
        code: str,
        argv: List[str] | NotGiven = NOT_GIVEN,
        envs: object | NotGiven = NOT_GIVEN,
        language: Literal["bash", "python", "typescript"] | NotGiven = NOT_GIVEN,
        api_timeout: str | NotGiven = NOT_GIVEN,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxRunCodeResponse:
        """
        Run code on the box

        Args:
          code: The code to run

          argv: The arguments to run the code. For example, if you want to run "python index.py
              --help", you should pass ["--help"] as arguments.

          envs: The environment variables to run the code

          language: The language of the code.

          api_timeout: The timeout of the code execution. If the code execution times out, the exit
              code will be 124.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30s

          working_dir: The working directory of the code. It not provided, the code will be run in the
              `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/run-code",
            body=await async_maybe_transform(
                {
                    "code": code,
                    "argv": argv,
                    "envs": envs,
                    "language": language,
                    "api_timeout": api_timeout,
                    "working_dir": working_dir,
                },
                box_run_code_params.BoxRunCodeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BoxRunCodeResponse,
        )

    async def start(
        self,
        box_id: str,
        *,
        wait: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxStartResponse:
        """
        Start box

        Args:
          wait: Wait for the box operation to be completed, default is true

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            BoxStartResponse,
            await self._post(
                f"/boxes/{box_id}/start",
                body=await async_maybe_transform({"wait": wait}, box_start_params.BoxStartParams),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, BoxStartResponse),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def stop(
        self,
        box_id: str,
        *,
        wait: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxStopResponse:
        """
        Stop box

        Args:
          wait: Wait for the box operation to be completed, default is true

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            BoxStopResponse,
            await self._post(
                f"/boxes/{box_id}/stop",
                body=await async_maybe_transform({"wait": wait}, box_stop_params.BoxStopParams),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, BoxStopResponse),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def terminate(
        self,
        box_id: str,
        *,
        wait: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Terminate a running box.

        This action will stop the box and release its resources

        Args:
          wait: Wait for the box operation to be completed, default is true

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/boxes/{box_id}/terminate",
            body=await async_maybe_transform({"wait": wait}, box_terminate_params.BoxTerminateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def web_terminal_url(
        self,
        box_id: str,
        *,
        expires_in: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxWebTerminalURLResponse:
        """
        This endpoint allows you to generate a pre-signed URL for accessing the web
        terminal of a running box. The URL is valid for a limited time and can be used
        to access the box's terminal interface

        Args:
          expires_in: The web terminal will be alive for the given duration

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 180m

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/web-terminal-url",
            body=await async_maybe_transform(
                {"expires_in": expires_in}, box_web_terminal_url_params.BoxWebTerminalURLParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BoxWebTerminalURLResponse,
        )

    async def websocket_url(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BoxWebsocketURLResponse:
        """Get the websocket url for the box.

        This endpoint provides the WebSocket URLs for
        executing shell commands and running code snippets in the box environment. These
        URLs allow real-time communication and data exchange with the box, enabling
        interactive terminal sessions and code execution.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._get(
            f"/boxes/{box_id}/websocket-url",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BoxWebsocketURLResponse,
        )


class BoxesResourceWithRawResponse:
    def __init__(self, boxes: BoxesResource) -> None:
        self._boxes = boxes

        self.retrieve = to_raw_response_wrapper(
            boxes.retrieve,
        )
        self.list = to_raw_response_wrapper(
            boxes.list,
        )
        self.create_android = to_raw_response_wrapper(
            boxes.create_android,
        )
        self.create_linux = to_raw_response_wrapper(
            boxes.create_linux,
        )
        self.display = to_raw_response_wrapper(
            boxes.display,
        )
        self.execute_commands = to_raw_response_wrapper(
            boxes.execute_commands,
        )
        self.live_view_url = to_raw_response_wrapper(
            boxes.live_view_url,
        )
        self.run_code = to_raw_response_wrapper(
            boxes.run_code,
        )
        self.start = to_raw_response_wrapper(
            boxes.start,
        )
        self.stop = to_raw_response_wrapper(
            boxes.stop,
        )
        self.terminate = to_raw_response_wrapper(
            boxes.terminate,
        )
        self.web_terminal_url = to_raw_response_wrapper(
            boxes.web_terminal_url,
        )
        self.websocket_url = to_raw_response_wrapper(
            boxes.websocket_url,
        )

    @cached_property
    def storage(self) -> StorageResourceWithRawResponse:
        return StorageResourceWithRawResponse(self._boxes.storage)

    @cached_property
    def actions(self) -> ActionsResourceWithRawResponse:
        return ActionsResourceWithRawResponse(self._boxes.actions)

    @cached_property
    def proxy(self) -> ProxyResourceWithRawResponse:
        return ProxyResourceWithRawResponse(self._boxes.proxy)

    @cached_property
    def media(self) -> MediaResourceWithRawResponse:
        return MediaResourceWithRawResponse(self._boxes.media)

    @cached_property
    def fs(self) -> FsResourceWithRawResponse:
        return FsResourceWithRawResponse(self._boxes.fs)

    @cached_property
    def browser(self) -> BrowserResourceWithRawResponse:
        return BrowserResourceWithRawResponse(self._boxes.browser)

    @cached_property
    def android(self) -> AndroidResourceWithRawResponse:
        return AndroidResourceWithRawResponse(self._boxes.android)


class AsyncBoxesResourceWithRawResponse:
    def __init__(self, boxes: AsyncBoxesResource) -> None:
        self._boxes = boxes

        self.retrieve = async_to_raw_response_wrapper(
            boxes.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            boxes.list,
        )
        self.create_android = async_to_raw_response_wrapper(
            boxes.create_android,
        )
        self.create_linux = async_to_raw_response_wrapper(
            boxes.create_linux,
        )
        self.display = async_to_raw_response_wrapper(
            boxes.display,
        )
        self.execute_commands = async_to_raw_response_wrapper(
            boxes.execute_commands,
        )
        self.live_view_url = async_to_raw_response_wrapper(
            boxes.live_view_url,
        )
        self.run_code = async_to_raw_response_wrapper(
            boxes.run_code,
        )
        self.start = async_to_raw_response_wrapper(
            boxes.start,
        )
        self.stop = async_to_raw_response_wrapper(
            boxes.stop,
        )
        self.terminate = async_to_raw_response_wrapper(
            boxes.terminate,
        )
        self.web_terminal_url = async_to_raw_response_wrapper(
            boxes.web_terminal_url,
        )
        self.websocket_url = async_to_raw_response_wrapper(
            boxes.websocket_url,
        )

    @cached_property
    def storage(self) -> AsyncStorageResourceWithRawResponse:
        return AsyncStorageResourceWithRawResponse(self._boxes.storage)

    @cached_property
    def actions(self) -> AsyncActionsResourceWithRawResponse:
        return AsyncActionsResourceWithRawResponse(self._boxes.actions)

    @cached_property
    def proxy(self) -> AsyncProxyResourceWithRawResponse:
        return AsyncProxyResourceWithRawResponse(self._boxes.proxy)

    @cached_property
    def media(self) -> AsyncMediaResourceWithRawResponse:
        return AsyncMediaResourceWithRawResponse(self._boxes.media)

    @cached_property
    def fs(self) -> AsyncFsResourceWithRawResponse:
        return AsyncFsResourceWithRawResponse(self._boxes.fs)

    @cached_property
    def browser(self) -> AsyncBrowserResourceWithRawResponse:
        return AsyncBrowserResourceWithRawResponse(self._boxes.browser)

    @cached_property
    def android(self) -> AsyncAndroidResourceWithRawResponse:
        return AsyncAndroidResourceWithRawResponse(self._boxes.android)


class BoxesResourceWithStreamingResponse:
    def __init__(self, boxes: BoxesResource) -> None:
        self._boxes = boxes

        self.retrieve = to_streamed_response_wrapper(
            boxes.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            boxes.list,
        )
        self.create_android = to_streamed_response_wrapper(
            boxes.create_android,
        )
        self.create_linux = to_streamed_response_wrapper(
            boxes.create_linux,
        )
        self.display = to_streamed_response_wrapper(
            boxes.display,
        )
        self.execute_commands = to_streamed_response_wrapper(
            boxes.execute_commands,
        )
        self.live_view_url = to_streamed_response_wrapper(
            boxes.live_view_url,
        )
        self.run_code = to_streamed_response_wrapper(
            boxes.run_code,
        )
        self.start = to_streamed_response_wrapper(
            boxes.start,
        )
        self.stop = to_streamed_response_wrapper(
            boxes.stop,
        )
        self.terminate = to_streamed_response_wrapper(
            boxes.terminate,
        )
        self.web_terminal_url = to_streamed_response_wrapper(
            boxes.web_terminal_url,
        )
        self.websocket_url = to_streamed_response_wrapper(
            boxes.websocket_url,
        )

    @cached_property
    def storage(self) -> StorageResourceWithStreamingResponse:
        return StorageResourceWithStreamingResponse(self._boxes.storage)

    @cached_property
    def actions(self) -> ActionsResourceWithStreamingResponse:
        return ActionsResourceWithStreamingResponse(self._boxes.actions)

    @cached_property
    def proxy(self) -> ProxyResourceWithStreamingResponse:
        return ProxyResourceWithStreamingResponse(self._boxes.proxy)

    @cached_property
    def media(self) -> MediaResourceWithStreamingResponse:
        return MediaResourceWithStreamingResponse(self._boxes.media)

    @cached_property
    def fs(self) -> FsResourceWithStreamingResponse:
        return FsResourceWithStreamingResponse(self._boxes.fs)

    @cached_property
    def browser(self) -> BrowserResourceWithStreamingResponse:
        return BrowserResourceWithStreamingResponse(self._boxes.browser)

    @cached_property
    def android(self) -> AndroidResourceWithStreamingResponse:
        return AndroidResourceWithStreamingResponse(self._boxes.android)


class AsyncBoxesResourceWithStreamingResponse:
    def __init__(self, boxes: AsyncBoxesResource) -> None:
        self._boxes = boxes

        self.retrieve = async_to_streamed_response_wrapper(
            boxes.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            boxes.list,
        )
        self.create_android = async_to_streamed_response_wrapper(
            boxes.create_android,
        )
        self.create_linux = async_to_streamed_response_wrapper(
            boxes.create_linux,
        )
        self.display = async_to_streamed_response_wrapper(
            boxes.display,
        )
        self.execute_commands = async_to_streamed_response_wrapper(
            boxes.execute_commands,
        )
        self.live_view_url = async_to_streamed_response_wrapper(
            boxes.live_view_url,
        )
        self.run_code = async_to_streamed_response_wrapper(
            boxes.run_code,
        )
        self.start = async_to_streamed_response_wrapper(
            boxes.start,
        )
        self.stop = async_to_streamed_response_wrapper(
            boxes.stop,
        )
        self.terminate = async_to_streamed_response_wrapper(
            boxes.terminate,
        )
        self.web_terminal_url = async_to_streamed_response_wrapper(
            boxes.web_terminal_url,
        )
        self.websocket_url = async_to_streamed_response_wrapper(
            boxes.websocket_url,
        )

    @cached_property
    def storage(self) -> AsyncStorageResourceWithStreamingResponse:
        return AsyncStorageResourceWithStreamingResponse(self._boxes.storage)

    @cached_property
    def actions(self) -> AsyncActionsResourceWithStreamingResponse:
        return AsyncActionsResourceWithStreamingResponse(self._boxes.actions)

    @cached_property
    def proxy(self) -> AsyncProxyResourceWithStreamingResponse:
        return AsyncProxyResourceWithStreamingResponse(self._boxes.proxy)

    @cached_property
    def media(self) -> AsyncMediaResourceWithStreamingResponse:
        return AsyncMediaResourceWithStreamingResponse(self._boxes.media)

    @cached_property
    def fs(self) -> AsyncFsResourceWithStreamingResponse:
        return AsyncFsResourceWithStreamingResponse(self._boxes.fs)

    @cached_property
    def browser(self) -> AsyncBrowserResourceWithStreamingResponse:
        return AsyncBrowserResourceWithStreamingResponse(self._boxes.browser)

    @cached_property
    def android(self) -> AsyncAndroidResourceWithStreamingResponse:
        return AsyncAndroidResourceWithStreamingResponse(self._boxes.android)
