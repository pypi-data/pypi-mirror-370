from typing import Dict, List, Union, Literal, Callable, Optional
from typing_extensions import Self

from gbox_sdk._types import NOT_GIVEN, NotGiven
from gbox_sdk._client import GboxClient
from gbox_sdk.wrapper.box.media import MediaOperator
from gbox_sdk.types.v1.linux_box import LinuxBox
from gbox_sdk.wrapper.box.action import ActionOperator
from gbox_sdk.wrapper.box.browser import BrowserOperator
from gbox_sdk.wrapper.box.storage import StorageOperator
from gbox_sdk.types.v1.android_box import AndroidBox
from gbox_sdk.wrapper.box.file_system import FileSystemOperator
from gbox_sdk.wrapper.box.websocket_client import WebSocketClient, WebSocketResult
from gbox_sdk.types.v1.box_display_response import BoxDisplayResponse
from gbox_sdk.types.v1.box_run_code_response import BoxRunCodeResponse
from gbox_sdk.types.v1.box_live_view_url_response import BoxLiveViewURLResponse
from gbox_sdk.types.v1.box_execute_commands_response import BoxExecuteCommandsResponse
from gbox_sdk.types.v1.box_web_terminal_url_response import BoxWebTerminalURLResponse


class BaseBox:
    """
    Base class for box operations, providing common interfaces for box lifecycle and actions.

    Attributes:
        client (GboxClient): The Gbox client instance used for API calls.
        data (Union[LinuxBox, AndroidBox]): The box data object.
        action (ActionOperator): Operator for box actions.
        fs (FileSystemOperator): Operator for file system actions.
        browser (BrowserOperator): Operator for browser actions.
    """

    def __init__(self, client: GboxClient, data: Union[LinuxBox, AndroidBox]):
        """
        Initialize a BaseBox instance.

        Args:
            client (GboxClient): The Gbox client instance.
            data (Union[LinuxBox, AndroidBox]): The box data object.
        """
        self.client = client
        self.data = data

        self.action = ActionOperator(self.client, self.data.id)
        self.fs = FileSystemOperator(self.client, self.data.id)
        self.browser = BrowserOperator(self.client, self.data.id)
        self.storage = StorageOperator(self.client, self.data.id)
        self.media = MediaOperator(self.client, self.data.id)

    def _sync_data(self) -> None:
        """
        Synchronize the box data with the latest state from the server.
        """
        res = self.client.v1.boxes.retrieve(box_id=self.data.id)
        self.data = res

    def start(self, *, wait: Union[bool, NotGiven] = NOT_GIVEN) -> Self:
        """
        Start the box.

        Args:
            wait: Whether to wait for the box to start.

        Returns:
            Self: The updated box instance for method chaining.

        Example:
            >>> box.start()
            >>> box.start(wait=True)
        """
        self.client.v1.boxes.start(box_id=self.data.id, wait=wait)
        self._sync_data()
        return self

    def stop(self, *, wait: Union[bool, NotGiven] = NOT_GIVEN) -> Self:
        """
        Stop the box.

        Args:
            wait: Whether to wait for the box to stop.

        Returns:
            Self: The updated box instance for method chaining.

        Example:
            >>> box.stop()
            >>> box.stop(wait=True)
        """
        self.client.v1.boxes.stop(box_id=self.data.id, wait=wait)
        self._sync_data()
        return self

    def terminate(self, *, wait: Union[bool, NotGiven] = NOT_GIVEN) -> Self:
        """
        Terminate the box.

        Args:
            wait: Whether to wait for the box to terminate.

        Returns:
            Self: The updated box instance for method chaining.

        Example:
            >>> box.terminate()
            >>> box.terminate(wait=True)
        """
        self.client.v1.boxes.terminate(box_id=self.data.id, wait=wait)
        self._sync_data()
        return self

    def display(self) -> BoxDisplayResponse:
        """
        Retrieve the current display properties for a running box.

        This endpoint
        provides details about the box's screen resolution, orientation, and other
        visual properties

        Returns:
            BoxDisplayResponse: The response containing the display properties.

        Example:
            >>> box.display()
        """
        return self.client.v1.boxes.display(box_id=self.data.id)

    def command(
        self,
        commands: Union[List[str], str],
        on_stdout: Optional[Callable[[str], None]] = None,
        on_stderr: Optional[Callable[[str], None]] = None,
        envs: Union[Dict[str, str], NotGiven] = NOT_GIVEN,
        api_timeout: Union[str, NotGiven] = NOT_GIVEN,
        working_dir: Union[str, NotGiven] = NOT_GIVEN,
    ) -> Union["BoxExecuteCommandsResponse", "WebSocketResult"]:
        """
        Execute shell commands in the box.

        Args:
            commands: The command to run. Can be a single string or an array of strings

            envs: The environment variables to run the command

            api_timeout: The timeout of the command. If the command times out, the exit code will be 124.
                For example: 'timeout 5s sleep 10s' will result in exit code 124.

                Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
                Example formats: "500ms", "30s", "5m", "1h" Default: 30s

            working_dir: The working directory of the command. It not provided, the command will be run
                in the `box.config.workingDir` directory.

            on_stdout: Callback for stdout.

            on_stderr: Callback for stderr.

        Returns:
            Union[BoxExecuteCommandsResponse, WebSocketResult]: The response containing the command execution result.

        Example:
            >>> box.command(commands=["ls", "-l"], on_stdout=lambda x: print(x), on_stderr=lambda x: print(x))
        """
        if on_stdout is not None or on_stderr is not None:
            return self._command_via_websocket(commands, on_stdout, on_stderr, envs, api_timeout, working_dir)

        return self.client.v1.boxes.execute_commands(
            box_id=self.data.id,
            commands=commands,
            envs=envs,
            api_timeout=api_timeout,
            working_dir=working_dir,
        )

    def _command_via_websocket(
        self,
        commands: Union[List[str], str],
        on_stdout: Optional[Callable[[str], None]] = None,
        on_stderr: Optional[Callable[[str], None]] = None,
        envs: Union[Dict[str, str], NotGiven] = NOT_GIVEN,
        api_timeout: Union[str, NotGiven] = NOT_GIVEN,
        working_dir: Union[str, NotGiven] = NOT_GIVEN,
    ) -> "WebSocketResult":
        """
        Execute commands via WebSocket with streaming output.

        This method runs the WebSocket execution in a new event loop if one is not already running.
        """
        try:
            websocket_response = self.client.v1.boxes.websocket_url(box_id=self.data.id)
            websocket_url = websocket_response.command

            websocket_client = WebSocketClient(websocket_url, self.client.api_key)

            import asyncio

            try:
                loop = asyncio.get_running_loop()
                return asyncio.run_coroutine_threadsafe(
                    websocket_client.execute_command(
                        commands=commands,
                        on_stdout=on_stdout,
                        on_stderr=on_stderr,
                        envs=envs,
                        api_timeout=api_timeout,
                        working_dir=working_dir,
                    ),
                    loop,
                ).result()
            except RuntimeError:
                return asyncio.run(
                    websocket_client.execute_command(
                        commands=commands,
                        on_stdout=on_stdout,
                        on_stderr=on_stderr,
                        envs=envs,
                        api_timeout=api_timeout,
                        working_dir=working_dir,
                    )
                )

        except Exception as e:
            raise RuntimeError(f"Failed to execute command via WebSocket: {e}") from e

    def run_code(
        self,
        code: str,
        argv: Union[List[str], NotGiven] = NOT_GIVEN,
        envs: Union[Dict[str, str], NotGiven] = NOT_GIVEN,
        language: Union[Literal["bash", "python", "typescript"], NotGiven] = NOT_GIVEN,
        api_timeout: Union[str, NotGiven] = NOT_GIVEN,
        working_dir: Union[str, NotGiven] = NOT_GIVEN,
        on_stdout: Optional[Callable[[str], None]] = None,
        on_stderr: Optional[Callable[[str], None]] = None,
    ) -> Union["BoxRunCodeResponse", "WebSocketResult"]:
        """
        Run code in the box.

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

            on_stdout: Callback for stdout.

            on_stderr: Callback for stderr.
        Returns:
            Union[BoxRunCodeResponse, WebSocketResult]: The response containing the code execution result.

        Example:
            >>> box.run_code(
            ...     code="print('Hello, World!')",
            ...     language="python",
            ...     on_stdout=lambda x: print(x),
            ...     on_stderr=lambda x: print(x),
            ... )
        """

        if on_stdout is not None or on_stderr is not None:
            return self._run_code_via_websocket(
                code=code,
                argv=argv,
                envs=envs,
                language=language,
                api_timeout=api_timeout,
                working_dir=working_dir,
                on_stdout=on_stdout,
                on_stderr=on_stderr,
            )

        return self.client.v1.boxes.run_code(
            box_id=self.data.id,
            code=code,
            argv=argv,
            envs=envs,
            language=language,
            api_timeout=api_timeout,
            working_dir=working_dir,
        )

    def _run_code_via_websocket(
        self,
        code: str,
        argv: Union[List[str], NotGiven] = NOT_GIVEN,
        envs: Union[Dict[str, str], NotGiven] = NOT_GIVEN,
        language: Union[Literal["bash", "python", "typescript"], NotGiven] = NOT_GIVEN,
        api_timeout: Union[str, NotGiven] = NOT_GIVEN,
        working_dir: Union[str, NotGiven] = NOT_GIVEN,
        on_stdout: Optional[Callable[[str], None]] = None,
        on_stderr: Optional[Callable[[str], None]] = None,
    ) -> "WebSocketResult":
        """
        Run code via WebSocket with streaming output.

        This method runs the WebSocket execution in a new event loop if one is not already running.
        """
        try:
            websocket_response = self.client.v1.boxes.websocket_url(box_id=self.data.id)
            websocket_url = websocket_response.run_code

            websocket_client = WebSocketClient(websocket_url, self.client.api_key)

            import asyncio

            try:
                loop = asyncio.get_running_loop()
                return asyncio.run_coroutine_threadsafe(
                    websocket_client.run_code(
                        code=code,
                        on_stdout=on_stdout,
                        on_stderr=on_stderr,
                        argv=argv,
                        envs=envs,
                        language=language,
                        api_timeout=api_timeout,
                        working_dir=working_dir,
                    ),
                    loop,
                ).result()
            except RuntimeError:
                return asyncio.run(
                    websocket_client.run_code(
                        code=code,
                        on_stdout=on_stdout,
                        on_stderr=on_stderr,
                        argv=argv,
                        envs=envs,
                        language=language,
                        api_timeout=api_timeout,
                        working_dir=working_dir,
                    )
                )

        except Exception as e:
            raise RuntimeError(f"Failed to run code via WebSocket: {e}") from e

    def live_view(
        self,
        *,
        expires_in: Union[str, NotGiven] = NOT_GIVEN,
    ) -> BoxLiveViewURLResponse:
        """
        Get the live view URL for the box.

        Args:
            expires_in: The duration for the live view URL to be valid.
        Returns:
            BoxLiveViewURLResponse: The response containing the live view URL.
        """
        return self.client.v1.boxes.live_view_url(
            box_id=self.data.id,
            expires_in=expires_in,
        )

    def web_terminal(
        self,
        *,
        expires_in: Union[str, NotGiven] = NOT_GIVEN,
    ) -> BoxWebTerminalURLResponse:
        """
        Get the web terminal URL for the box.

        Args:
            body (BoxWebTerminalURLParams): Parameters for web terminal URL.
        Returns:
            BoxWebTerminalURLResponse: The response containing the web terminal URL.
        """
        return self.client.v1.boxes.web_terminal_url(
            box_id=self.data.id,
            expires_in=expires_in,
        )
