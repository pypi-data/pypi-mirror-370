import os
from typing import List
from builtins import open as _open
from typing_extensions import Union, Literal

from gbox_sdk._types import NOT_GIVEN, NotGiven, FileTypes
from gbox_sdk._client import GboxClient
from gbox_sdk._response import BinaryAPIResponse
from gbox_sdk.types.v1.android_box import AndroidBox
from gbox_sdk.wrapper.box.android.types import ListAndroidPkg
from gbox_sdk.wrapper.box.android.pkg_operator import AndroidPkgOperator
from gbox_sdk.types.v1.boxes.android_get_response import AndroidGetResponse
from gbox_sdk.types.v1.boxes.android_install_response import AndroidInstallResponse
from gbox_sdk.types.v1.boxes.android_list_pkg_response import AndroidListPkgResponse
from gbox_sdk.types.v1.boxes.android_list_pkg_simple_response import AndroidListPkgSimpleResponse


class AndroidPkgManager:
    """
    Manager class for handling Android package operations within a box.

    Provides methods to install, uninstall, list, retrieve, close, and backup Android packages.

    Attributes:
        client (GboxClient): The API client used for communication.
        box (AndroidBox): The Android box data object.
    """

    def __init__(self, client: GboxClient, box: AndroidBox):
        """
        Initialize an AndroidPkgManager instance.

        Args:
            client (GboxClient): The API client used for communication.
            box (AndroidBox): The Android box data object.
        """
        self.client = client
        self.box = box

    def install(
        self,
        *,
        apk: Union[str, FileTypes],
        open: Union[bool, NotGiven] = NOT_GIVEN,
    ) -> AndroidInstallResponse:
        """
        Install an Android package on the box.

        Args:
            apk: APK file or ZIP archive to install (max file size: 512MB).

              **Single APK mode (installMultiple: false):**

              - Upload a single APK file (e.g., app.apk)

              **Install-Multiple mode (installMultiple: true):**

              - Upload a ZIP archive containing multiple APK files
              - ZIP filename example: com.reddit.frontpage-gplay.zip
              - ZIP contents example:

              com.reddit.frontpage-gplay.zip
              └── com.reddit.frontpage-gplay/ (folder)
                ├── reddit-base.apk (base APK)
                ├── reddit-arm64.apk (architecture-specific)
                ├── reddit-en.apk (language pack)
                └── reddit-mdpi.apk (density-specific resources)

              This is commonly used for split APKs where different components are separated by
              architecture, language, or screen density.

            open: Whether to open the app after installation. Will find and launch the launcher
                activity of the installed app. If there are multiple launcher activities, only
                one will be opened. If the installed APK has no launcher activity, this
                parameter will have no effect.

        Returns:
            AndroidInstallResponse: The response of the install operation.

        Examples:
            >>> box.pkg.install(apk="/path/to/app.apk")
            >>> box.pkg.install(apk="https://example.com/app.apk")
        """
        if isinstance(apk, str) and not apk.startswith("http"):
            if not os.path.exists(apk):
                raise FileNotFoundError(f"File {apk} does not exist")
            with _open(apk, "rb") as apk_file:
                return self.client.v1.boxes.android.install(box_id=self.box.id, apk=apk_file, open=open)
        elif isinstance(apk, str) and apk.startswith("http"):
            return self.client.v1.boxes.android.install(box_id=self.box.id, apk=apk, open=open)

        return self.client.v1.boxes.android.install(box_id=self.box.id, apk=apk, open=open)

    def uninstall(self, package_name: str, *, keep_data: Union[bool, NotGiven] = NOT_GIVEN) -> None:
        """
        Uninstall an Android package from the box.

        Args:
            package_name: The package name of the app to uninstall.

            keep_data: uninstalls the pkg while retaining the data/cache

        Examples:
            >>> box.pkg.uninstall("com.example.app")
            >>> box.pkg.uninstall(package_name="com.example.app", keep_data=True)
        """
        return self.client.v1.boxes.android.uninstall(package_name, box_id=self.box.id, keep_data=keep_data)

    def list(
        self,
        *,
        pkg_type: Union[List[Literal["system", "thirdParty"]], NotGiven] = NOT_GIVEN,
        running_filter: Union[List[Literal["running", "notRunning"]], NotGiven] = NOT_GIVEN,
    ) -> ListAndroidPkg:
        """
        List all installed Android packages as operator objects.

        Args:
          pkg_type: system or thirdParty, default is thirdParty

          running_filter: Filter pkgs by running status: running (show only running pkgs), notRunning
              (show only non-running pkgs). Default is all

        Returns:
            ListAndroidPkg: Response containing package operator instances.

        Examples:
            >>> box.pkg.list()
            >>> box.pkg.list(pkg_type=["system", "thirdParty"], running_filter=["running", "notRunning"])
        """
        res = self.client.v1.boxes.android.list_pkg(
            box_id=self.box.id, pkg_type=pkg_type, running_filter=running_filter
        )
        operators: List[AndroidPkgOperator] = []
        for pkg in res.data:
            # Create AndroidGetResponse using camelCase field names
            android_get_response = AndroidGetResponse(
                apkPath=pkg.apk_path,
                isRunning=pkg.is_running,
                name=pkg.name,
                packageName=pkg.package_name,
                pkgType=pkg.pkg_type,
                version=pkg.version,
            )
            operators.append(AndroidPkgOperator(self.client, self.box, android_get_response))
        return ListAndroidPkg(operators=operators)

    def list_info(
        self,
        *,
        pkg_type: Union[List[Literal["system", "thirdParty"]], NotGiven] = NOT_GIVEN,
        running_filter: Union[List[Literal["running", "notRunning"]], NotGiven] = NOT_GIVEN,
    ) -> AndroidListPkgResponse:
        """
        Get detailed information of all installed Android packages.

        Args:
          pkg_type: system or thirdParty, default is thirdParty

          running_filter: Filter pkgs by running status: running (show only running pkgs), notRunning
              (show only non-running pkgs). Default is all

        Returns:
            AndroidListPkgResponse: Response containing package information.

        Examples:
            >>> box.pkg.list_info()
            >>> box.pkg.list_info(pkg_type=["system", "thirdParty"], running_filter=["running", "notRunning"])
        """
        return self.client.v1.boxes.android.list_pkg(
            box_id=self.box.id, pkg_type=pkg_type, running_filter=running_filter
        )

    def get(self, package_name: str) -> AndroidPkgOperator:
        """
        Get an operator for a specific installed package.

        Args:
            package_name (str): The package name of the app.

        Returns:
            AndroidPkgOperator: Operator for the specified package.

        Examples:
            >>> box.pkg.get("com.example.app")
        """
        res = self.client.v1.boxes.android.get(package_name, box_id=self.box.id)
        return AndroidPkgOperator(self.client, self.box, res)

    def get_info(self, package_name: str) -> AndroidGetResponse:
        """
        Get detailed information for a specific installed package.

        Args:
            package_name (str): The package name of the app.

        Returns:
            AndroidGetResponse: Package information response.

        Examples:
            >>> box.pkg.get_info("com.example.app")
        """
        res = self.client.v1.boxes.android.get(package_name, box_id=self.box.id)
        return res

    def close_all(self) -> None:
        """
        Close all running Android packages on the box.

        Examples:
            >>> box.pkg.close_all()
        """
        return self.client.v1.boxes.android.close_all(box_id=self.box.id)

    def backup_all(self) -> BinaryAPIResponse:
        """
        Backup all installed Android packages on the box.

        Returns:
            BinaryAPIResponse: The backup response containing binary data.

        Examples:
            >>> box.pkg.backup_all()
        """
        return self.client.v1.boxes.android.backup_all(box_id=self.box.id)

    def list_simple_info(
        self,
        *,
        pkg_type: Union[List[Literal["system", "thirdParty"]], NotGiven] = NOT_GIVEN,
    ) -> AndroidListPkgSimpleResponse:
        """
        List all installed Android packages with simple information.

        Args:
          pkg_type: system or thirdParty, default is thirdParty

        Returns:
            ListAndroidPkgResponse: Response containing package information.

        Examples:
            >>> box.pkg.list_simple_info()
        """
        return self.client.v1.boxes.android.list_pkg_simple(box_id=self.box.id, pkg_type=pkg_type)
