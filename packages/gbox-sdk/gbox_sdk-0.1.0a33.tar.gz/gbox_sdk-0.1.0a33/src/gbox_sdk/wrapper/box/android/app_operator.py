from typing import Union

from gbox_sdk._types import NOT_GIVEN, NotGiven
from gbox_sdk._client import GboxClient
from gbox_sdk._response import BinaryAPIResponse
from gbox_sdk.types.v1.android_box import AndroidBox
from gbox_sdk.types.v1.boxes.android_app import AndroidApp
from gbox_sdk.types.v1.boxes.android_list_activities_response import AndroidListActivitiesResponse


class AndroidAppOperator:
    """
    Operator class for managing a specific Android app within a box.

    Provides methods to open, restart, close, list activities, and backup the app.

    Attributes:
        client (GboxClient): The API client used for communication.
        box (AndroidBox): The Android box data object.
        data (AndroidApp): The app data object.
    """

    def __init__(self, client: GboxClient, box: AndroidBox, data: AndroidApp):
        """
        Initialize an AndroidAppOperator instance.

        Args:
            client (GboxClient): The API client used for communication.
            box (AndroidBox): The Android box data object.
            data (AndroidApp): The app data object.
        """
        self.client = client
        self.box = box
        self.data = data

    def open(self, activity_name: Union[str, NotGiven] = NOT_GIVEN) -> None:
        """
        Open the app, optionally specifying an activity name.

        Args:
            activity_name: Activity name, default is the main activity.

        Examples:
            >>> box.app.open()
            >>> box.app.open("com.example.app.MainActivity")
        """
        return self.client.v1.boxes.android.open(
            self.data.package_name, box_id=self.box.id, activity_name=activity_name
        )

    def restart(self, activity_name: Union[str, NotGiven] = NOT_GIVEN) -> None:
        """
        Restart the app, optionally specifying an activity name.

        Args:
            activity_name: Activity name, default is the main activity.

        Examples:
            >>> box.app.restart()
            >>> box.app.restart("com.example.app.MainActivity")
        """
        return self.client.v1.boxes.android.restart(
            self.data.package_name, box_id=self.box.id, activity_name=activity_name
        )

    def close(self) -> None:
        """
        Close the app.

        Examples:
            >>> box.app.close()
        """
        return self.client.v1.boxes.android.close(package_name=self.data.package_name, box_id=self.box.id)

    def list_activities(self) -> AndroidListActivitiesResponse:
        """
        List all activities of the app.

        Returns:
            AndroidListActivitiesResponse: The response containing the list of activities.

        Examples:
            >>> box.app.list_activities()
        """
        return self.client.v1.boxes.android.list_activities(package_name=self.data.package_name, box_id=self.box.id)

    def backup(self) -> BinaryAPIResponse:
        """
        Backup the app.

        Returns:
            BinaryAPIResponse: The backup response containing binary data.

        Examples:
            >>> box.app.backup()
        """
        return self.client.v1.boxes.android.backup(package_name=self.data.package_name, box_id=self.box.id)
