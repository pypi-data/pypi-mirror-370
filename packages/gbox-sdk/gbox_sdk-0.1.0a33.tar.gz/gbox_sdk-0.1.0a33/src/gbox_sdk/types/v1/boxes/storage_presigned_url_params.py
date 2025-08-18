# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["StoragePresignedURLParams"]


class StoragePresignedURLParams(TypedDict, total=False):
    storage_key: Required[Annotated[str, PropertyInfo(alias="storageKey")]]
    """Storage key"""

    expires_in: Annotated[str, PropertyInfo(alias="expiresIn")]
    """Presigned url expires in

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m Maximum allowed: 6h
    """
