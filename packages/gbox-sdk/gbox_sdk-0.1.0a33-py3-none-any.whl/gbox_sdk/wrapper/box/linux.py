from gbox_sdk._client import GboxClient
from gbox_sdk.wrapper.box.base import BaseBox
from gbox_sdk.types.v1.linux_box import LinuxBox


class LinuxBoxOperator(BaseBox):
    """
    Operator class for managing Linux boxes via the Gbox SDK.
    Provides an interface to interact with and control Linux-based boxes.
    """

    def __init__(self, client: GboxClient, data: LinuxBox):
        """
        Initialize a LinuxBoxOperator instance.

        Args:
            client (GboxClient): The Gbox client used for API communication.
            data (LinuxBox): The LinuxBox data model instance representing the box.
        """
        super().__init__(client, data)
