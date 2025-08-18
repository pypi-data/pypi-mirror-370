# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ...._models import BaseModel

__all__ = ["MediaGetMediaSupportResponse"]


class MediaGetMediaSupportResponse(BaseModel):
    photo: List[str]
    """Supported photo extensions"""

    video: List[str]
    """Supported video extensions"""
