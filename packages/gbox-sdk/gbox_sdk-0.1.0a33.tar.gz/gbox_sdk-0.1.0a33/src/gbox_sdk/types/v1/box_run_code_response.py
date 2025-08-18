# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["BoxRunCodeResponse"]


class BoxRunCodeResponse(BaseModel):
    exit_code: float = FieldInfo(alias="exitCode")
    """The exit code of the code"""

    stderr: str
    """The stderr of the code"""

    stdout: str
    """The stdout of the code"""
