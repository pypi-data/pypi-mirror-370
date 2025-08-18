# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["AndroidListActivitiesResponse", "Data"]


class Data(BaseModel):
    class_name: str = FieldInfo(alias="className")
    """Activity class name"""

    is_exported: bool = FieldInfo(alias="isExported")
    """Activity class name"""

    is_launcher: bool = FieldInfo(alias="isLauncher")
    """Whether the activity is a launcher activity.

    Launcher activities appear in the device's pkg launcher/home screen and can be
    directly launched by the user.
    """

    is_main: bool = FieldInfo(alias="isMain")
    """Whether the activity is the main activity.

    Main activity is the entry point of the pkg and is typically launched when the
    pkg is started.
    """

    name: str
    """Activity name"""

    package_name: str = FieldInfo(alias="packageName")
    """Activity package name"""


class AndroidListActivitiesResponse(BaseModel):
    data: List[Data]
    """Activity list"""
