# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["AndroidOpenParams"]


class AndroidOpenParams(TypedDict, total=False):
    box_id: Required[Annotated[str, PropertyInfo(alias="boxId")]]

    activity_name: Annotated[str, PropertyInfo(alias="activityName")]
    """Activity name, default is the main activity."""
