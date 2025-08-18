import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing_extensions import List, Union, Optional, Protocol

from gbox_sdk._types import FileTypes
from gbox_sdk._utils import file_from_path
from gbox_sdk._client import GboxClient
from gbox_sdk.types.v1.boxes.media_get_media_response import MediaGetMediaResponse
from gbox_sdk.types.v1.boxes.media_list_media_response import (
    DataPhoto as MediaListMediaPhotoResponse,
    DataVideo as MediaListMediaVideoResponse,
    MediaListMediaResponse,
)
from gbox_sdk.types.v1.boxes.media_list_albums_response import MediaListAlbumsResponse
from gbox_sdk.types.v1.boxes.media_get_album_detail_response import MediaGetAlbumDetailResponse
from gbox_sdk.types.v1.boxes.media_get_media_support_response import MediaGetMediaSupportResponse


@dataclass
class DownloadResult:
    """Result of a single media download operation"""

    success: bool
    file_name: str
    file_path: Optional[str] = None
    error: Optional[str] = None


@dataclass
class DownloadSummary:
    """Summary of album download operation"""

    total_files: int
    successful: int
    failed: int
    results: List[DownloadResult]


media_support_cache: Union[MediaGetMediaSupportResponse, None] = None


def get_media_support(client: GboxClient, box_id: str) -> MediaGetMediaSupportResponse:
    """
    Get supported media extensions from the API
    """
    global media_support_cache
    if media_support_cache is None:
        media_support_cache = client.v1.boxes.media.get_media_support(box_id=box_id)
    return media_support_cache


def is_media_file(file_path: str, client: GboxClient, box_id: str) -> bool:
    """
    Check if a file is an image or video based on its extension
    """
    # Extract lower-cased extension with leading dot (e.g., ".jpg")
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    media_support = get_media_support(client, box_id)

    # Normalize supported extensions to include a leading dot and be lower-cased
    photo_extensions = [
        e if e.startswith(".") else f".{e}" for e in (ext_str.lower() for ext_str in media_support.photo)
    ]
    video_extensions = [
        e if e.startswith(".") else f".{e}" for e in (ext_str.lower() for ext_str in media_support.video)
    ]

    return ext in photo_extensions or ext in video_extensions


def get_media_files_from_directory(dir_path: str, client: GboxClient, box_id: str) -> List[str]:
    """
    Recursively get all media files from a directory
    """
    media_files: List[str] = []

    try:
        items = os.listdir(dir_path)

        for item in items:
            full_path = os.path.join(dir_path, item)
            stat = os.stat(full_path)

            if stat.st_mode & 0o40000:  # Check if directory
                # Recursively process subdirectories
                sub_files = get_media_files_from_directory(full_path, client, box_id)
                media_files.extend(sub_files)
            elif stat.st_mode & 0o100000:  # Check if regular file
                # Only include image and video files
                if is_media_file(full_path, client, box_id):
                    media_files.append(full_path)
    except OSError as error:
        raise OSError(f"Error reading directory {dir_path}: {error}") from error

    return media_files


def process_media_item(item: str, client: GboxClient, box_id: str) -> List[FileTypes]:
    """
    Process a media item and return a list of FileTypes
    """
    processed_media: List[FileTypes] = []

    # Handle file:// protocol or local file paths
    if item.startswith("file://"):
        from urllib.parse import unquote, urlparse

        parsed = urlparse(item)
        file_path = unquote(parsed.path)
    else:
        file_path = item

    # Check if path exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Path {file_path} does not exist")

    # Get file stats
    stat = os.stat(file_path)

    if stat.st_mode & 0o40000:  # Check if directory
        # If it's a directory, get all media files from it
        media_files = get_media_files_from_directory(file_path, client, box_id)
        for media_file in media_files:
            processed_media.append(file_from_path(media_file))
    elif stat.st_mode & 0o100000:  # Check if regular file
        # If it's a file, check if it's a media file
        if is_media_file(file_path, client, box_id):
            processed_media.append(file_from_path(file_path))
        else:
            raise ValueError(f"File {file_path} is not a supported image or video file")
    else:
        raise ValueError(f"Path {file_path} is neither a file nor a directory")

    return processed_media


