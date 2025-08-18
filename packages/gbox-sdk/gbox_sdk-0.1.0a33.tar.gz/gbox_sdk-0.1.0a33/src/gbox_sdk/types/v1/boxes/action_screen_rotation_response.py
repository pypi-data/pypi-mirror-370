# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = [
    "ActionScreenRotationResponse",
    "ActionIncludeScreenshotResult",
    "ActionIncludeScreenshotResultScreenshot",
    "ActionIncludeScreenshotResultScreenshotAfter",
    "ActionIncludeScreenshotResultScreenshotBefore",
    "ActionIncludeScreenshotResultScreenshotTrace",
    "ActionCommonResult",
]


class ActionIncludeScreenshotResultScreenshotAfter(BaseModel):
    uri: str
    """URI of the screenshot after the action"""

    presigned_url: Optional[str] = FieldInfo(alias="presignedUrl", default=None)
    """Presigned url of the screenshot before the action"""


class ActionIncludeScreenshotResultScreenshotBefore(BaseModel):
    uri: str
    """URI of the screenshot before the action"""

    presigned_url: Optional[str] = FieldInfo(alias="presignedUrl", default=None)
    """Presigned url of the screenshot before the action"""


class ActionIncludeScreenshotResultScreenshotTrace(BaseModel):
    uri: str
    """URI of the screenshot with operation trace"""


class ActionIncludeScreenshotResultScreenshot(BaseModel):
    after: ActionIncludeScreenshotResultScreenshotAfter
    """Screenshot taken after action execution"""

    before: ActionIncludeScreenshotResultScreenshotBefore
    """Screenshot taken before action execution"""

    trace: ActionIncludeScreenshotResultScreenshotTrace
    """Screenshot with action operation trace"""


class ActionIncludeScreenshotResult(BaseModel):
    screenshot: ActionIncludeScreenshotResultScreenshot
    """Complete screenshot result with operation trace, before and after images"""


class ActionCommonResult(BaseModel):
    message: str
    """message"""


ActionScreenRotationResponse: TypeAlias = Union[ActionIncludeScreenshotResult, ActionCommonResult]
