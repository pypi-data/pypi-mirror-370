from typing_extensions import Union

from gbox_sdk._types import NOT_GIVEN, NotGiven
from gbox_sdk._client import GboxClient


class StorageOperator:
    """
    Operator class for managing storage via the Gbox SDK.
    Provides an interface to interact with and control storage.
    """

    def __init__(self, client: GboxClient, box_id: str):
        """
        Initialize a StorageOperator instance.

        Args:
            client (GboxClient): The Gbox client used for API communication.
            box_id (str): The box id.
        """
        self.client = client
        self.box_id = box_id

    def create_presigned_url(self, storage_key: str, *, expires_in: Union[str, NotGiven] = NOT_GIVEN) -> str:
        """
        Create a presigned url for a storage key.

        This endpoint provides a presigned url
        for a storage key, which can be used to download the file from the storage.

        Args:
            storage_key: Storage key

            expires_in: Presigned url expires in
                Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
                Example formats: "500ms", "30s", "5m", "1h" Default: 30m Maximum allowed: 6h
        """
        return self.client.v1.boxes.storage.presigned_url(
            box_id=self.box_id, storage_key=storage_key, expires_in=expires_in
        )
