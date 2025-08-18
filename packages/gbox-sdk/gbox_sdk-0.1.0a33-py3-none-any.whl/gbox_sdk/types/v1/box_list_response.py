# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .linux_box import LinuxBox
from .android_box import AndroidBox

__all__ = ["BoxListResponse", "Data"]

Data: TypeAlias = Union[LinuxBox, AndroidBox]


class BoxListResponse(BaseModel):
    data: List[Data]
    """A box instance that can be either Linux or Android type"""

    page: int
    """Page number"""

    page_size: int = FieldInfo(alias="pageSize")
    """Page size"""

    total: int
    """Total number of items"""
