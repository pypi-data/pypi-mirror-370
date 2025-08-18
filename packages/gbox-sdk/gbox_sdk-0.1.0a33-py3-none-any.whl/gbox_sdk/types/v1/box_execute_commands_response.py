# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["BoxExecuteCommandsResponse"]


class BoxExecuteCommandsResponse(BaseModel):
    exit_code: float = FieldInfo(alias="exitCode")
    """The exit code of the command"""

    stderr: str
    """The standard error output of the command"""

    stdout: str
    """The standard output of the command"""
