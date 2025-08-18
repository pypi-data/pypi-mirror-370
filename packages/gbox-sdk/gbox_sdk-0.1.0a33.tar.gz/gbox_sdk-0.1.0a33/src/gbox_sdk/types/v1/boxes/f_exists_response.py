# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import TypeAlias

from ...._models import BaseModel

__all__ = ["FExistsResponse", "ExistsFileResult", "NotExistsFileResult"]


class ExistsFileResult(BaseModel):
    exists: bool
    """Exists"""

    type: str
    """Type"""


class NotExistsFileResult(BaseModel):
    exists: bool
    """Exists"""


FExistsResponse: TypeAlias = Union[ExistsFileResult, NotExistsFileResult]
