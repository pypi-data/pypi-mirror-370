# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["BoxStopParams"]


class BoxStopParams(TypedDict, total=False):
    wait: bool
    """Wait for the box operation to be completed, default is true"""