def process_media_array(media: List[Union[FileTypes, str]], client: GboxClient, box_id: str) -> List[FileTypes]:
    processed: List[FileTypes] = []

    for item in media:
        if isinstance(item, str):
            processed.extend(process_media_item(item, client, box_id))
        else:
            processed.append(item)

    return processed


class MediaItemOperator:
    def __init__(
        self,
        client: GboxClient,
        box_id: str,
        album_name: str,
        data: Union[MediaListMediaPhotoResponse, MediaListMediaVideoResponse],
    ):
        self.client = client
        self.box_id = box_id
        self.album_name = album_name
        self.data = data

    def get_info(self) -> MediaGetMediaResponse:
        """
        Get the info of the media item.

        Example:
            >>> media.get_info()
        """
        return self.client.v1.boxes.media.get_media(
            box_id=self.box_id,
            album_name=self.album_name,
            media_name=self.data.name,
        )

    def download(self, file_path: Optional[str] = None) -> bytes:
        """
        Download media file and optionally save to file system.

        Args:
            file_path: Optional file path to save the downloaded media.
                      If provided, the media will be saved to the specified path.
                      If not provided, only the binary data is returned.

        Returns:
            bytes: The binary data of the downloaded media.

        Example:
            # Return binary data only
            blob = media.download()

            # Download and save to file, then return blob
            blob = media.download("path/to/your/file")
        """
        res = self.client.v1.boxes.media.download_media(
            media_name=self.data.name,
            box_id=self.box_id,
            album_name=self.album_name,
        )

        # Get binary data from response
        binary_data = res.read()

        # If file path is provided, write to file system
        if file_path:
            # Create directory if it doesn't exist
            dir_path = os.path.dirname(file_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)

            # Write binary data to file
            with open(file_path, "wb") as f:
                f.write(binary_data)

        return binary_data


class MediaAlbumOperator:
    class AlbumInfoLike(Protocol):
        last_modified: datetime
        media_count: float
        name: str
        path: str

    def __init__(self, client: GboxClient, box_id: str, data: "MediaAlbumOperator.AlbumInfoLike"):
        self.client = client
        self.box_id = box_id
        self.data = data

    def list_media_info(self) -> MediaListMediaResponse:
        """
        List all media info in the album.
        """
        return self.client.v1.boxes.media.list_media(box_id=self.box_id, album_name=self.data.name)

    def list_media(self) -> List[MediaItemOperator]:
        """
        List all media in the album.

        Returns:
            List[MediaItemOperator]: A list of MediaItemOperator instances for each media item.

        Example:
            >>> media_items = album.list_media()
        """
        res = self.list_media_info()
        return [MediaItemOperator(self.client, self.box_id, self.data.name, media) for media in res.data]

    def download(self, local_path: str) -> DownloadSummary:
        """
        Download all media files from the album to the specified local folder

        Args:
            local_path: Local directory path to save the downloaded media files

        Returns:
            DownloadSummary: Summary of the download operation including success/failure counts

        Example:
            >>> album.download("path/to/your/folder")
        """
        # Ensure the target directory exists
        Path(local_path).mkdir(parents=True, exist_ok=True)

        # Get all media files in the album
        media_list = self.list_media()

        # Download each media file
        results: List[DownloadResult] = []
        for media_item in media_list:
            try:
                # Get media info to get the file name
                media_info = media_item.get_info()
                file_name = media_info.name
                file_path = os.path.join(local_path, file_name)

                # Download the media file
                media_item.download(file_path)
                results.append(DownloadResult(success=True, file_name=file_name, file_path=file_path))
            except Exception as error:
                results.append(
                    DownloadResult(
                        success=False,
                        file_name=getattr(media_item.data, "name", "unknown"),
                        error=str(error),
                    )
                )

        # Calculate summary statistics
        successful = len([r for r in results if r.success])
        failed = len([r for r in results if not r.success])

        return DownloadSummary(
            total_files=len(results),
            successful=successful,
            failed=failed,
            results=results,
        )

    def append_media(self, media: List[Union[FileTypes, str]]) -> "MediaAlbumOperator":
        """
        Append one or more media files to this album.

        Examples:
            >>> album.append_media(["/path/to/file.jpg"])  # from local file path
            >>> album.append_media(["file:///path/to/file.jpg"])  # from file URL
            >>> album.append_media(["/path/to/folder"])  # add all files from folder recursively
        """
        processed_media = process_media_array(media, self.client, self.box_id)
        self.client.v1.boxes.media.update_album(
            self.data.name,
            box_id=self.box_id,
            media=processed_media,
        )
        return self

    def delete_media(self, media_name: str) -> None:
        """
        Delete a media file from the album.

        Examples:
            >>> album.delete_media("My Media")
        """
        return self.client.v1.boxes.media.delete_media(
            box_id=self.box_id,
            album_name=self.data.name,
            media_name=media_name,
        )


