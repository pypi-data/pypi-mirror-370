from typing import TYPE_CHECKING, List, Union
from typing_extensions import Required, Annotated, TypedDict

from gbox_sdk._utils._transform import PropertyInfo
from gbox_sdk.types.v1.boxes.android_install_params import InstallAndroidPkgByURL, InstallAndroidPkgByFile

# Forward references for type annotations
if TYPE_CHECKING:
    from gbox_sdk.wrapper.box.android.app_operator import AndroidAppOperator
    from gbox_sdk.wrapper.box.android.pkg_operator import AndroidPkgOperator


class InstallAndroidAppByLocalFile(TypedDict, total=False):
    apk: Required[str]


AndroidInstall = Union[InstallAndroidPkgByFile, InstallAndroidPkgByURL, InstallAndroidAppByLocalFile]


class ListAndroidApp:
    """Response type for listing Android apps as operators."""

    def __init__(self, operators: List["AndroidAppOperator"]):
        self.operators = operators


class ListAndroidPkg:
    """Response type for listing Android packages as operators."""

    def __init__(self, operators: List["AndroidPkgOperator"]):
        self.operators = operators


class AndroidUninstall(TypedDict, total=False):
    """Parameters for uninstalling an Android package (without box_id)."""

    keep_data: Annotated[bool, PropertyInfo(alias="keepData")]
    """uninstalls the pkg while retaining the data/cache"""
