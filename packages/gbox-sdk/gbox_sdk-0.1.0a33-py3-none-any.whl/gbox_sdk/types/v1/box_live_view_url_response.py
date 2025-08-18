# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["BoxLiveViewURLResponse"]


class BoxLiveViewURLResponse(BaseModel):
    raw_url: str = FieldInfo(alias="rawUrl")
    """
    Raw live view url without additional layout content, typically used for
    embedding into your own application
    """

    url: str
    """
    Live view url with Gbox interface and basic information, typically used for
    real-time observation of box usage status
    """
