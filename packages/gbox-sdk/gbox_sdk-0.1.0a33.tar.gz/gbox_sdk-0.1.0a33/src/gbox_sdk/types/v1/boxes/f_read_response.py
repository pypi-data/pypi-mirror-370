# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["FReadResponse"]


class FReadResponse(BaseModel):
    content: str
    """Content of the file"""
