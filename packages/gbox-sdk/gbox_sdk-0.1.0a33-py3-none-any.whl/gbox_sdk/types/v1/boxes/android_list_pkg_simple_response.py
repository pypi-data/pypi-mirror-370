# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["AndroidListPkgSimpleResponse", "Data"]


class Data(BaseModel):
    apk_path: str = FieldInfo(alias="apkPath")
    """Android apk path"""

    package_name: str = FieldInfo(alias="packageName")
    """Android pkg package name"""

    pkg_type: Literal["system", "thirdParty"] = FieldInfo(alias="pkgType")
    """system or thirdParty"""


class AndroidListPkgSimpleResponse(BaseModel):
    data: List[Data]
    """Android pkg simple list"""
