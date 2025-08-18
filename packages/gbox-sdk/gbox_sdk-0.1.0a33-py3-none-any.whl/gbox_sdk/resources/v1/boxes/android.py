# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Mapping, cast
from typing_extensions import Literal, overload

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven, FileTypes
from ...._utils import extract_files, required_args, maybe_transform, deepcopy_minimal, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    to_custom_raw_response_wrapper,
    async_to_streamed_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_raw_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v1.boxes import (
    android_open_params,
    android_install_params,
    android_restart_params,
    android_restore_params,
    android_list_pkg_params,
    android_uninstall_params,
    android_list_pkg_simple_params,
)
from ....types.v1.boxes.android_app import AndroidApp
from ....types.v1.boxes.android_get_response import AndroidGetResponse
from ....types.v1.boxes.android_install_response import AndroidInstallResponse
from ....types.v1.boxes.android_list_app_response import AndroidListAppResponse
from ....types.v1.boxes.android_list_pkg_response import AndroidListPkgResponse
from ....types.v1.boxes.android_list_activities_response import AndroidListActivitiesResponse
from ....types.v1.boxes.android_list_pkg_simple_response import AndroidListPkgSimpleResponse
from ....types.v1.boxes.android_get_connect_address_response import AndroidGetConnectAddressResponse

__all__ = ["AndroidResource", "AsyncAndroidResource"]


class AndroidResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AndroidResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AndroidResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AndroidResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return AndroidResourceWithStreamingResponse(self)

    def backup(
        self,
        package_name: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse:
        """
        Backup

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not package_name:
            raise ValueError(f"Expected a non-empty value for `package_name` but received {package_name!r}")
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return self._post(
            f"/boxes/{box_id}/android/packages/{package_name}/backup",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BinaryAPIResponse,
        )

    def backup_all(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse:
        """
        Backup all

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return self._post(
            f"/boxes/{box_id}/android/packages/backup-all",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BinaryAPIResponse,
        )

    def close(
        self,
        package_name: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Close app

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not package_name:
            raise ValueError(f"Expected a non-empty value for `package_name` but received {package_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/boxes/{box_id}/android/packages/{package_name}/close",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def close_all(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Close all apps

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/boxes/{box_id}/android/packages/close-all",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get(
        self,
        package_name: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidGetResponse:
        """
        Get pkg

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not package_name:
            raise ValueError(f"Expected a non-empty value for `package_name` but received {package_name!r}")
        return self._get(
            f"/boxes/{box_id}/android/packages/{package_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AndroidGetResponse,
        )

    def get_app(
        self,
        package_name: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidApp:
        """
        Get installed app info by package name

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not package_name:
            raise ValueError(f"Expected a non-empty value for `package_name` but received {package_name!r}")
        return self._get(
            f"/boxes/{box_id}/android/apps/{package_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AndroidApp,
        )

    def get_connect_address(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidGetConnectAddressResponse:
        """
        Get connect address

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._get(
            f"/boxes/{box_id}/android/connect-address",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AndroidGetConnectAddressResponse,
        )

    @overload
    def install(
        self,
        box_id: str,
        *,
        apk: FileTypes,
        open: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidInstallResponse:
        """
        Install app

        Args:
          apk: APK file or ZIP archive to install (max file size: 512MB).

              **Single APK mode:**

              - Upload a single APK file (e.g., app.apk)
              - System will automatically detect and install as single APK

              **Multi-APK mode (automatically detected):**

              - Upload a ZIP archive containing multiple APK files
              - System will automatically detect ZIP format and install all APKs inside
              - ZIP filename example: com.reddit.frontpage-gplay.zip
              - ZIP contents example:

              com.reddit.frontpage-gplay.zip └── com.reddit.frontpage-gplay/ (folder) ├──
              reddit-base.apk (base APK) ├── reddit-arm64.apk (architecture-specific) ├──
              reddit-en.apk (language pack) └── reddit-mdpi.apk (density-specific resources)

              This is commonly used for split APKs where different components are separated by
              architecture, language, or screen density.

          open: Whether to open the app after installation. Will find and launch the launcher
              activity of the installed app. If there are multiple launcher activities, only
              one will be opened. If the installed APK has no launcher activity, this
              parameter will have no effect.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def install(
        self,
        box_id: str,
        *,
        apk: str,
        open: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidInstallResponse:
        """
        Install app

        Args:
          apk: HTTP URL to download APK file or ZIP archive (max file size: 512MB).

              **Single APK mode (automatically detected):**

              - Provide URL to a single APK file
              - System will automatically detect .apk extension and install as single APK
              - Example: https://example.com/app.apk

              **Multi-APK mode (automatically detected):**

              - Provide URL to a ZIP archive containing multiple APK files
              - System will automatically detect .zip extension and install all APKs inside
              - ZIP filename example: com.reddit.frontpage-gplay.zip
              - ZIP contents example:

              com.reddit.frontpage-gplay.zip └── com.reddit.frontpage-gplay/ (folder) ├──
              reddit-base.apk (base APK) ├── reddit-arm64.apk (architecture-specific) ├──
              reddit-en.apk (language pack) └── reddit-mdpi.apk (density-specific resources)

              - Example URL: https://example.com/com.reddit.frontpage-gplay.zip

              This is commonly used for split APKs where different components are separated by
              architecture, language, or screen density.

          open: Whether to open the app after installation. Will find and launch the launcher
              activity of the installed app. If there are multiple launcher activities, only
              one will be opened. If the installed APK has no launcher activity, this
              parameter will have no effect.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["apk"])
    def install(
        self,
        box_id: str,
        *,
        apk: FileTypes | str,
        open: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidInstallResponse:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        body = deepcopy_minimal(
            {
                "apk": apk,
                "open": open,
            }
        )
        if isinstance(apk, str):
            return self._post(
                f"/boxes/{box_id}/android/packages",
                body=maybe_transform(body, android_install_params.AndroidInstallParams),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=AndroidInstallResponse,
            )
        else:
            files = extract_files(cast(Mapping[str, object], body), paths=[["apk"]])
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
            return self._post(
                f"/boxes/{box_id}/android/packages",
                body=maybe_transform(body, android_install_params.AndroidInstallParams),
                files=files,
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=AndroidInstallResponse,
            )

    def list_activities(
        self,
        package_name: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidListActivitiesResponse:
        """
        Get pkg activities

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not package_name:
            raise ValueError(f"Expected a non-empty value for `package_name` but received {package_name!r}")
        return self._get(
            f"/boxes/{box_id}/android/packages/{package_name}/activities",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AndroidListActivitiesResponse,
        )

    def list_app(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidListAppResponse:
        """
        List all installed apps on the launcher

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._get(
            f"/boxes/{box_id}/android/apps",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AndroidListAppResponse,
        )

    def list_pkg(
        self,
        box_id: str,
        *,
        pkg_type: List[Literal["system", "thirdParty"]] | NotGiven = NOT_GIVEN,
        running_filter: List[Literal["running", "notRunning"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidListPkgResponse:
        """Retrieve detailed information for all installed pkg.

        This endpoint provides
        comprehensive pkg details

        Args:
          pkg_type: system or thirdParty, default is thirdParty

          running_filter: Filter pkgs by running status: running (show only running pkgs), notRunning
              (show only non-running pkgs). Default is all

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._get(
            f"/boxes/{box_id}/android/packages",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "pkg_type": pkg_type,
                        "running_filter": running_filter,
                    },
                    android_list_pkg_params.AndroidListPkgParams,
                ),
            ),
            cast_to=AndroidListPkgResponse,
        )

    def list_pkg_simple(
        self,
        box_id: str,
        *,
        pkg_type: List[Literal["system", "thirdParty"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidListPkgSimpleResponse:
        """A faster endpoint to quickly retrieve basic pkg information.

        This API provides
        better performance for scenarios where you need to get essential pkg details
        quickly

        Args:
          pkg_type: system or thirdParty, default is thirdParty

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._get(
            f"/boxes/{box_id}/android/packages/simple",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"pkg_type": pkg_type}, android_list_pkg_simple_params.AndroidListPkgSimpleParams
                ),
            ),
            cast_to=AndroidListPkgSimpleResponse,
        )

    def open(
        self,
        package_name: str,
        *,
        box_id: str,
        activity_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Open app

        Args:
          activity_name: Activity name, default is the main activity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not package_name:
            raise ValueError(f"Expected a non-empty value for `package_name` but received {package_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/boxes/{box_id}/android/packages/{package_name}/open",
            body=maybe_transform({"activity_name": activity_name}, android_open_params.AndroidOpenParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def restart(
        self,
        package_name: str,
        *,
        box_id: str,
        activity_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Restart app

        Args:
          activity_name: Activity name, default is the main activity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not package_name:
            raise ValueError(f"Expected a non-empty value for `package_name` but received {package_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/boxes/{box_id}/android/packages/{package_name}/restart",
            body=maybe_transform({"activity_name": activity_name}, android_restart_params.AndroidRestartParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def restore(
        self,
        box_id: str,
        *,
        backup: FileTypes,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Restore

        Args:
          backup: Backup file to restore (max file size: 100MB)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/boxes/{box_id}/android/packages/restore",
            body=maybe_transform({"backup": backup}, android_restore_params.AndroidRestoreParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def uninstall(
        self,
        package_name: str,
        *,
        box_id: str,
        keep_data: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Uninstall app

        Args:
          keep_data: uninstalls the pkg while retaining the data/cache

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not package_name:
            raise ValueError(f"Expected a non-empty value for `package_name` but received {package_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/boxes/{box_id}/android/packages/{package_name}",
            body=maybe_transform({"keep_data": keep_data}, android_uninstall_params.AndroidUninstallParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncAndroidResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAndroidResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncAndroidResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAndroidResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return AsyncAndroidResourceWithStreamingResponse(self)

    async def backup(
        self,
        package_name: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse:
        """
        Backup

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not package_name:
            raise ValueError(f"Expected a non-empty value for `package_name` but received {package_name!r}")
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return await self._post(
            f"/boxes/{box_id}/android/packages/{package_name}/backup",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncBinaryAPIResponse,
        )

    async def backup_all(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse:
        """
        Backup all

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return await self._post(
            f"/boxes/{box_id}/android/packages/backup-all",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncBinaryAPIResponse,
        )

    async def close(
        self,
        package_name: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Close app

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not package_name:
            raise ValueError(f"Expected a non-empty value for `package_name` but received {package_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/boxes/{box_id}/android/packages/{package_name}/close",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def close_all(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Close all apps

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/boxes/{box_id}/android/packages/close-all",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get(
        self,
        package_name: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidGetResponse:
        """
        Get pkg

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not package_name:
            raise ValueError(f"Expected a non-empty value for `package_name` but received {package_name!r}")
        return await self._get(
            f"/boxes/{box_id}/android/packages/{package_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AndroidGetResponse,
        )

    async def get_app(
        self,
        package_name: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidApp:
        """
        Get installed app info by package name

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not package_name:
            raise ValueError(f"Expected a non-empty value for `package_name` but received {package_name!r}")
        return await self._get(
            f"/boxes/{box_id}/android/apps/{package_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AndroidApp,
        )

    async def get_connect_address(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidGetConnectAddressResponse:
        """
        Get connect address

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._get(
            f"/boxes/{box_id}/android/connect-address",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AndroidGetConnectAddressResponse,
        )

    @overload
    async def install(
        self,
        box_id: str,
        *,
        apk: FileTypes,
        open: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidInstallResponse:
        """
        Install app

        Args:
          apk: APK file or ZIP archive to install (max file size: 512MB).

              **Single APK mode:**

              - Upload a single APK file (e.g., app.apk)
              - System will automatically detect and install as single APK

              **Multi-APK mode (automatically detected):**

              - Upload a ZIP archive containing multiple APK files
              - System will automatically detect ZIP format and install all APKs inside
              - ZIP filename example: com.reddit.frontpage-gplay.zip
              - ZIP contents example:

              com.reddit.frontpage-gplay.zip └── com.reddit.frontpage-gplay/ (folder) ├──
              reddit-base.apk (base APK) ├── reddit-arm64.apk (architecture-specific) ├──
              reddit-en.apk (language pack) └── reddit-mdpi.apk (density-specific resources)

              This is commonly used for split APKs where different components are separated by
              architecture, language, or screen density.

          open: Whether to open the app after installation. Will find and launch the launcher
              activity of the installed app. If there are multiple launcher activities, only
              one will be opened. If the installed APK has no launcher activity, this
              parameter will have no effect.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def install(
        self,
        box_id: str,
        *,
        apk: str,
        open: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidInstallResponse:
        """
        Install app

        Args:
          apk: HTTP URL to download APK file or ZIP archive (max file size: 512MB).

              **Single APK mode (automatically detected):**

              - Provide URL to a single APK file
              - System will automatically detect .apk extension and install as single APK
              - Example: https://example.com/app.apk

              **Multi-APK mode (automatically detected):**

              - Provide URL to a ZIP archive containing multiple APK files
              - System will automatically detect .zip extension and install all APKs inside
              - ZIP filename example: com.reddit.frontpage-gplay.zip
              - ZIP contents example:

              com.reddit.frontpage-gplay.zip └── com.reddit.frontpage-gplay/ (folder) ├──
              reddit-base.apk (base APK) ├── reddit-arm64.apk (architecture-specific) ├──
              reddit-en.apk (language pack) └── reddit-mdpi.apk (density-specific resources)

              - Example URL: https://example.com/com.reddit.frontpage-gplay.zip

              This is commonly used for split APKs where different components are separated by
              architecture, language, or screen density.

          open: Whether to open the app after installation. Will find and launch the launcher
              activity of the installed app. If there are multiple launcher activities, only
              one will be opened. If the installed APK has no launcher activity, this
              parameter will have no effect.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["apk"])
    async def install(
        self,
        box_id: str,
        *,
        apk: FileTypes | str,
        open: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidInstallResponse:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        body = deepcopy_minimal(
            {
                "apk": apk,
                "open": open,
            }
        )
        if isinstance(apk, str):
            return await self._post(
                f"/boxes/{box_id}/android/packages",
                body=await async_maybe_transform(body, android_install_params.AndroidInstallParams),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=AndroidInstallResponse,
            )
        else:
            files = extract_files(cast(Mapping[str, object], body), paths=[["apk"]])
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
            return await self._post(
                f"/boxes/{box_id}/android/packages",
                body=await async_maybe_transform(body, android_install_params.AndroidInstallParams),
                files=files,
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=AndroidInstallResponse,
            )

    async def list_activities(
        self,
        package_name: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidListActivitiesResponse:
        """
        Get pkg activities

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not package_name:
            raise ValueError(f"Expected a non-empty value for `package_name` but received {package_name!r}")
        return await self._get(
            f"/boxes/{box_id}/android/packages/{package_name}/activities",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AndroidListActivitiesResponse,
        )

    async def list_app(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidListAppResponse:
        """
        List all installed apps on the launcher

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._get(
            f"/boxes/{box_id}/android/apps",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AndroidListAppResponse,
        )

    async def list_pkg(
        self,
        box_id: str,
        *,
        pkg_type: List[Literal["system", "thirdParty"]] | NotGiven = NOT_GIVEN,
        running_filter: List[Literal["running", "notRunning"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidListPkgResponse:
        """Retrieve detailed information for all installed pkg.

        This endpoint provides
        comprehensive pkg details

        Args:
          pkg_type: system or thirdParty, default is thirdParty

          running_filter: Filter pkgs by running status: running (show only running pkgs), notRunning
              (show only non-running pkgs). Default is all

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._get(
            f"/boxes/{box_id}/android/packages",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "pkg_type": pkg_type,
                        "running_filter": running_filter,
                    },
                    android_list_pkg_params.AndroidListPkgParams,
                ),
            ),
            cast_to=AndroidListPkgResponse,
        )

    async def list_pkg_simple(
        self,
        box_id: str,
        *,
        pkg_type: List[Literal["system", "thirdParty"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AndroidListPkgSimpleResponse:
        """A faster endpoint to quickly retrieve basic pkg information.

        This API provides
        better performance for scenarios where you need to get essential pkg details
        quickly

        Args:
          pkg_type: system or thirdParty, default is thirdParty

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._get(
            f"/boxes/{box_id}/android/packages/simple",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"pkg_type": pkg_type}, android_list_pkg_simple_params.AndroidListPkgSimpleParams
                ),
            ),
            cast_to=AndroidListPkgSimpleResponse,
        )

    async def open(
        self,
        package_name: str,
        *,
        box_id: str,
        activity_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Open app

        Args:
          activity_name: Activity name, default is the main activity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not package_name:
            raise ValueError(f"Expected a non-empty value for `package_name` but received {package_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/boxes/{box_id}/android/packages/{package_name}/open",
            body=await async_maybe_transform({"activity_name": activity_name}, android_open_params.AndroidOpenParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def restart(
        self,
        package_name: str,
        *,
        box_id: str,
        activity_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Restart app

        Args:
          activity_name: Activity name, default is the main activity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not package_name:
            raise ValueError(f"Expected a non-empty value for `package_name` but received {package_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/boxes/{box_id}/android/packages/{package_name}/restart",
            body=await async_maybe_transform(
                {"activity_name": activity_name}, android_restart_params.AndroidRestartParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def restore(
        self,
        box_id: str,
        *,
        backup: FileTypes,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Restore

        Args:
          backup: Backup file to restore (max file size: 100MB)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/boxes/{box_id}/android/packages/restore",
            body=await async_maybe_transform({"backup": backup}, android_restore_params.AndroidRestoreParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def uninstall(
        self,
        package_name: str,
        *,
        box_id: str,
        keep_data: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Uninstall app

        Args:
          keep_data: uninstalls the pkg while retaining the data/cache

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not package_name:
            raise ValueError(f"Expected a non-empty value for `package_name` but received {package_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/boxes/{box_id}/android/packages/{package_name}",
            body=await async_maybe_transform({"keep_data": keep_data}, android_uninstall_params.AndroidUninstallParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AndroidResourceWithRawResponse:
    def __init__(self, android: AndroidResource) -> None:
        self._android = android

        self.backup = to_custom_raw_response_wrapper(
            android.backup,
            BinaryAPIResponse,
        )
        self.backup_all = to_custom_raw_response_wrapper(
            android.backup_all,
            BinaryAPIResponse,
        )
        self.close = to_raw_response_wrapper(
            android.close,
        )
        self.close_all = to_raw_response_wrapper(
            android.close_all,
        )
        self.get = to_raw_response_wrapper(
            android.get,
        )
        self.get_app = to_raw_response_wrapper(
            android.get_app,
        )
        self.get_connect_address = to_raw_response_wrapper(
            android.get_connect_address,
        )
        self.install = to_raw_response_wrapper(
            android.install,
        )
        self.list_activities = to_raw_response_wrapper(
            android.list_activities,
        )
        self.list_app = to_raw_response_wrapper(
            android.list_app,
        )
        self.list_pkg = to_raw_response_wrapper(
            android.list_pkg,
        )
        self.list_pkg_simple = to_raw_response_wrapper(
            android.list_pkg_simple,
        )
        self.open = to_raw_response_wrapper(
            android.open,
        )
        self.restart = to_raw_response_wrapper(
            android.restart,
        )
        self.restore = to_raw_response_wrapper(
            android.restore,
        )
        self.uninstall = to_raw_response_wrapper(
            android.uninstall,
        )


class AsyncAndroidResourceWithRawResponse:
    def __init__(self, android: AsyncAndroidResource) -> None:
        self._android = android

        self.backup = async_to_custom_raw_response_wrapper(
            android.backup,
            AsyncBinaryAPIResponse,
        )
        self.backup_all = async_to_custom_raw_response_wrapper(
            android.backup_all,
            AsyncBinaryAPIResponse,
        )
        self.close = async_to_raw_response_wrapper(
            android.close,
        )
        self.close_all = async_to_raw_response_wrapper(
            android.close_all,
        )
        self.get = async_to_raw_response_wrapper(
            android.get,
        )
        self.get_app = async_to_raw_response_wrapper(
            android.get_app,
        )
        self.get_connect_address = async_to_raw_response_wrapper(
            android.get_connect_address,
        )
        self.install = async_to_raw_response_wrapper(
            android.install,
        )
        self.list_activities = async_to_raw_response_wrapper(
            android.list_activities,
        )
        self.list_app = async_to_raw_response_wrapper(
            android.list_app,
        )
        self.list_pkg = async_to_raw_response_wrapper(
            android.list_pkg,
        )
        self.list_pkg_simple = async_to_raw_response_wrapper(
            android.list_pkg_simple,
        )
        self.open = async_to_raw_response_wrapper(
            android.open,
        )
        self.restart = async_to_raw_response_wrapper(
            android.restart,
        )
        self.restore = async_to_raw_response_wrapper(
            android.restore,
        )
        self.uninstall = async_to_raw_response_wrapper(
            android.uninstall,
        )


class AndroidResourceWithStreamingResponse:
    def __init__(self, android: AndroidResource) -> None:
        self._android = android

        self.backup = to_custom_streamed_response_wrapper(
            android.backup,
            StreamedBinaryAPIResponse,
        )
        self.backup_all = to_custom_streamed_response_wrapper(
            android.backup_all,
            StreamedBinaryAPIResponse,
        )
        self.close = to_streamed_response_wrapper(
            android.close,
        )
        self.close_all = to_streamed_response_wrapper(
            android.close_all,
        )
        self.get = to_streamed_response_wrapper(
            android.get,
        )
        self.get_app = to_streamed_response_wrapper(
            android.get_app,
        )
        self.get_connect_address = to_streamed_response_wrapper(
            android.get_connect_address,
        )
        self.install = to_streamed_response_wrapper(
            android.install,
        )
        self.list_activities = to_streamed_response_wrapper(
            android.list_activities,
        )
        self.list_app = to_streamed_response_wrapper(
            android.list_app,
        )
        self.list_pkg = to_streamed_response_wrapper(
            android.list_pkg,
        )
        self.list_pkg_simple = to_streamed_response_wrapper(
            android.list_pkg_simple,
        )
        self.open = to_streamed_response_wrapper(
            android.open,
        )
        self.restart = to_streamed_response_wrapper(
            android.restart,
        )
        self.restore = to_streamed_response_wrapper(
            android.restore,
        )
        self.uninstall = to_streamed_response_wrapper(
            android.uninstall,
        )


class AsyncAndroidResourceWithStreamingResponse:
    def __init__(self, android: AsyncAndroidResource) -> None:
        self._android = android

        self.backup = async_to_custom_streamed_response_wrapper(
            android.backup,
            AsyncStreamedBinaryAPIResponse,
        )
        self.backup_all = async_to_custom_streamed_response_wrapper(
            android.backup_all,
            AsyncStreamedBinaryAPIResponse,
        )
        self.close = async_to_streamed_response_wrapper(
            android.close,
        )
        self.close_all = async_to_streamed_response_wrapper(
            android.close_all,
        )
        self.get = async_to_streamed_response_wrapper(
            android.get,
        )
        self.get_app = async_to_streamed_response_wrapper(
            android.get_app,
        )
        self.get_connect_address = async_to_streamed_response_wrapper(
            android.get_connect_address,
        )
        self.install = async_to_streamed_response_wrapper(
            android.install,
        )
        self.list_activities = async_to_streamed_response_wrapper(
            android.list_activities,
        )
        self.list_app = async_to_streamed_response_wrapper(
            android.list_app,
        )
        self.list_pkg = async_to_streamed_response_wrapper(
            android.list_pkg,
        )
        self.list_pkg_simple = async_to_streamed_response_wrapper(
            android.list_pkg_simple,
        )
        self.open = async_to_streamed_response_wrapper(
            android.open,
        )
        self.restart = async_to_streamed_response_wrapper(
            android.restart,
        )
        self.restore = async_to_streamed_response_wrapper(
            android.restore,
        )
        self.uninstall = async_to_streamed_response_wrapper(
            android.uninstall,
        )
