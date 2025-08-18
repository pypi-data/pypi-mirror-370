# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["FRenameResponse", "File", "Dir"]


class File(BaseModel):
    last_modified: datetime = FieldInfo(alias="lastModified")
    """Last modified time of the file"""

    mode: str
    """File metadata"""

    name: str
    """Name of the file"""

    path: str
    """Full path to the file in the box"""

    size: str
    """Size of the file"""

    type: Literal["file"]
    """File type indicator"""


class Dir(BaseModel):
    last_modified: datetime = FieldInfo(alias="lastModified")
    """Last modified time of the directory"""

    mode: str
    """Directory metadata"""

    name: str
    """Name of the directory"""

    path: str
    """Full path to the directory in the box"""

    type: Literal["dir"]
    """Directory type indicator"""


FRenameResponse: TypeAlias = Union[File, Dir]
