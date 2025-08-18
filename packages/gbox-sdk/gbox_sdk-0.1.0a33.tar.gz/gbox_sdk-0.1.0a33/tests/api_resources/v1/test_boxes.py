# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from gbox_sdk import GboxClient, AsyncGboxClient
from tests.utils import assert_matches_type
from gbox_sdk.types.v1 import (
    LinuxBox,
    AndroidBox,
    BoxListResponse,
    BoxStopResponse,
    BoxStartResponse,
    BoxDisplayResponse,
    BoxRunCodeResponse,
    BoxRetrieveResponse,
    BoxLiveViewURLResponse,
    BoxWebsocketURLResponse,
    BoxWebTerminalURLResponse,
    BoxExecuteCommandsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBoxes:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: GboxClient) -> None:
        box = client.v1.boxes.retrieve(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BoxRetrieveResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: GboxClient) -> None:
        response = client.v1.boxes.with_raw_response.retrieve(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = response.parse()
        assert_matches_type(BoxRetrieveResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: GboxClient) -> None:
        with client.v1.boxes.with_streaming_response.retrieve(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = response.parse()
            assert_matches_type(BoxRetrieveResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: GboxClient) -> None:
        box = client.v1.boxes.list()
        assert_matches_type(BoxListResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: GboxClient) -> None:
        box = client.v1.boxes.list(
            device_type="virtual",
            labels={},
            page=1,
            page_size=10,
            status=["running"],
            type=["linux"],
        )
        assert_matches_type(BoxListResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: GboxClient) -> None:
        response = client.v1.boxes.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = response.parse()
        assert_matches_type(BoxListResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: GboxClient) -> None:
        with client.v1.boxes.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = response.parse()
            assert_matches_type(BoxListResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_android(self, client: GboxClient) -> None:
        box = client.v1.boxes.create_android()
        assert_matches_type(AndroidBox, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_android_with_all_params(self, client: GboxClient) -> None:
        box = client.v1.boxes.create_android(
            config={
                "device_type": "virtual",
                "envs": {
                    "ANDROID_LOG_TAGS": "*:V",
                    "ADB_TRACE": "all",
                },
                "expires_in": "15m",
                "labels": {
                    "app": "mobile-testing",
                    "version": "v1.0",
                },
            },
            api_timeout="30s",
            wait=True,
        )
        assert_matches_type(AndroidBox, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_android(self, client: GboxClient) -> None:
        response = client.v1.boxes.with_raw_response.create_android()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = response.parse()
        assert_matches_type(AndroidBox, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_android(self, client: GboxClient) -> None:
        with client.v1.boxes.with_streaming_response.create_android() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = response.parse()
            assert_matches_type(AndroidBox, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_linux(self, client: GboxClient) -> None:
        box = client.v1.boxes.create_linux()
        assert_matches_type(LinuxBox, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_linux_with_all_params(self, client: GboxClient) -> None:
        box = client.v1.boxes.create_linux(
            config={
                "envs": {
                    "DEBUG": "true",
                    "API_URL": "https://api.example.com",
                },
                "expires_in": "60m",
                "labels": {
                    "project": "web-automation",
                    "environment": "testing",
                },
            },
            api_timeout="30s",
            wait=True,
        )
        assert_matches_type(LinuxBox, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_linux(self, client: GboxClient) -> None:
        response = client.v1.boxes.with_raw_response.create_linux()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = response.parse()
        assert_matches_type(LinuxBox, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_linux(self, client: GboxClient) -> None:
        with client.v1.boxes.with_streaming_response.create_linux() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = response.parse()
            assert_matches_type(LinuxBox, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_display(self, client: GboxClient) -> None:
        box = client.v1.boxes.display(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BoxDisplayResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_display(self, client: GboxClient) -> None:
        response = client.v1.boxes.with_raw_response.display(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = response.parse()
        assert_matches_type(BoxDisplayResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_display(self, client: GboxClient) -> None:
        with client.v1.boxes.with_streaming_response.display(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = response.parse()
            assert_matches_type(BoxDisplayResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_display(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.with_raw_response.display(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_commands(self, client: GboxClient) -> None:
        box = client.v1.boxes.execute_commands(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            commands=["ls", "-l"],
        )
        assert_matches_type(BoxExecuteCommandsResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_commands_with_all_params(self, client: GboxClient) -> None:
        box = client.v1.boxes.execute_commands(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            commands=["ls", "-l"],
            envs={
                "PATH": "/usr/bin:/bin",
                "NODE_ENV": "production",
            },
            api_timeout="30s",
            working_dir="/home/user/projects",
        )
        assert_matches_type(BoxExecuteCommandsResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_execute_commands(self, client: GboxClient) -> None:
        response = client.v1.boxes.with_raw_response.execute_commands(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            commands=["ls", "-l"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = response.parse()
        assert_matches_type(BoxExecuteCommandsResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_execute_commands(self, client: GboxClient) -> None:
        with client.v1.boxes.with_streaming_response.execute_commands(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            commands=["ls", "-l"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = response.parse()
            assert_matches_type(BoxExecuteCommandsResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_execute_commands(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.with_raw_response.execute_commands(
                box_id="",
                commands=["ls", "-l"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_live_view_url(self, client: GboxClient) -> None:
        box = client.v1.boxes.live_view_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BoxLiveViewURLResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_live_view_url_with_all_params(self, client: GboxClient) -> None:
        box = client.v1.boxes.live_view_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            expires_in="180m",
        )
        assert_matches_type(BoxLiveViewURLResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_live_view_url(self, client: GboxClient) -> None:
        response = client.v1.boxes.with_raw_response.live_view_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = response.parse()
        assert_matches_type(BoxLiveViewURLResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_live_view_url(self, client: GboxClient) -> None:
        with client.v1.boxes.with_streaming_response.live_view_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = response.parse()
            assert_matches_type(BoxLiveViewURLResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_live_view_url(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.with_raw_response.live_view_url(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_run_code(self, client: GboxClient) -> None:
        box = client.v1.boxes.run_code(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            code='print("Hello, World!")',
        )
        assert_matches_type(BoxRunCodeResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_run_code_with_all_params(self, client: GboxClient) -> None:
        box = client.v1.boxes.run_code(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            code='print("Hello, World!")',
            argv=["--help"],
            envs={
                "PYTHONPATH": "/usr/lib/python",
                "DEBUG": "true",
            },
            language="python",
            api_timeout="30s",
            working_dir="/home/user/scripts",
        )
        assert_matches_type(BoxRunCodeResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_run_code(self, client: GboxClient) -> None:
        response = client.v1.boxes.with_raw_response.run_code(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            code='print("Hello, World!")',
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = response.parse()
        assert_matches_type(BoxRunCodeResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_run_code(self, client: GboxClient) -> None:
        with client.v1.boxes.with_streaming_response.run_code(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            code='print("Hello, World!")',
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = response.parse()
            assert_matches_type(BoxRunCodeResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_run_code(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.with_raw_response.run_code(
                box_id="",
                code='print("Hello, World!")',
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_start(self, client: GboxClient) -> None:
        box = client.v1.boxes.start(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BoxStartResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_start_with_all_params(self, client: GboxClient) -> None:
        box = client.v1.boxes.start(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            wait=True,
        )
        assert_matches_type(BoxStartResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_start(self, client: GboxClient) -> None:
        response = client.v1.boxes.with_raw_response.start(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = response.parse()
        assert_matches_type(BoxStartResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_start(self, client: GboxClient) -> None:
        with client.v1.boxes.with_streaming_response.start(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = response.parse()
            assert_matches_type(BoxStartResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_start(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.with_raw_response.start(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_stop(self, client: GboxClient) -> None:
        box = client.v1.boxes.stop(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BoxStopResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_stop_with_all_params(self, client: GboxClient) -> None:
        box = client.v1.boxes.stop(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            wait=True,
        )
        assert_matches_type(BoxStopResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_stop(self, client: GboxClient) -> None:
        response = client.v1.boxes.with_raw_response.stop(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = response.parse()
        assert_matches_type(BoxStopResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_stop(self, client: GboxClient) -> None:
        with client.v1.boxes.with_streaming_response.stop(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = response.parse()
            assert_matches_type(BoxStopResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_stop(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.with_raw_response.stop(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_terminate(self, client: GboxClient) -> None:
        box = client.v1.boxes.terminate(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert box is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_terminate_with_all_params(self, client: GboxClient) -> None:
        box = client.v1.boxes.terminate(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            wait=True,
        )
        assert box is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_terminate(self, client: GboxClient) -> None:
        response = client.v1.boxes.with_raw_response.terminate(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = response.parse()
        assert box is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_terminate(self, client: GboxClient) -> None:
        with client.v1.boxes.with_streaming_response.terminate(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = response.parse()
            assert box is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_terminate(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.with_raw_response.terminate(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_web_terminal_url(self, client: GboxClient) -> None:
        box = client.v1.boxes.web_terminal_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BoxWebTerminalURLResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_web_terminal_url_with_all_params(self, client: GboxClient) -> None:
        box = client.v1.boxes.web_terminal_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            expires_in="180m",
        )
        assert_matches_type(BoxWebTerminalURLResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_web_terminal_url(self, client: GboxClient) -> None:
        response = client.v1.boxes.with_raw_response.web_terminal_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = response.parse()
        assert_matches_type(BoxWebTerminalURLResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_web_terminal_url(self, client: GboxClient) -> None:
        with client.v1.boxes.with_streaming_response.web_terminal_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = response.parse()
            assert_matches_type(BoxWebTerminalURLResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_web_terminal_url(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.with_raw_response.web_terminal_url(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_websocket_url(self, client: GboxClient) -> None:
        box = client.v1.boxes.websocket_url(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BoxWebsocketURLResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_websocket_url(self, client: GboxClient) -> None:
        response = client.v1.boxes.with_raw_response.websocket_url(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = response.parse()
        assert_matches_type(BoxWebsocketURLResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_websocket_url(self, client: GboxClient) -> None:
        with client.v1.boxes.with_streaming_response.websocket_url(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = response.parse()
            assert_matches_type(BoxWebsocketURLResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_websocket_url(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.with_raw_response.websocket_url(
                "",
            )


class TestAsyncBoxes:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.retrieve(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BoxRetrieveResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.with_raw_response.retrieve(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = await response.parse()
        assert_matches_type(BoxRetrieveResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.with_streaming_response.retrieve(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = await response.parse()
            assert_matches_type(BoxRetrieveResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.list()
        assert_matches_type(BoxListResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.list(
            device_type="virtual",
            labels={},
            page=1,
            page_size=10,
            status=["running"],
            type=["linux"],
        )
        assert_matches_type(BoxListResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = await response.parse()
        assert_matches_type(BoxListResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = await response.parse()
            assert_matches_type(BoxListResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_android(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.create_android()
        assert_matches_type(AndroidBox, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_android_with_all_params(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.create_android(
            config={
                "device_type": "virtual",
                "envs": {
                    "ANDROID_LOG_TAGS": "*:V",
                    "ADB_TRACE": "all",
                },
                "expires_in": "15m",
                "labels": {
                    "app": "mobile-testing",
                    "version": "v1.0",
                },
            },
            api_timeout="30s",
            wait=True,
        )
        assert_matches_type(AndroidBox, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_android(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.with_raw_response.create_android()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = await response.parse()
        assert_matches_type(AndroidBox, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_android(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.with_streaming_response.create_android() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = await response.parse()
            assert_matches_type(AndroidBox, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_linux(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.create_linux()
        assert_matches_type(LinuxBox, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_linux_with_all_params(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.create_linux(
            config={
                "envs": {
                    "DEBUG": "true",
                    "API_URL": "https://api.example.com",
                },
                "expires_in": "60m",
                "labels": {
                    "project": "web-automation",
                    "environment": "testing",
                },
            },
            api_timeout="30s",
            wait=True,
        )
        assert_matches_type(LinuxBox, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_linux(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.with_raw_response.create_linux()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = await response.parse()
        assert_matches_type(LinuxBox, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_linux(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.with_streaming_response.create_linux() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = await response.parse()
            assert_matches_type(LinuxBox, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_display(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.display(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BoxDisplayResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_display(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.with_raw_response.display(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = await response.parse()
        assert_matches_type(BoxDisplayResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_display(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.with_streaming_response.display(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = await response.parse()
            assert_matches_type(BoxDisplayResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_display(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.with_raw_response.display(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_commands(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.execute_commands(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            commands=["ls", "-l"],
        )
        assert_matches_type(BoxExecuteCommandsResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_commands_with_all_params(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.execute_commands(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            commands=["ls", "-l"],
            envs={
                "PATH": "/usr/bin:/bin",
                "NODE_ENV": "production",
            },
            api_timeout="30s",
            working_dir="/home/user/projects",
        )
        assert_matches_type(BoxExecuteCommandsResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_execute_commands(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.with_raw_response.execute_commands(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            commands=["ls", "-l"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = await response.parse()
        assert_matches_type(BoxExecuteCommandsResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_execute_commands(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.with_streaming_response.execute_commands(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            commands=["ls", "-l"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = await response.parse()
            assert_matches_type(BoxExecuteCommandsResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_execute_commands(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.with_raw_response.execute_commands(
                box_id="",
                commands=["ls", "-l"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_live_view_url(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.live_view_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BoxLiveViewURLResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_live_view_url_with_all_params(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.live_view_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            expires_in="180m",
        )
        assert_matches_type(BoxLiveViewURLResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_live_view_url(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.with_raw_response.live_view_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = await response.parse()
        assert_matches_type(BoxLiveViewURLResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_live_view_url(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.with_streaming_response.live_view_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = await response.parse()
            assert_matches_type(BoxLiveViewURLResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_live_view_url(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.with_raw_response.live_view_url(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_run_code(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.run_code(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            code='print("Hello, World!")',
        )
        assert_matches_type(BoxRunCodeResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_run_code_with_all_params(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.run_code(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            code='print("Hello, World!")',
            argv=["--help"],
            envs={
                "PYTHONPATH": "/usr/lib/python",
                "DEBUG": "true",
            },
            language="python",
            api_timeout="30s",
            working_dir="/home/user/scripts",
        )
        assert_matches_type(BoxRunCodeResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_run_code(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.with_raw_response.run_code(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            code='print("Hello, World!")',
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = await response.parse()
        assert_matches_type(BoxRunCodeResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_run_code(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.with_streaming_response.run_code(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            code='print("Hello, World!")',
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = await response.parse()
            assert_matches_type(BoxRunCodeResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_run_code(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.with_raw_response.run_code(
                box_id="",
                code='print("Hello, World!")',
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_start(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.start(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BoxStartResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_start_with_all_params(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.start(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            wait=True,
        )
        assert_matches_type(BoxStartResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_start(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.with_raw_response.start(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = await response.parse()
        assert_matches_type(BoxStartResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_start(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.with_streaming_response.start(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = await response.parse()
            assert_matches_type(BoxStartResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_start(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.with_raw_response.start(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_stop(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.stop(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BoxStopResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_stop_with_all_params(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.stop(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            wait=True,
        )
        assert_matches_type(BoxStopResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_stop(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.with_raw_response.stop(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = await response.parse()
        assert_matches_type(BoxStopResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_stop(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.with_streaming_response.stop(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = await response.parse()
            assert_matches_type(BoxStopResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_stop(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.with_raw_response.stop(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_terminate(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.terminate(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert box is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_terminate_with_all_params(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.terminate(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            wait=True,
        )
        assert box is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_terminate(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.with_raw_response.terminate(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = await response.parse()
        assert box is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_terminate(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.with_streaming_response.terminate(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = await response.parse()
            assert box is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_terminate(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.with_raw_response.terminate(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_web_terminal_url(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.web_terminal_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BoxWebTerminalURLResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_web_terminal_url_with_all_params(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.web_terminal_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            expires_in="180m",
        )
        assert_matches_type(BoxWebTerminalURLResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_web_terminal_url(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.with_raw_response.web_terminal_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = await response.parse()
        assert_matches_type(BoxWebTerminalURLResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_web_terminal_url(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.with_streaming_response.web_terminal_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = await response.parse()
            assert_matches_type(BoxWebTerminalURLResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_web_terminal_url(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.with_raw_response.web_terminal_url(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_websocket_url(self, async_client: AsyncGboxClient) -> None:
        box = await async_client.v1.boxes.websocket_url(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BoxWebsocketURLResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_websocket_url(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.with_raw_response.websocket_url(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        box = await response.parse()
        assert_matches_type(BoxWebsocketURLResponse, box, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_websocket_url(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.with_streaming_response.websocket_url(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            box = await response.parse()
            assert_matches_type(BoxWebsocketURLResponse, box, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_websocket_url(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.with_raw_response.websocket_url(
                "",
            )
