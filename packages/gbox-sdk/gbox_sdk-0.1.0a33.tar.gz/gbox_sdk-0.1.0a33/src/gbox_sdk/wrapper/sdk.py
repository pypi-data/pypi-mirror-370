from typing import Any, List, Union, Mapping, Optional, cast, overload
from typing_extensions import Literal, TypedDict

import httpx

from gbox_sdk import GboxClient
from gbox_sdk._types import NOT_GIVEN, Timeout, NotGiven
from gbox_sdk.wrapper.utils import is_linux_box, is_android_box
from gbox_sdk.wrapper.box.linux import LinuxBoxOperator
from gbox_sdk.types.v1.linux_box import LinuxBox
from gbox_sdk.types.v1.android_box import AndroidBox
from gbox_sdk.types.v1.box_list_response import BoxListResponse
from gbox_sdk.wrapper.box.android.android import AndroidBoxOperator
from gbox_sdk.types.v1.box_retrieve_response import BoxRetrieveResponse
from gbox_sdk.types.v1.box_create_linux_params import Config as LinuxConfig
from gbox_sdk.types.v1.box_create_android_params import Config as AndroidConfig

BoxOperator = Union[AndroidBoxOperator, LinuxBoxOperator]


class _CreateAndroidRequired(TypedDict):
    """Required fields for CreateAndroid."""

    type: Literal["android"]


class _CreateAndroidOptional(TypedDict, total=False):
    """Optional fields for CreateAndroid."""

    config: AndroidConfig
    wait: bool


class CreateAndroid(_CreateAndroidRequired, _CreateAndroidOptional):
    """Parameters for creating an Android box with type specification."""

    pass


class _CreateLinuxRequired(TypedDict):
    """Required fields for CreateLinux."""

    type: Literal["linux"]


class _CreateLinuxOptional(TypedDict, total=False):
    """Optional fields for CreateLinux."""

    config: LinuxConfig
    wait: bool


class CreateLinux(_CreateLinuxRequired, _CreateLinuxOptional):
    """Parameters for creating a Linux box with type specification."""

    pass


CreateParams = Union[CreateAndroid, CreateLinux]


class BoxListOperatorResponse:
    def __init__(
        self,
        operators: List[BoxOperator],
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        total: Optional[int] = None,
    ):
        self.operators = operators
        self.page = page
        self.page_size = page_size
        self.total = total


