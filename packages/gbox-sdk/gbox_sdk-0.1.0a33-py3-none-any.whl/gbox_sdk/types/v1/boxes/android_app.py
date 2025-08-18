# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["AndroidApp"]


class AndroidApp(BaseModel):
    activity_class_name: str = FieldInfo(alias="activityClassName")
    """Activity class name"""

    activity_name: str = FieldInfo(alias="activityName")
    """Activity name"""

    package_name: str = FieldInfo(alias="packageName")
    """App package name"""