class MediaOperator:
    """
    Operator class for managing media operations within a box.
    Provides an interface to interact with and control media operations
    within a box.
    """

    def __init__(self, client: GboxClient, box_id: str):
        """
        Initialize a MediaOperator instance.

        Args:
            client (GboxClient): The Gbox client used for API communication.
            box_id (str): The ID of the box to operate on.
        """
        self.client = client
        self.box_id = box_id

    def list_albums(self) -> List[MediaAlbumOperator]:
        """
        List all albums in the box.

        Examples:
            >>> albums = box.media.list_albums()
        """
        res = self.client.v1.boxes.media.list_albums(box_id=self.box_id)
        return [MediaAlbumOperator(self.client, self.box_id, album) for album in res.data]

    def list_albums_info(self) -> MediaListAlbumsResponse:
        """
        Get a list of albums in the box.

        Examples:
            >>> albums = box.media.list_albums_info()
        """
        return self.client.v1.boxes.media.list_albums(box_id=self.box_id)

    def create_album(self, *, name: str, media: List[Union[FileTypes, str]]) -> MediaAlbumOperator:
        """
        Create a new album in the box.

        Args:
          name: Name of the album to create

          media: Media files to include in the album (max size: 512MB per file)

        Examples:
            >>> album = box.media.create_album("My Album")
        """
        processed_media = process_media_array(media, self.client, self.box_id)
        res = self.client.v1.boxes.media.create_album(box_id=self.box_id, name=name, media=processed_media)
        return MediaAlbumOperator(self.client, self.box_id, res)

    def delete_album(self, album_name: str) -> None:
        """
        Delete an album from the box.

        Examples:
            >>> box.media.delete_album("My Album")
        """
        return self.client.v1.boxes.media.delete_album(box_id=self.box_id, album_name=album_name)

    def get_album_info(self, album_name: str) -> MediaGetAlbumDetailResponse:
        """
        Get the info of an album.

        Examples:
            >>> album = box.media.get_album_info("My Album")
        """
        return self.client.v1.boxes.media.get_album_detail(box_id=self.box_id, album_name=album_name)

    def get_album(self, album_name: str) -> MediaAlbumOperator:
        """
        Get an album.

        Examples:
            >>> album = box.media.get_album("My Album")
        """
        res = self.get_album_info(album_name)
        return MediaAlbumOperator(self.client, self.box_id, res)

    def get_media_support(self) -> MediaGetMediaSupportResponse:
        """
        Get the media support of the box.

        Examples:
            >>> support = box.media.get_media_support()
        """
        return self.client.v1.boxes.media.get_media_support(box_id=self.box_id)
