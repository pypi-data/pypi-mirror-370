# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ActionRecordingStartParams"]


class ActionRecordingStartParams(TypedDict, total=False):
    duration: str
    """Duration of the recording.

    Default is 30m, max is 30m. The recording will automatically stop when the
    duration time is reached.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Maximum allowed: 30m
    """
