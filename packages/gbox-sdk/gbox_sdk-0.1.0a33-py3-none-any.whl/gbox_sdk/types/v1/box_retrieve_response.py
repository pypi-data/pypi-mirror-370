# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import TypeAlias

from .linux_box import LinuxBox
from .android_box import AndroidBox

__all__ = ["BoxRetrieveResponse"]

BoxRetrieveResponse: TypeAlias = Union[LinuxBox, AndroidBox]
