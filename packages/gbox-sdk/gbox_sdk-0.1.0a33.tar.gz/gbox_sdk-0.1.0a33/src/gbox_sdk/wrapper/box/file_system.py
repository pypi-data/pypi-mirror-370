from typing import List, Union, Optional

from gbox_sdk._types import NOT_GIVEN, NotGiven
from gbox_sdk._client import GboxClient
from gbox_sdk.types.v1.boxes.f_write_params import FileTypes
from gbox_sdk.types.v1.boxes.f_list_response import Data, DataDir, DataFile, FListResponse
from gbox_sdk.types.v1.boxes.f_read_response import FReadResponse
from gbox_sdk.types.v1.boxes.f_write_response import FWriteResponse
from gbox_sdk.types.v1.boxes.f_exists_response import FExistsResponse
from gbox_sdk.types.v1.boxes.f_remove_response import FRemoveResponse
from gbox_sdk.types.v1.boxes.f_rename_response import FRenameResponse


class FileSystemOperator:
    """
    Operator for file system operations within a box.

    Provides methods to list, read, write, remove, check existence, rename, and retrieve file or directory information in a box.

    Args:
        client (GboxClient): The Gbox client instance.
        box_id (str): The ID of the box to operate on.
    """

    def __init__(self, client: GboxClient, box_id: str):
        self.client = client
        self.box_id = box_id

    def list_info(
        self,
        path: str,
        *,
        depth: Union[float, NotGiven] = NOT_GIVEN,
        working_dir: Union[str, NotGiven] = NOT_GIVEN,
    ) -> FListResponse:
        """
        Get detailed information about files and directories at a given path or with given parameters.

        Args:
            path: Target directory path in the box

            depth: Depth of the directory

            working_dir: Working directory. If not provided, the file will be read from the
                `box.config.workingDir` directory.

        Returns:
            FListResponse: The response containing file/directory information.

        Example:
            >>> box.file_system.list_info(path="/path/to/directory", depth=1, working_dir="/path/to/working_dir")
            >>> box.file_system.list_info("/path/to/directory")
        """
        return self.client.v1.boxes.fs.list(box_id=self.box_id, path=path, depth=depth, working_dir=working_dir)

    def list(
        self,
        path: str,
        *,
        depth: Union[float, NotGiven] = NOT_GIVEN,
        working_dir: Union[str, NotGiven] = NOT_GIVEN,
    ) -> List[Union["FileOperator", "DirectoryOperator"]]:
        """
        List files and directories at a given path or with given parameters, returning operator objects.

        Args:
            path: Target directory path in the box

            depth: Depth of the directory

            working_dir: Working directory. If not provided, the file will be read from the
                `box.config.workingDir` directory.

        Returns:
            List[Union[FileOperator, DirectoryOperator]]: List of file or directory operator objects.

        Example:
            >>> box.file_system.list(path="/path/to/directory", depth=1, working_dir="/path/to/working_dir")
            >>> box.file_system.list("/path/to/directory")
        """
        res = self.list_info(path, depth=depth, working_dir=working_dir)
        return [self._data_to_operator(r) for r in res.data]

    def read(
        self,
        path: str,
        *,
        working_dir: Union[str, NotGiven] = NOT_GIVEN,
    ) -> FReadResponse:
        """
        Read the content of a file.

        Args:
            path: Target path in the box. If the path does not start with '/', the file will be
                read from the working directory.

            working_dir: Working directory. If not provided, the file will be read from the
                `box.config.workingDir` directory.

        Returns:
            FReadResponse: The response containing file content.

        Example:
            >>> box.file_system.read(path="/path/to/file", working_dir="/path/to/working_dir")
            >>> box.file_system.read("/path/to/file")
        """
        return self.client.v1.boxes.fs.read(box_id=self.box_id, path=path, working_dir=working_dir)

    def write(
        self, *, content: Union[str, FileTypes], path: str, working_dir: Union[str, NotGiven] = NOT_GIVEN
    ) -> "FileOperator":
        """
        Write content to a file (text or binary).

        Args:
            content: Content of the file (Max size: 512MB)

            path: Target path in the box. If the path does not start with '/', the file will be
                written relative to the working directory. Creates necessary directories in the
                path if they don't exist. If the target path already exists, the write will
                fail.

            working_dir: Working directory. If not provided, the file will be read from the
                `box.config.workingDir` directory.

        Returns:
            FileOperator: The file operator for the written file.

        Example:
            >>> box.file_system.write(content="Hello, World!", path="/path/to/file", working_dir="/path/to/working_dir")
            >>> box.file_system.write(content="Hello, World!", path="/path/to/file")
        """
        res = self.client.v1.boxes.fs.write(
            box_id=self.box_id, content=content, path=path, working_dir=working_dir if working_dir else NOT_GIVEN
        )

        # Convert FWriteResponse to DataFile format for FileOperator
        data_file = DataFile(
            path=res.path, type="file", mode=res.mode, name=res.name, size=res.size, lastModified=res.last_modified
        )

        return FileOperator(self.client, self.box_id, data_file)

    def remove(self, path: str, *, working_dir: Union[str, NotGiven] = NOT_GIVEN) -> FRemoveResponse:
        """
        Remove a file or directory.

        Args:
            path: Target path in the box. If the path does not start with '/', the file/directory
                will be checked relative to the working directory

            working_dir: Working directory. If not provided, the file will be read from the
                `box.config.workingDir` directory.

        Returns:
            FRemoveResponse: The response after removing the file or directory.

        Example:
            >>> box.file_system.remove(path="/path/to/file", working_dir="/path/to/working_dir")
            >>> box.file_system.remove("/path/to/file")
        """
        return self.client.v1.boxes.fs.remove(box_id=self.box_id, path=path, working_dir=working_dir)

    def exists(self, path: str, *, working_dir: Union[str, NotGiven] = NOT_GIVEN) -> FExistsResponse:
        """
        Check if a file or directory exists.

        Args:
            path: Target path in the box. If the path does not start with '/', the file/directory
                will be checked relative to the working directory

            working_dir: Working directory. If not provided, the file will be read from the
                `box.config.workingDir` directory.

        Returns:
            FExistsResponse: The response indicating existence.

        Example:
            >>> box.file_system.exists(path="/path/to/file", working_dir="/path/to/working_dir")
            >>> box.file_system.exists("/path/to/file")
        """
        return self.client.v1.boxes.fs.exists(box_id=self.box_id, path=path, working_dir=working_dir)

    def rename(self, *, old_path: str, new_path: str, working_dir: Union[str, NotGiven] = NOT_GIVEN) -> FRenameResponse:
        """
        Rename a file or directory.

        Args:
          new_path: New path in the box. If the path does not start with '/', the file/directory
              will be renamed relative to the working directory. If the newPath already
              exists, the rename will fail.

          old_path: Old path in the box. If the path does not start with '/', the file/directory
              will be renamed relative to the working directory. If the oldPath does not
              exist, the rename will fail.

          working_dir: Working directory. If not provided, the file will be read from the
              `box.config.workingDir` directory.

        Returns:
            FRenameResponse: The response after renaming.

        Example:
            >>> box.file_system.rename(
            ...     old_path="/path/to/old/file", new_path="/path/to/new/file", working_dir="/path/to/working_dir"
            ... )
        """
        return self.client.v1.boxes.fs.rename(
            box_id=self.box_id, old_path=old_path, new_path=new_path, working_dir=working_dir
        )

    def get(
        self, path: str, *, working_dir: Union[str, NotGiven] = NOT_GIVEN
    ) -> Union["FileOperator", "DirectoryOperator"]:
        """
        Get an operator for a file or directory by its information.

        Args:
            path: Target path in the box. If the path does not start with '/', the file/directory
                will be checked relative to the working directory

            working_dir: Working directory. If not provided, the file will be read from the
                `box.config.workingDir` directory.

        Returns:
            Union[FileOperator, DirectoryOperator]: The corresponding operator object.

        Example:
            >>> box.file_system.get(path="/path/to/file", working_dir="/path/to/working_dir")
            >>> box.file_system.get("/path/to/file")
        """
        res = self.client.v1.boxes.fs.info(box_id=self.box_id, path=path, working_dir=working_dir)
        if res.type == "file":
            data_file = DataFile(
                path=res.path, type="file", mode=res.mode, name=res.name, size=res.size, lastModified=res.last_modified
            )
            return FileOperator(self.client, self.box_id, data_file)
        else:
            data_dir = DataDir(path=res.path, type="dir", mode=res.mode, name=res.name, lastModified=res.last_modified)
            return DirectoryOperator(self.client, self.box_id, data_dir)

    def _data_to_operator(self, data: Optional[Data]) -> Union["FileOperator", "DirectoryOperator"]:
        """
        Convert a Data object to the corresponding operator.

        Args:
            data (Optional[Data]): The data object to convert.
        Returns:
            Union[FileOperator, DirectoryOperator]: The corresponding operator object.
        Raises:
            ValueError: If data is None.
        """
        if data is None:
            raise ValueError("data is None")
        if data.type == "file":
            return FileOperator(self.client, self.box_id, data)
        else:
            return DirectoryOperator(self.client, self.box_id, data)


