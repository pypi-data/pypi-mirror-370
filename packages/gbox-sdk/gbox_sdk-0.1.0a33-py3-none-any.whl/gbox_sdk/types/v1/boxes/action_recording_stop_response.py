# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["ActionRecordingStopResponse"]


class ActionRecordingStopResponse(BaseModel):
    presigned_url: str = FieldInfo(alias="presignedUrl")
    """Presigned URL of the recording.

    This is a temporary downloadable URL with an expiration time for accessing the
    recording file.
    """

    storage_key: str = FieldInfo(alias="storageKey")
    """Storage key of the recording.

    Before the box is deleted, you can use this storageKey with the endpoint
    `box/:boxId/storage/presigned-url` to get a downloadable URL for the recording.
    """
