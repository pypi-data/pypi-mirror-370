# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, Annotated, TypedDict

from ...._types import FileTypes
from ...._utils import PropertyInfo

__all__ = ["MediaUpdateAlbumParams"]


class MediaUpdateAlbumParams(TypedDict, total=False):
    box_id: Required[Annotated[str, PropertyInfo(alias="boxId")]]

    media: Required[List[FileTypes]]
    """Media files to add to the album (max size: 512MB per file)"""
