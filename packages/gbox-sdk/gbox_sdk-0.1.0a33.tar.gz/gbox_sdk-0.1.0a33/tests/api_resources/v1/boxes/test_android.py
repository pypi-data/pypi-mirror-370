# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

from gbox_sdk import GboxClient, AsyncGboxClient
from tests.utils import assert_matches_type
from gbox_sdk._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
)
from gbox_sdk.types.v1.boxes import (
    AndroidApp,
    AndroidGetResponse,
    AndroidInstallResponse,
    AndroidListAppResponse,
    AndroidListPkgResponse,
    AndroidListPkgSimpleResponse,
    AndroidListActivitiesResponse,
    AndroidGetConnectAddressResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAndroid:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_backup(self, client: GboxClient, respx_mock: MockRouter) -> None:
        respx_mock.post("/boxes/c9bdc193-b54b-4ddb-a035-5ac0c598d32d/android/packages/com.example.myapp/backup").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        android = client.v1.boxes.android.backup(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert android.is_closed
        assert android.json() == {"foo": "bar"}
        assert cast(Any, android.is_closed) is True
        assert isinstance(android, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_backup(self, client: GboxClient, respx_mock: MockRouter) -> None:
        respx_mock.post("/boxes/c9bdc193-b54b-4ddb-a035-5ac0c598d32d/android/packages/com.example.myapp/backup").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        android = client.v1.boxes.android.with_raw_response.backup(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert android.is_closed is True
        assert android.http_request.headers.get("X-Stainless-Lang") == "python"
        assert android.json() == {"foo": "bar"}
        assert isinstance(android, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_backup(self, client: GboxClient, respx_mock: MockRouter) -> None:
        respx_mock.post("/boxes/c9bdc193-b54b-4ddb-a035-5ac0c598d32d/android/packages/com.example.myapp/backup").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        with client.v1.boxes.android.with_streaming_response.backup(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as android:
            assert not android.is_closed
            assert android.http_request.headers.get("X-Stainless-Lang") == "python"

            assert android.json() == {"foo": "bar"}
            assert cast(Any, android.is_closed) is True
            assert isinstance(android, StreamedBinaryAPIResponse)

        assert cast(Any, android.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_backup(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.android.with_raw_response.backup(
                package_name="com.example.myapp",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `package_name` but received ''"):
            client.v1.boxes.android.with_raw_response.backup(
                package_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_backup_all(self, client: GboxClient, respx_mock: MockRouter) -> None:
        respx_mock.post("/boxes/c9bdc193-b54b-4ddb-a035-5ac0c598d32d/android/packages/backup-all").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        android = client.v1.boxes.android.backup_all(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert android.is_closed
        assert android.json() == {"foo": "bar"}
        assert cast(Any, android.is_closed) is True
        assert isinstance(android, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_backup_all(self, client: GboxClient, respx_mock: MockRouter) -> None:
        respx_mock.post("/boxes/c9bdc193-b54b-4ddb-a035-5ac0c598d32d/android/packages/backup-all").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        android = client.v1.boxes.android.with_raw_response.backup_all(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert android.is_closed is True
        assert android.http_request.headers.get("X-Stainless-Lang") == "python"
        assert android.json() == {"foo": "bar"}
        assert isinstance(android, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_backup_all(self, client: GboxClient, respx_mock: MockRouter) -> None:
        respx_mock.post("/boxes/c9bdc193-b54b-4ddb-a035-5ac0c598d32d/android/packages/backup-all").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        with client.v1.boxes.android.with_streaming_response.backup_all(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as android:
            assert not android.is_closed
            assert android.http_request.headers.get("X-Stainless-Lang") == "python"

            assert android.json() == {"foo": "bar"}
            assert cast(Any, android.is_closed) is True
            assert isinstance(android, StreamedBinaryAPIResponse)

        assert cast(Any, android.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_backup_all(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.android.with_raw_response.backup_all(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_close(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.close(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_close(self, client: GboxClient) -> None:
        response = client.v1.boxes.android.with_raw_response.close(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = response.parse()
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_close(self, client: GboxClient) -> None:
        with client.v1.boxes.android.with_streaming_response.close(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = response.parse()
            assert android is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_close(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.android.with_raw_response.close(
                package_name="com.example.myapp",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `package_name` but received ''"):
            client.v1.boxes.android.with_raw_response.close(
                package_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_close_all(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.close_all(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_close_all(self, client: GboxClient) -> None:
        response = client.v1.boxes.android.with_raw_response.close_all(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = response.parse()
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_close_all(self, client: GboxClient) -> None:
        with client.v1.boxes.android.with_streaming_response.close_all(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = response.parse()
            assert android is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_close_all(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.android.with_raw_response.close_all(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.get(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(AndroidGetResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: GboxClient) -> None:
        response = client.v1.boxes.android.with_raw_response.get(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = response.parse()
        assert_matches_type(AndroidGetResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: GboxClient) -> None:
        with client.v1.boxes.android.with_streaming_response.get(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = response.parse()
            assert_matches_type(AndroidGetResponse, android, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.android.with_raw_response.get(
                package_name="com.example.myapp",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `package_name` but received ''"):
            client.v1.boxes.android.with_raw_response.get(
                package_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_app(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.get_app(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(AndroidApp, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_app(self, client: GboxClient) -> None:
        response = client.v1.boxes.android.with_raw_response.get_app(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = response.parse()
        assert_matches_type(AndroidApp, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_app(self, client: GboxClient) -> None:
        with client.v1.boxes.android.with_streaming_response.get_app(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = response.parse()
            assert_matches_type(AndroidApp, android, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_app(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.android.with_raw_response.get_app(
                package_name="com.example.myapp",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `package_name` but received ''"):
            client.v1.boxes.android.with_raw_response.get_app(
                package_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_connect_address(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.get_connect_address(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(AndroidGetConnectAddressResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_connect_address(self, client: GboxClient) -> None:
        response = client.v1.boxes.android.with_raw_response.get_connect_address(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = response.parse()
        assert_matches_type(AndroidGetConnectAddressResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_connect_address(self, client: GboxClient) -> None:
        with client.v1.boxes.android.with_streaming_response.get_connect_address(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = response.parse()
            assert_matches_type(AndroidGetConnectAddressResponse, android, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_connect_address(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.android.with_raw_response.get_connect_address(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_install_overload_1(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.install(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            apk=b"raw file contents",
        )
        assert_matches_type(AndroidInstallResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_install_with_all_params_overload_1(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.install(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            apk=b"raw file contents",
            open=False,
        )
        assert_matches_type(AndroidInstallResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_install_overload_1(self, client: GboxClient) -> None:
        response = client.v1.boxes.android.with_raw_response.install(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            apk=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = response.parse()
        assert_matches_type(AndroidInstallResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_install_overload_1(self, client: GboxClient) -> None:
        with client.v1.boxes.android.with_streaming_response.install(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            apk=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = response.parse()
            assert_matches_type(AndroidInstallResponse, android, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_install_overload_1(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.android.with_raw_response.install(
                box_id="",
                apk=b"raw file contents",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_install_overload_2(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.install(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            apk="https://example.com/app.apk",
        )
        assert_matches_type(AndroidInstallResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_install_with_all_params_overload_2(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.install(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            apk="https://example.com/app.apk",
            open=False,
        )
        assert_matches_type(AndroidInstallResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_install_overload_2(self, client: GboxClient) -> None:
        response = client.v1.boxes.android.with_raw_response.install(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            apk="https://example.com/app.apk",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = response.parse()
        assert_matches_type(AndroidInstallResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_install_overload_2(self, client: GboxClient) -> None:
        with client.v1.boxes.android.with_streaming_response.install(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            apk="https://example.com/app.apk",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = response.parse()
            assert_matches_type(AndroidInstallResponse, android, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_install_overload_2(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.android.with_raw_response.install(
                box_id="",
                apk="https://example.com/app.apk",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_activities(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.list_activities(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(AndroidListActivitiesResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_activities(self, client: GboxClient) -> None:
        response = client.v1.boxes.android.with_raw_response.list_activities(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = response.parse()
        assert_matches_type(AndroidListActivitiesResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_activities(self, client: GboxClient) -> None:
        with client.v1.boxes.android.with_streaming_response.list_activities(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = response.parse()
            assert_matches_type(AndroidListActivitiesResponse, android, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_activities(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.android.with_raw_response.list_activities(
                package_name="com.example.myapp",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `package_name` but received ''"):
            client.v1.boxes.android.with_raw_response.list_activities(
                package_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_app(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.list_app(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(AndroidListAppResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_app(self, client: GboxClient) -> None:
        response = client.v1.boxes.android.with_raw_response.list_app(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = response.parse()
        assert_matches_type(AndroidListAppResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_app(self, client: GboxClient) -> None:
        with client.v1.boxes.android.with_streaming_response.list_app(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = response.parse()
            assert_matches_type(AndroidListAppResponse, android, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_app(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.android.with_raw_response.list_app(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_pkg(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.list_pkg(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(AndroidListPkgResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_pkg_with_all_params(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.list_pkg(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            pkg_type=["thirdParty"],
            running_filter=["running", "notRunning"],
        )
        assert_matches_type(AndroidListPkgResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_pkg(self, client: GboxClient) -> None:
        response = client.v1.boxes.android.with_raw_response.list_pkg(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = response.parse()
        assert_matches_type(AndroidListPkgResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_pkg(self, client: GboxClient) -> None:
        with client.v1.boxes.android.with_streaming_response.list_pkg(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = response.parse()
            assert_matches_type(AndroidListPkgResponse, android, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_pkg(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.android.with_raw_response.list_pkg(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_pkg_simple(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.list_pkg_simple(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(AndroidListPkgSimpleResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_pkg_simple_with_all_params(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.list_pkg_simple(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            pkg_type=["thirdParty"],
        )
        assert_matches_type(AndroidListPkgSimpleResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_pkg_simple(self, client: GboxClient) -> None:
        response = client.v1.boxes.android.with_raw_response.list_pkg_simple(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = response.parse()
        assert_matches_type(AndroidListPkgSimpleResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_pkg_simple(self, client: GboxClient) -> None:
        with client.v1.boxes.android.with_streaming_response.list_pkg_simple(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = response.parse()
            assert_matches_type(AndroidListPkgSimpleResponse, android, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_pkg_simple(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.android.with_raw_response.list_pkg_simple(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_open(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.open(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_open_with_all_params(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.open(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            activity_name="com.android.settings.Settings",
        )
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_open(self, client: GboxClient) -> None:
        response = client.v1.boxes.android.with_raw_response.open(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = response.parse()
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_open(self, client: GboxClient) -> None:
        with client.v1.boxes.android.with_streaming_response.open(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = response.parse()
            assert android is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_open(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.android.with_raw_response.open(
                package_name="com.example.myapp",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `package_name` but received ''"):
            client.v1.boxes.android.with_raw_response.open(
                package_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_restart(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.restart(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_restart_with_all_params(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.restart(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            activity_name="com.android.settings.Settings",
        )
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_restart(self, client: GboxClient) -> None:
        response = client.v1.boxes.android.with_raw_response.restart(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = response.parse()
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_restart(self, client: GboxClient) -> None:
        with client.v1.boxes.android.with_streaming_response.restart(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = response.parse()
            assert android is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_restart(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.android.with_raw_response.restart(
                package_name="com.example.myapp",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `package_name` but received ''"):
            client.v1.boxes.android.with_raw_response.restart(
                package_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_restore(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.restore(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            backup=b"raw file contents",
        )
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_restore(self, client: GboxClient) -> None:
        response = client.v1.boxes.android.with_raw_response.restore(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            backup=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = response.parse()
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_restore(self, client: GboxClient) -> None:
        with client.v1.boxes.android.with_streaming_response.restore(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            backup=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = response.parse()
            assert android is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_restore(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.android.with_raw_response.restore(
                box_id="",
                backup=b"raw file contents",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_uninstall(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.uninstall(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_uninstall_with_all_params(self, client: GboxClient) -> None:
        android = client.v1.boxes.android.uninstall(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            keep_data=True,
        )
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_uninstall(self, client: GboxClient) -> None:
        response = client.v1.boxes.android.with_raw_response.uninstall(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = response.parse()
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_uninstall(self, client: GboxClient) -> None:
        with client.v1.boxes.android.with_streaming_response.uninstall(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = response.parse()
            assert android is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_uninstall(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.android.with_raw_response.uninstall(
                package_name="com.example.myapp",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `package_name` but received ''"):
            client.v1.boxes.android.with_raw_response.uninstall(
                package_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )


class TestAsyncAndroid:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_backup(self, async_client: AsyncGboxClient, respx_mock: MockRouter) -> None:
        respx_mock.post("/boxes/c9bdc193-b54b-4ddb-a035-5ac0c598d32d/android/packages/com.example.myapp/backup").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        android = await async_client.v1.boxes.android.backup(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert android.is_closed
        assert await android.json() == {"foo": "bar"}
        assert cast(Any, android.is_closed) is True
        assert isinstance(android, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_backup(self, async_client: AsyncGboxClient, respx_mock: MockRouter) -> None:
        respx_mock.post("/boxes/c9bdc193-b54b-4ddb-a035-5ac0c598d32d/android/packages/com.example.myapp/backup").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        android = await async_client.v1.boxes.android.with_raw_response.backup(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert android.is_closed is True
        assert android.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await android.json() == {"foo": "bar"}
        assert isinstance(android, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_backup(self, async_client: AsyncGboxClient, respx_mock: MockRouter) -> None:
        respx_mock.post("/boxes/c9bdc193-b54b-4ddb-a035-5ac0c598d32d/android/packages/com.example.myapp/backup").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        async with async_client.v1.boxes.android.with_streaming_response.backup(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as android:
            assert not android.is_closed
            assert android.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await android.json() == {"foo": "bar"}
            assert cast(Any, android.is_closed) is True
            assert isinstance(android, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, android.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_backup(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.backup(
                package_name="com.example.myapp",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `package_name` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.backup(
                package_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_backup_all(self, async_client: AsyncGboxClient, respx_mock: MockRouter) -> None:
        respx_mock.post("/boxes/c9bdc193-b54b-4ddb-a035-5ac0c598d32d/android/packages/backup-all").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        android = await async_client.v1.boxes.android.backup_all(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert android.is_closed
        assert await android.json() == {"foo": "bar"}
        assert cast(Any, android.is_closed) is True
        assert isinstance(android, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_backup_all(self, async_client: AsyncGboxClient, respx_mock: MockRouter) -> None:
        respx_mock.post("/boxes/c9bdc193-b54b-4ddb-a035-5ac0c598d32d/android/packages/backup-all").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        android = await async_client.v1.boxes.android.with_raw_response.backup_all(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert android.is_closed is True
        assert android.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await android.json() == {"foo": "bar"}
        assert isinstance(android, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_backup_all(self, async_client: AsyncGboxClient, respx_mock: MockRouter) -> None:
        respx_mock.post("/boxes/c9bdc193-b54b-4ddb-a035-5ac0c598d32d/android/packages/backup-all").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        async with async_client.v1.boxes.android.with_streaming_response.backup_all(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as android:
            assert not android.is_closed
            assert android.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await android.json() == {"foo": "bar"}
            assert cast(Any, android.is_closed) is True
            assert isinstance(android, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, android.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_backup_all(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.backup_all(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_close(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.close(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_close(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.android.with_raw_response.close(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = await response.parse()
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_close(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.android.with_streaming_response.close(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = await response.parse()
            assert android is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_close(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.close(
                package_name="com.example.myapp",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `package_name` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.close(
                package_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_close_all(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.close_all(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_close_all(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.android.with_raw_response.close_all(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = await response.parse()
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_close_all(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.android.with_streaming_response.close_all(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = await response.parse()
            assert android is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_close_all(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.close_all(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.get(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(AndroidGetResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.android.with_raw_response.get(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = await response.parse()
        assert_matches_type(AndroidGetResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.android.with_streaming_response.get(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = await response.parse()
            assert_matches_type(AndroidGetResponse, android, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.get(
                package_name="com.example.myapp",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `package_name` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.get(
                package_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_app(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.get_app(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(AndroidApp, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_app(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.android.with_raw_response.get_app(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = await response.parse()
        assert_matches_type(AndroidApp, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_app(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.android.with_streaming_response.get_app(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = await response.parse()
            assert_matches_type(AndroidApp, android, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_app(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.get_app(
                package_name="com.example.myapp",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `package_name` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.get_app(
                package_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_connect_address(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.get_connect_address(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(AndroidGetConnectAddressResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_connect_address(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.android.with_raw_response.get_connect_address(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = await response.parse()
        assert_matches_type(AndroidGetConnectAddressResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_connect_address(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.android.with_streaming_response.get_connect_address(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = await response.parse()
            assert_matches_type(AndroidGetConnectAddressResponse, android, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_connect_address(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.get_connect_address(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_install_overload_1(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.install(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            apk=b"raw file contents",
        )
        assert_matches_type(AndroidInstallResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_install_with_all_params_overload_1(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.install(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            apk=b"raw file contents",
            open=False,
        )
        assert_matches_type(AndroidInstallResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_install_overload_1(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.android.with_raw_response.install(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            apk=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = await response.parse()
        assert_matches_type(AndroidInstallResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_install_overload_1(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.android.with_streaming_response.install(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            apk=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = await response.parse()
            assert_matches_type(AndroidInstallResponse, android, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_install_overload_1(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.install(
                box_id="",
                apk=b"raw file contents",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_install_overload_2(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.install(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            apk="https://example.com/app.apk",
        )
        assert_matches_type(AndroidInstallResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_install_with_all_params_overload_2(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.install(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            apk="https://example.com/app.apk",
            open=False,
        )
        assert_matches_type(AndroidInstallResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_install_overload_2(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.android.with_raw_response.install(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            apk="https://example.com/app.apk",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = await response.parse()
        assert_matches_type(AndroidInstallResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_install_overload_2(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.android.with_streaming_response.install(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            apk="https://example.com/app.apk",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = await response.parse()
            assert_matches_type(AndroidInstallResponse, android, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_install_overload_2(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.install(
                box_id="",
                apk="https://example.com/app.apk",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_activities(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.list_activities(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(AndroidListActivitiesResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_activities(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.android.with_raw_response.list_activities(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = await response.parse()
        assert_matches_type(AndroidListActivitiesResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_activities(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.android.with_streaming_response.list_activities(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = await response.parse()
            assert_matches_type(AndroidListActivitiesResponse, android, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_activities(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.list_activities(
                package_name="com.example.myapp",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `package_name` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.list_activities(
                package_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_app(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.list_app(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(AndroidListAppResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_app(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.android.with_raw_response.list_app(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = await response.parse()
        assert_matches_type(AndroidListAppResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_app(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.android.with_streaming_response.list_app(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = await response.parse()
            assert_matches_type(AndroidListAppResponse, android, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_app(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.list_app(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_pkg(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.list_pkg(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(AndroidListPkgResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_pkg_with_all_params(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.list_pkg(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            pkg_type=["thirdParty"],
            running_filter=["running", "notRunning"],
        )
        assert_matches_type(AndroidListPkgResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_pkg(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.android.with_raw_response.list_pkg(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = await response.parse()
        assert_matches_type(AndroidListPkgResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_pkg(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.android.with_streaming_response.list_pkg(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = await response.parse()
            assert_matches_type(AndroidListPkgResponse, android, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_pkg(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.list_pkg(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_pkg_simple(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.list_pkg_simple(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(AndroidListPkgSimpleResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_pkg_simple_with_all_params(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.list_pkg_simple(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            pkg_type=["thirdParty"],
        )
        assert_matches_type(AndroidListPkgSimpleResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_pkg_simple(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.android.with_raw_response.list_pkg_simple(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = await response.parse()
        assert_matches_type(AndroidListPkgSimpleResponse, android, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_pkg_simple(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.android.with_streaming_response.list_pkg_simple(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = await response.parse()
            assert_matches_type(AndroidListPkgSimpleResponse, android, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_pkg_simple(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.list_pkg_simple(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_open(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.open(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_open_with_all_params(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.open(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            activity_name="com.android.settings.Settings",
        )
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_open(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.android.with_raw_response.open(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = await response.parse()
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_open(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.android.with_streaming_response.open(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = await response.parse()
            assert android is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_open(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.open(
                package_name="com.example.myapp",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `package_name` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.open(
                package_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_restart(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.restart(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_restart_with_all_params(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.restart(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            activity_name="com.android.settings.Settings",
        )
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_restart(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.android.with_raw_response.restart(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = await response.parse()
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_restart(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.android.with_streaming_response.restart(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = await response.parse()
            assert android is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_restart(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.restart(
                package_name="com.example.myapp",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `package_name` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.restart(
                package_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_restore(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.restore(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            backup=b"raw file contents",
        )
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_restore(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.android.with_raw_response.restore(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            backup=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = await response.parse()
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_restore(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.android.with_streaming_response.restore(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            backup=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = await response.parse()
            assert android is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_restore(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.restore(
                box_id="",
                backup=b"raw file contents",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_uninstall(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.uninstall(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_uninstall_with_all_params(self, async_client: AsyncGboxClient) -> None:
        android = await async_client.v1.boxes.android.uninstall(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            keep_data=True,
        )
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_uninstall(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.android.with_raw_response.uninstall(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        android = await response.parse()
        assert android is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_uninstall(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.android.with_streaming_response.uninstall(
            package_name="com.example.myapp",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            android = await response.parse()
            assert android is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_uninstall(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.uninstall(
                package_name="com.example.myapp",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `package_name` but received ''"):
            await async_client.v1.boxes.android.with_raw_response.uninstall(
                package_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )
