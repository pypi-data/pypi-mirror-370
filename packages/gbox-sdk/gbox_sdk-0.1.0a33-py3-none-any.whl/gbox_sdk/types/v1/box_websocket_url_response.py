# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["BoxWebsocketURLResponse"]


class BoxWebsocketURLResponse(BaseModel):
    command: str
    """WebSocket URL for executing shell commands in the box.

    This endpoint allows real-time command execution with streaming output,
    supporting interactive terminal sessions and long-running processes.
    """

    run_code: str = FieldInfo(alias="runCode")
    """WebSocket URL for running code snippets in the box environment.

    This endpoint enables execution of code in various programming languages with
    real-time output streaming, perfect for interactive coding sessions and script
    execution.
    """