class FileOperator:
    """
    Operator for file operations within a box.

    Provides methods to read, write, and rename a file.

    Args:
        client (GboxClient): The Gbox client instance.
        box_id (str): The ID of the box to operate on.
        data (DataFile): The file data.
    """

    def __init__(self, client: GboxClient, box_id: str, data: DataFile):
        self.client = client
        self.box_id = box_id
        self.data = data

    def write(self, content: Union[str, FileTypes], *, working_dir: Union[str, NotGiven] = NOT_GIVEN) -> FWriteResponse:
        """
        Write content to this file (text or binary).

        Args:
            content: The content to write to the file.
            working_dir: The working directory to write the file to.

        Returns:
            FWriteResponse: The response after writing.

        Example:
            >>> box.file_system.write(content="Hello, World!", path="/path/to/file", working_dir="/path/to/working_dir")
            >>> box.file_system.write("Hello, World!")
        """
        return self.client.v1.boxes.fs.write(
            box_id=self.box_id,
            content=content,
            path=self.data.path,
            working_dir=working_dir if working_dir else NOT_GIVEN,
        )

    def read(self, *, working_dir: Union[str, NotGiven] = NOT_GIVEN) -> FReadResponse:
        """
        Read the content of this file.

        Args:
            working_dir: The working directory to read the file from.

        Returns:
            FReadResponse: The response containing file content.

        Example:
            >>> box.file_system.read(working_dir="/path/to/working_dir")
            >>> box.file_system.read()
        """
        return self.client.v1.boxes.fs.read(box_id=self.box_id, path=self.data.path, working_dir=working_dir)

    def rename(self, new_path: str, *, working_dir: Union[str, NotGiven] = NOT_GIVEN) -> FRenameResponse:
        """
        Rename this file.

        Args:
            new_path: The new path of the file.
            working_dir: The working directory to rename the file in.

        Returns:
            FRenameResponse: The response after renaming.

        Example:
            >>> box.file_system.rename(new_path="/path/to/new/file", working_dir="/path/to/working_dir")
        """
        return self.client.v1.boxes.fs.rename(
            box_id=self.box_id, old_path=self.data.path, new_path=new_path, working_dir=working_dir
        )


