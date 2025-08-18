# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["AndroidUninstallParams"]


class AndroidUninstallParams(TypedDict, total=False):
    box_id: Required[Annotated[str, PropertyInfo(alias="boxId")]]

    keep_data: Annotated[bool, PropertyInfo(alias="keepData")]
    """uninstalls the pkg while retaining the data/cache"""
