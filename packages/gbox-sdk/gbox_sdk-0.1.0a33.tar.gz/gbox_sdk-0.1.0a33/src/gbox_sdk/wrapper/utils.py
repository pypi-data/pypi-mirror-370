from typing import Union

from gbox_sdk.types.v1.linux_box import LinuxBox
from gbox_sdk.types.v1.android_box import AndroidBox


def is_android_box(box: Union[AndroidBox, LinuxBox]) -> bool:
    return getattr(box, "type", None) == "android"


def is_linux_box(box: Union[AndroidBox, LinuxBox]) -> bool:
    return getattr(box, "type", None) == "linux"
