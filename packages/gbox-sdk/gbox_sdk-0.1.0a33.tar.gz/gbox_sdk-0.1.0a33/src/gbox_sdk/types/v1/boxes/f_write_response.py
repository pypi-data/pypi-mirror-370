# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["FWriteResponse"]


class FWriteResponse(BaseModel):
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
