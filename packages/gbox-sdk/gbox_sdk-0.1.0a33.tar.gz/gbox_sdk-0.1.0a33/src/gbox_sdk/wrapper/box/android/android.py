from gbox_sdk._client import GboxClient
from gbox_sdk.wrapper.box.base import BaseBox
from gbox_sdk.types.v1.android_box import AndroidBox
from gbox_sdk.wrapper.box.android.app_manager import AndroidAppManager
from gbox_sdk.wrapper.box.android.pkg_manager import AndroidPkgManager


class AndroidBoxOperator(BaseBox):
    """
    Operator class for managing Android boxes, providing access to app and package management functionalities.

    Attributes:
        app (AndroidAppManager): Manager for Android app operations.
        pkg (AndroidPkgManager): Manager for Android package operations.
    """

    def __init__(self, client: GboxClient, data: AndroidBox):
        """
        Initialize an AndroidBoxOperator instance.

        Args:
            client (GboxClient): The API client used for communication.
            data (AndroidBox): The Android box data object.
        """
        super().__init__(client, data)
        self.app = AndroidAppManager(client, data)
        self.pkg = AndroidPkgManager(client, data)
