# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["MediaGetMediaResponse", "Photo", "Video"]


class Photo(BaseModel):
    last_modified: datetime = FieldInfo(alias="lastModified")
    """Last modified time of the photo"""

    mime_type: str = FieldInfo(alias="mimeType")
    """MIME type of the photo"""

    name: str
    """Name of the photo"""

    path: str
    """Full path to the photo in the box"""

    size: str
    """Size of the photo"""

    type: Literal["photo"]
    """Photo type indicator"""


class Video(BaseModel):
    last_modified: datetime = FieldInfo(alias="lastModified")
    """Last modified time of the video"""

    mime_type: str = FieldInfo(alias="mimeType")
    """MIME type of the video"""

    name: str
    """Name of the video"""

    path: str
    """Full path to the video in the box"""

    size: str
    """Size of the video"""

    type: Literal["video"]
    """Video type indicator"""


MediaGetMediaResponse: TypeAlias = Union[Photo, Video]
