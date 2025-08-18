import json
import asyncio
import threading
from typing import Any, Dict, List, Union, Callable, Optional
from dataclasses import dataclass
from typing_extensions import Literal

import websocket
from websocket import WebSocket

from gbox_sdk._types import NOT_GIVEN, NotGiven


@dataclass
class WebSocketResult:
    """Result from WebSocket command execution"""

    exit_code: int
    stdout: str
    stderr: str


class WebSocketClient:
    """WebSocket client for streaming command execution"""

    def __init__(self, websocket_url: str, api_key: str):
        self.websocket_url = websocket_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

    async def execute_command(
        self,
        commands: Union[List[str], str],
        on_stdout: Optional[Callable[[str], None]] = None,
        on_stderr: Optional[Callable[[str], None]] = None,
        envs: Union[Dict[str, str], NotGiven] = NOT_GIVEN,
        api_timeout: Union[str, NotGiven] = NOT_GIVEN,
        working_dir: Union[str, NotGiven] = NOT_GIVEN,
    ) -> WebSocketResult:
        """
        Execute commands via WebSocket with streaming output

        Args:
            commands: Commands to execute
            on_stdout: Callback for stdout data
            on_stderr: Callback for stderr data
            envs: Environment variables
            api_timeout: API timeout
            working_dir: Working directory

        Returns:
            WebSocketResult with execution results
        """
        command_obj: Dict[str, Any] = {
            "commands": commands if isinstance(commands, list) else [commands],
        }

        payload: Dict[str, Any] = {
            "command": command_obj,
        }

        if envs is not NOT_GIVEN:
            payload["envs"] = envs
        if api_timeout is not NOT_GIVEN:
            payload["timeout"] = api_timeout
        if working_dir is not NOT_GIVEN:
            payload["workingDir"] = working_dir

        return await self._execute_via_websocket(payload, on_stdout, on_stderr)

    async def run_code(
        self,
        code: str,
        on_stdout: Optional[Callable[[str], None]] = None,
        on_stderr: Optional[Callable[[str], None]] = None,
        argv: Union[List[str], NotGiven] = NOT_GIVEN,
        envs: Union[Dict[str, str], NotGiven] = NOT_GIVEN,
        language: Union[Literal["bash", "python", "typescript"], NotGiven] = NOT_GIVEN,
        api_timeout: Union[str, NotGiven] = NOT_GIVEN,
        working_dir: Union[str, NotGiven] = NOT_GIVEN,
    ) -> WebSocketResult:
        """
        Run code via WebSocket with streaming output

        Args:
            code: Code to execute
            on_stdout: Callback for stdout data
            on_stderr: Callback for stderr data
            argv: Arguments to pass to the code
            envs: Environment variables
            language: Programming language (bash, python, typescript)
            api_timeout: API timeout
            working_dir: Working directory

        Returns:
            WebSocketResult with execution results
        """
        run_code_obj: Dict[str, Any] = {
            "code": code,
        }

        if language is not NOT_GIVEN:
            run_code_obj["language"] = language

        payload: Dict[str, Any] = {
            "runCode": run_code_obj,
        }

        if argv is not NOT_GIVEN:
            payload["argv"] = argv
        if envs is not NOT_GIVEN:
            payload["envs"] = envs
        if api_timeout is not NOT_GIVEN:
            payload["timeout"] = api_timeout
        if working_dir is not NOT_GIVEN:
            payload["workingDir"] = working_dir

        return await self._execute_via_websocket(payload, on_stdout, on_stderr)

    async def _execute_via_websocket(
        self,
        payload: Dict[str, Any],
        on_stdout: Optional[Callable[[str], None]] = None,
        on_stderr: Optional[Callable[[str], None]] = None,
    ) -> WebSocketResult:
        """Execute command via WebSocket with streaming output"""

        def run_websocket() -> WebSocketResult:
            stdout = ""
            stderr = ""
            exit_code = 0
            result_event = threading.Event()
            result: Optional[WebSocketResult] = None

            def on_message(ws: WebSocket, message: str) -> None:
                nonlocal stdout, stderr, exit_code, result
                try:
                    data = json.loads(message)
                    if data.get("event") == "stdout":
                        output = data.get("data", "")
                        stdout += output
                        if on_stdout:
                            on_stdout(output)
                    elif data.get("event") == "stderr":
                        output = data.get("data", "")
                        stderr += output
                        if on_stderr:
                            on_stderr(output)
                    elif data.get("event") == "end":
                        exit_code = data.get("exitCode", 0)
                        ws.close()
                except Exception as e:
                    result = WebSocketResult(exit_code=1, stdout="", stderr=f"Failed to parse WebSocket message: {e}")
                    result_event.set()
                    ws.close()

            def on_error(_ws: WebSocket, error: str) -> None:
                nonlocal result
                result = WebSocketResult(exit_code=1, stdout="", stderr=f"WebSocket error: {error}")
                result_event.set()

            def on_close(_ws: WebSocket, _close_status_code: int, _close_msg: str) -> None:
                nonlocal result
                if result is None:
                    result = WebSocketResult(exit_code=exit_code, stdout=stdout, stderr=stderr)
                result_event.set()

            def on_open(ws: WebSocket) -> None:
                try:
                    ws.send(json.dumps(payload))
                except Exception as e:
                    nonlocal result
                    result = WebSocketResult(exit_code=1, stdout="", stderr=f"Failed to send payload: {e}")
                    result_event.set()
                    ws.close()

            ws = websocket.WebSocketApp(
                self.websocket_url,
                header=self.headers,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
            )

            ws.run_forever()  # type: ignore[attr-defined]
            result_event.wait()
            if result is None:
                result = WebSocketResult(exit_code=1, stdout="", stderr="No result received")
            return result

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, run_websocket)
        return result
