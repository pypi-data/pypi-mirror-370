# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["FRenameParams"]


class FRenameParams(TypedDict, total=False):
    new_path: Required[Annotated[str, PropertyInfo(alias="newPath")]]
    """New path in the box.

    If the path does not start with '/', the file/directory will be renamed relative
    to the working directory. If the newPath already exists, the rename will fail.
    """

    old_path: Required[Annotated[str, PropertyInfo(alias="oldPath")]]
    """Old path in the box.

    If the path does not start with '/', the file/directory will be renamed relative
    to the working directory. If the oldPath does not exist, the rename will fail.
    """

    working_dir: Annotated[str, PropertyInfo(alias="workingDir")]
    """Working directory.

    If not provided, the file will be read from the `box.config.workingDir`
    directory.
    """
