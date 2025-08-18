# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["MediaListMediaResponse", "Data", "DataPhoto", "DataVideo"]


class DataPhoto(BaseModel):
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


class DataVideo(BaseModel):
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


Data: TypeAlias = Union[DataPhoto, DataVideo]


class MediaListMediaResponse(BaseModel):
    data: List[Data]
    """List of media files (photos and videos) in the album"""
