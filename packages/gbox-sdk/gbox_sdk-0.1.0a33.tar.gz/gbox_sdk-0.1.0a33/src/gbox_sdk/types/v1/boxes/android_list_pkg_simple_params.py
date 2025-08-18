# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["AndroidListPkgSimpleParams"]


class AndroidListPkgSimpleParams(TypedDict, total=False):
    pkg_type: Annotated[List[Literal["system", "thirdParty"]], PropertyInfo(alias="pkgType")]
    """system or thirdParty, default is thirdParty"""
