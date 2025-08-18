# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["FInfoParams"]


class FInfoParams(TypedDict, total=False):
    path: Required[str]
    """Target path in the box.

    If the path does not start with '/', the file/directory will be checked relative
    to the working directory
    """

    working_dir: Annotated[str, PropertyInfo(alias="workingDir")]
    """Working directory.

    If not provided, the file will be read from the `box.config.workingDir`
    directory.
    """
