# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["BoxExecuteCommandsParams"]


class BoxExecuteCommandsParams(TypedDict, total=False):
    commands: Required[Union[str, List[str]]]
    """The command to run. Can be a single string or an array of strings"""

    envs: object
    """The environment variables to run the command"""

    api_timeout: Annotated[str, PropertyInfo(alias="timeout")]
    """The timeout of the command.

    If the command times out, the exit code will be 124. For example: 'timeout 5s
    sleep 10s' will result in exit code 124.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30s
    """

    working_dir: Annotated[str, PropertyInfo(alias="workingDir")]
    """The working directory of the command.

    It not provided, the command will be run in the `box.config.workingDir`
    directory.
    """
