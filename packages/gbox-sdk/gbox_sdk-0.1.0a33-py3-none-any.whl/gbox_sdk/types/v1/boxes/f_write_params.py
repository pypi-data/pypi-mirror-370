# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from ...._types import FileTypes
from ...._utils import PropertyInfo

__all__ = ["FWriteParams", "WriteFile", "WriteFileByBinary"]


class WriteFile(TypedDict, total=False):
    content: Required[str]
    """Content of the file (Max size: 512MB)"""

    path: Required[str]
    """Target path in the box.

    If the path does not start with '/', the file will be written relative to the
    working directory. Creates necessary directories in the path if they don't
    exist. If the target path already exists, the write will fail.
    """

    working_dir: Annotated[str, PropertyInfo(alias="workingDir")]
    """Working directory.

    If not provided, the file will be read from the `box.config.workingDir`
    directory.
    """


class WriteFileByBinary(TypedDict, total=False):
    content: Required[FileTypes]
    """Binary content of the file (Max file size: 512MB)"""

    path: Required[str]
    """Target path in the box.

    If the path does not start with '/', the file will be written relative to the
    working directory. Creates necessary directories in the path if they don't
    exist. If the target path already exists, the write will fail.
    """

    working_dir: Annotated[str, PropertyInfo(alias="workingDir")]
    """Working directory.

    If not provided, the file will be read from the `box.config.workingDir`
    directory.
    """


FWriteParams: TypeAlias = Union[WriteFile, WriteFileByBinary]
