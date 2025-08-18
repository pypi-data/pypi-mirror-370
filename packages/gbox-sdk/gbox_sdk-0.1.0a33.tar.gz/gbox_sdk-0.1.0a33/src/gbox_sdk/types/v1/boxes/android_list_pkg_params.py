# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["AndroidListPkgParams"]


class AndroidListPkgParams(TypedDict, total=False):
    pkg_type: Annotated[List[Literal["system", "thirdParty"]], PropertyInfo(alias="pkgType")]
    """system or thirdParty, default is thirdParty"""

    running_filter: Annotated[List[Literal["running", "notRunning"]], PropertyInfo(alias="runningFilter")]
    """
    Filter pkgs by running status: running (show only running pkgs), notRunning
    (show only non-running pkgs). Default is all
    """
