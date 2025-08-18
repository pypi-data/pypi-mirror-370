# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ...._models import BaseModel

__all__ = ["BrowserGetTabsResponse", "Data"]


class Data(BaseModel):
    id: str
    """The tab id"""

    active: bool
    """Whether the tab is the current active (frontmost) tab"""

    favicon: str
    """The tab favicon"""

    loading: bool
    """Whether the tab is currently in a loading state.

    The value is **true** while the browser is still navigating to the target URL or
    fetching sub-resources (i.e. `document.readyState` is not "complete"). It
    typically switches to **false** once the `load` event fires and all major
    network activity has settled.
    """

    title: str
    """The tab title"""

    url: str
    """The tab url"""


class BrowserGetTabsResponse(BaseModel):
    data: List[Data]
    """The tabs"""