class GboxSDK:
    """
    GboxSDK provides a high-level interface for managing and operating Gbox containers (boxes).

    This SDK allows users to create, list, retrieve, and terminate both Android and Linux boxes, and provides
    operator objects for further box-specific operations. It wraps the lower-level GboxClient and exposes
    convenient methods for common workflows.

    Attributes:
        client (GboxClient): The underlying client used for API communication.

    Examples:
        Initialize the SDK:
        ```python
        from gbox_sdk.wrapper import GboxSDK

        # Initialize the SDK
        sdk = GboxSDK(api_key="your-api-key")
        ```

        Create boxes using the unified create method:
        ```python
        # Create an Android box
        android_box = sdk.create(type="android", config={"labels": {"env": "test"}})

        # Create a Linux box
        linux_box = sdk.create(type="linux", config={"envs": {"PYTHON_VERSION": "3.9"}})
        ```

        List and manage boxes:
        ```python
        # List all boxes
        boxes = sdk.list()

        # Get a specific box
        box = sdk.get(box_id="box_id")

        # Terminate a box
        sdk.terminate(box_id="box_id")
        ```
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[Union[str, httpx.URL]] = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: Optional[int] = None,
        default_headers: Optional[Mapping[str, str]] = None,
        default_query: Optional[Mapping[str, object]] = None,
        http_client: Optional[httpx.Client] = None,
        _strict_response_validation: Optional[bool] = None,
    ):
        """
        Initialize the GboxSDK instance.

        Args:
            api_key (Optional[str]): API key for authentication.
            base_url (Optional[Union[str, httpx.URL]]): Base URL for the API.
            timeout (Union[float, Timeout, None, NotGiven]): Request timeout setting.
            max_retries (Optional[int]): Maximum number of retries for failed requests.
            default_headers (Optional[Mapping[str, str]]): Default headers to include in requests.
            default_query (Optional[Mapping[str, object]]): Default query parameters for requests.
            http_client (Optional[httpx.Client]): Custom HTTP client instance.
            _strict_response_validation (Optional[bool]): Whether to strictly validate API responses.
        """
        self.client = GboxClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries if max_retries is not None else 2,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation
            if _strict_response_validation is not None
            else False,
        )

    @overload
    def create(
        self,
        *,
        type: Literal["android"],
        config: Union[AndroidConfig, NotGiven] = NOT_GIVEN,
        wait: Union[bool, NotGiven] = NOT_GIVEN,
    ) -> AndroidBoxOperator:
        """Create a new Android box and return its operator."""
        ...

    @overload
    def create(
        self,
        *,
        type: Literal["linux"],
        config: Union[LinuxConfig, NotGiven] = NOT_GIVEN,
        wait: Union[bool, NotGiven] = NOT_GIVEN,
    ) -> LinuxBoxOperator:
        """Create a new Linux box and return its operator."""
        ...

    def create(
        self,
        *,
        type: Union[Literal["android"], Literal["linux"]],
        config: Union[AndroidConfig, LinuxConfig, NotGiven] = NOT_GIVEN,
        wait: Union[bool, NotGiven] = NOT_GIVEN,
        timeout: Union[str, NotGiven] = NOT_GIVEN,
    ) -> BoxOperator:
        """
        Create a new box and return its operator.

        This method provides a unified interface for creating both Android and Linux boxes.
        The box type is determined by the 'type' parameter.

        Args:
            type: The type of box to create, either 'android' or 'linux'.
            config: Configuration for the box (optional).
            wait: Whether to wait for the box operation to complete (optional).
            timeout: Timeout for the box operation (optional).

        Returns:
            BoxOperator: Operator for the created box (AndroidBoxOperator or LinuxBoxOperator).

        Raises:
            ValueError: If an unsupported box type is provided.

        Examples:
            Create an Android box:
            ```python
            android_box = sdk.create(type="android", config={"labels": {"env": "test"}})
            ```

            Create a Linux box:
            ```python
            linux_box = sdk.create(type="linux", config={"envs": {"PYTHON_VERSION": "3.9"}})
            ```
        """
        if type == "android":
            android_res = self.client.v1.boxes.create_android(
                config=cast(AndroidConfig, config),
                wait=wait,
                api_timeout=timeout,
            )
            return AndroidBoxOperator(self.client, android_res)
        elif type == "linux":
            linux_res = self.client.v1.boxes.create_linux(
                config=cast(LinuxConfig, config),
                wait=wait,
                api_timeout=timeout,
            )
            return LinuxBoxOperator(self.client, linux_res)
        else:
            raise ValueError(f"Unsupported box type: {type}")

    def list_info(
        self,
        *,
        device_type: Union[str, NotGiven] = NOT_GIVEN,
        labels: Union[object, NotGiven] = NOT_GIVEN,
        page: Union[int, NotGiven] = NOT_GIVEN,
        page_size: Union[int, NotGiven] = NOT_GIVEN,
        status: Union[List[Literal["all", "pending", "running", "error", "terminated"]], NotGiven] = NOT_GIVEN,
        type: Union[List[Literal["all", "linux", "android"]], NotGiven] = NOT_GIVEN,
    ) -> BoxListResponse:
        """
        List information of all boxes matching the query.

        Args:
            device_type: Filter boxes by their device type (virtual, physical)
            labels: Filter boxes by their labels.
            page: Page number
            page_size: Page size
            status: Filter boxes by their current status (pending, running, stopped, error, terminated, all). Must be an array of statuses. Use 'all' to get boxes with any status.
            type: Filter boxes by their type (linux, android, all). Must be an array of types. Use 'all' to get boxes of any type.

        Returns:
            BoxListResponse: Response containing box information.

        Examples:
            ```python
            # List all boxes
            boxes = sdk.list_info()

            # List with pagination
            boxes = sdk.list_info(page=1, page_size=10)
            ```
        """
        return self.client.v1.boxes.list(
            device_type=device_type,
            labels=labels,
            page=page,
            page_size=page_size,
            status=status,
            type=type,
        )

    def list(
        self,
        *,
        device_type: Union[str, NotGiven] = NOT_GIVEN,
        labels: Union[object, NotGiven] = NOT_GIVEN,
        page: Union[int, NotGiven] = NOT_GIVEN,
        page_size: Union[int, NotGiven] = NOT_GIVEN,
        status: Union[List[Literal["all", "pending", "running", "error", "terminated"]], NotGiven] = NOT_GIVEN,
        type: Union[List[Literal["all", "linux", "android"]], NotGiven] = NOT_GIVEN,
    ) -> BoxListOperatorResponse:
        """
        List all boxes matching the query and return their operator objects.

        Args:
            device_type: Filter boxes by their device type (virtual, physical)
            labels: Filter boxes by their labels.
            page: Page number
            page_size: Page size
            status: Filter boxes by their current status (pending, running, stopped, error, terminated, all). Must be an array of statuses. Use 'all' to get boxes with any status.
            type: Filter boxes by their type (linux, android, all). Must be an array of types. Use 'all' to get boxes of any type.

        Returns:
            BoxListOperatorResponse: Response containing operator objects and pagination info.

        Examples:
            ```python
            # List all boxes
            boxes = sdk.list()

            # List with pagination
            boxes = sdk.list(page=1, page_size=10)
            ```
        """
        res = self.client.v1.boxes.list(
            device_type=device_type,
            labels=labels,
            page=page,
            page_size=page_size,
            status=status,
            type=type,
        )
        data = getattr(res, "data", [])
        operators = [self._data_to_operator(item) for item in data]
        return BoxListOperatorResponse(
            operators=operators,
            page=getattr(res, "page", None),
            page_size=getattr(res, "page_size", None),
            total=getattr(res, "total", None),
        )

    def get_info(self, box_id: str) -> BoxRetrieveResponse:
        """
        Retrieve detailed information for a specific box.

        Args:
            box_id (str): The ID of the box to retrieve.

        Returns:
            BoxRetrieveResponse: Detailed information about the box.

        Example:
            ```python
            box_info = sdk.get("975fed9f-bb28-4718-a2c5-e01f72864bd1")
            box_info = sdk.get_info(box_id="975fed9f-bb28-4718-a2c5-e01f72864bd1")
            ```
        """
        return self.client.v1.boxes.retrieve(box_id)

    def get(self, box_id: str) -> BoxOperator:
        """
        Retrieve a specific box and return its operator object.

        Args:
            box_id (str): The ID of the box to retrieve.

        Returns:
            BoxOperator: Operator object for the specified box.

        Example:
            ```python
            box = sdk.get("975fed9f-bb28-4718-a2c5-e01f72864bd1")
            box = sdk.get(box_id="975fed9f-bb28-4718-a2c5-e01f72864bd1")
            ```
        """
        res = self.client.v1.boxes.retrieve(box_id)
        return self._data_to_operator(res)

    def terminate(self, box_id: str, *, wait: Union[bool, NotGiven] = NOT_GIVEN) -> None:
        """
        Terminate a specific box.

        Args:
            box_id (str): The ID of the box to terminate.
            wait: Whether to wait for the box operation to complete (optional).

        Example:
            ```python
            sdk.terminate("975fed9f-bb28-4718-a2c5-e01f72864bd1")
            sdk.terminate(box_id="975fed9f-bb28-4718-a2c5-e01f72864bd1")
            ```
        """
        self.client.v1.boxes.terminate(box_id=box_id, wait=wait)

    def _data_to_operator(self, data: Union[AndroidBox, LinuxBox]) -> BoxOperator:
        """
        Convert box data to the corresponding operator object.

        Args:
            data (Union[AndroidBox, LinuxBox]): The box data to convert.

        Returns:
            BoxOperator: The corresponding operator object.

        Raises:
            ValueError: If the box type is invalid.
        """
        if is_android_box(data):
            data_dict = data.model_dump(by_alias=True)
            if (
                "config" in data_dict
                and isinstance(data_dict["config"], dict)
                and cast("dict[str, Any]", data_dict["config"]).get("labels") is None
            ):
                data_dict["config"]["labels"] = {}
            android_box: AndroidBox = AndroidBox(**data_dict)
            return AndroidBoxOperator(self.client, android_box)
        elif is_linux_box(data):
            data_dict = data.model_dump(by_alias=True)
            if (
                "config" in data_dict
                and isinstance(data_dict["config"], dict)
                and cast("dict[str, Any]", data_dict["config"]).get("labels") is None
            ):
                data_dict["config"]["labels"] = {}
            linux_box: LinuxBox = LinuxBox(**data_dict)
            return LinuxBoxOperator(self.client, linux_box)
        else:
            raise ValueError(f"Invalid box type: {data.type}")
