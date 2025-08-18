from typing import Union

from gbox_sdk._client import GboxClient
from gbox_sdk._response import BinaryAPIResponse
from gbox_sdk.types.v1.android_box import AndroidBox
from gbox_sdk.types.v1.boxes.android_open_params import AndroidOpenParams
from gbox_sdk.types.v1.boxes.android_get_response import AndroidGetResponse
from gbox_sdk.types.v1.boxes.android_restart_params import AndroidRestartParams
from gbox_sdk.types.v1.boxes.android_list_activities_response import AndroidListActivitiesResponse


class AndroidPkgOperator:
    """
    Operator class for managing a specific Android package within a box.

    Provides methods to open, close, restart, list activities, and backup the package.

    Attributes:
        client (GboxClient): The API client used for communication.
        box (AndroidBox): The Android box data object.
        data (AndroidGetResponse): The package data object.
    """

    def __init__(self, client: GboxClient, box: AndroidBox, data: AndroidGetResponse):
        """
        Initialize an AndroidPkgOperator instance.

        Args:
            client (GboxClient): The API client used for communication.
            box (AndroidBox): The Android box data object.
            data (AndroidGetResponse): The package data object.
        """
        self.client = client
        self.box = box
        self.data = data

    def open(self, activity_name: Union[str, None] = None) -> None:
        """
        Open the package, optionally specifying an activity name.

        Args:
            activity_name: Activity name, default is the main activity.

        Examples:
            >>> box.pkg.open()
            >>> box.pkg.open("com.example.app.MainActivity")
        """
        params = AndroidOpenParams(box_id=self.box.id)
        if activity_name is not None:
            params["activity_name"] = activity_name
        self.client.v1.boxes.android.open(self.data.package_name, **params)
        self._sync_data()

    def close(self) -> None:
        """
        Close the package.
        """
        self.client.v1.boxes.android.close(self.data.package_name, box_id=self.box.id)
        self._sync_data()

    def restart(self, activity_name: Union[str, None] = None) -> None:
        """
        Restart the package, optionally specifying an activity name.

        Args:
            activity_name: Activity name, default is the main activity.

        Examples:
            >>> box.pkg.restart()
            >>> box.pkg.restart("com.example.app.MainActivity")
        """
        params = AndroidRestartParams(box_id=self.box.id)
        if activity_name is not None:
            params["activity_name"] = activity_name
        self.client.v1.boxes.android.restart(self.data.package_name, **params)
        self._sync_data()

    def list_activities(self) -> AndroidListActivitiesResponse:
        """
        List all activities of the package.

        Returns:
            AndroidListActivitiesResponse: The response containing the list of activities.

        Examples:
            >>> box.pkg.list_activities()
        """
        return self.client.v1.boxes.android.list_activities(self.data.package_name, box_id=self.box.id)

    def backup(self) -> BinaryAPIResponse:
        """
        Backup the package.

        Returns:
            BinaryAPIResponse: The backup response containing binary data.

        Examples:
            >>> box.pkg.backup()
        """
        return self.client.v1.boxes.android.backup(self.data.package_name, box_id=self.box.id)

    def _sync_data(self) -> None:
        """
        Sync the data of the package.
        """
        res = self.client.v1.boxes.android.get(self.data.package_name, box_id=self.box.id)
        self.data = res