class DirectoryOperator:
    """
    Operator for directory operations within a box.

    Provides methods to list and rename a directory.

    Args:
        client (GboxClient): The Gbox client instance.
        box_id (str): The ID of the box to operate on.
        data (DataDir): The directory data.
    """

    def __init__(self, client: GboxClient, box_id: str, data: DataDir):
        self.client = client
        self.box_id = box_id
        self.data = data

    def list_info(
        self, *, depth: Union[float, NotGiven] = NOT_GIVEN, working_dir: Union[str, NotGiven] = NOT_GIVEN
    ) -> FListResponse:
        """
        Get detailed information about files and directories in this directory.

        Args:
            path: Target directory path in the box

            depth: Depth of the directory

            working_dir: Working directory. If not provided, the file will be read from the
                `box.config.workingDir` directory.

        Returns:
            FListResponse: The response containing file/directory information.

        Example:
            >>> box.file_system.list_info(path="/path/to/directory", depth=1, working_dir="/path/to/working_dir")
            >>> box.file_system.list_info("/path/to/directory")
        """
        return self.client.v1.boxes.fs.list(
            box_id=self.box_id, path=self.data.path, depth=depth, working_dir=working_dir
        )

    def list(
        self, *, depth: Union[float, NotGiven] = NOT_GIVEN, working_dir: Union[str, NotGiven] = NOT_GIVEN
    ) -> List[Union["FileOperator", "DirectoryOperator"]]:
        """
        List files and directories in this directory, returning operator objects.

        Args:
            path: Target directory path in the box

            depth: Depth of the directory

            working_dir: Working directory. If not provided, the file will be read from the
                `box.config.workingDir` directory.

        Returns:
            List[Union[FileOperator, DirectoryOperator]]: List of file or directory operator objects.

        Example:
            >>> box.file_system.list(path="/path/to/directory", depth=1, working_dir="/path/to/working_dir")
            >>> box.file_system.list("/path/to/directory")
        """
        res = self.list_info(depth=depth, working_dir=working_dir)
        result: List[Union["FileOperator", "DirectoryOperator"]] = []
        for r in res.data:
            if r.type == "file":
                file = DataFile(
                    path=r.path, type=r.type, mode=r.mode, name=r.name, size=r.size, lastModified=r.last_modified
                )
                result.append(FileOperator(self.client, self.box_id, file))
            else:
                dir = DataDir(path=r.path, type=r.type, mode=r.mode, name=r.name, lastModified=r.last_modified)
                result.append(DirectoryOperator(self.client, self.box_id, dir))
        return result

    def rename(self, *, new_path: str, working_dir: Union[str, NotGiven] = NOT_GIVEN) -> FRenameResponse:
        """
        Rename this directory.

        Args:
          new_path: New path in the box. If the path does not start with '/', the file/directory
              will be renamed relative to the working directory. If the newPath already
              exists, the rename will fail.

          working_dir: Working directory. If not provided, the file will be read from the
              `box.config.workingDir` directory.

        Returns:
            FRenameResponse: The response after renaming.

        Example:
            >>> box.file_system.rename(
            ...     old_path="/path/to/old/file", new_path="/path/to/new/file", working_dir="/path/to/working_dir"
            ... )
            >>> box.file_system.rename("/path/to/old/file", "/path/to/new/file")
        """
        return self.client.v1.boxes.fs.rename(
            box_id=self.box_id, old_path=self.data.path, new_path=new_path, working_dir=working_dir
        )
