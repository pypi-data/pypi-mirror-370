# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["AndroidBox", "Config", "ConfigOs"]


class ConfigOs(BaseModel):
    version: Literal["12", "13", "15"]
    """Supported Android versions"""


class Config(BaseModel):
    cpu: float
    """CPU cores allocated to the box"""

    envs: Dict[str, str]
    """Environment variables for the box.

    These variables will be available in all operations including command execution,
    code running, and other box behaviors
    """

    labels: Dict[str, str]
    """Key-value pairs of labels for the box.

    Labels are used to add custom metadata to help identify, categorize, and manage
    boxes. Common use cases include project names, environments, teams,
    applications, or any other organizational tags that help you organize and filter
    your boxes.
    """

    memory: float
    """Memory allocated to the box in MiB"""

    os: ConfigOs
    """Android operating system configuration"""

    storage: float
    """Storage allocated to the box in GiB"""

    device_type: Optional[Literal["virtual", "physical"]] = FieldInfo(alias="deviceType", default=None)
    """Device type - virtual or physical Android device"""

    working_dir: Optional[str] = FieldInfo(alias="workingDir", default=None)
    """Working directory path for the box.

    This directory serves as the default starting point for all operations including
    command execution, code running, and file system operations. When you execute
    commands or run code, they will start from this directory unless explicitly
    specified otherwise.
    """


class AndroidBox(BaseModel):
    id: str
    """Unique identifier for the box"""

    config: Config
    """Complete configuration for Android box instance"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Creation timestamp of the box"""

    expires_at: Optional[datetime] = FieldInfo(alias="expiresAt", default=None)
    """Expiration timestamp of the box"""

    status: Literal["pending", "running", "error", "terminated"]
    """The current status of a box instance"""

    type: Literal["android"]
    """Box type is Android"""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Last update timestamp of the box"""

    reason: Optional[str] = None
    """The reason for the current status, if any"""
