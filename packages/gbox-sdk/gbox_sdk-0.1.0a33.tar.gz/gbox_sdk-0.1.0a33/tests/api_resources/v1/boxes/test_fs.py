# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from gbox_sdk import GboxClient, AsyncGboxClient
from tests.utils import assert_matches_type
from gbox_sdk.types.v1.boxes import (
    FInfoResponse,
    FListResponse,
    FReadResponse,
    FWriteResponse,
    FExistsResponse,
    FRemoveResponse,
    FRenameResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: GboxClient) -> None:
        f = client.v1.boxes.fs.list(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents",
        )
        assert_matches_type(FListResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: GboxClient) -> None:
        f = client.v1.boxes.fs.list(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents",
            depth=2,
            working_dir="/home/user/documents",
        )
        assert_matches_type(FListResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: GboxClient) -> None:
        response = client.v1.boxes.fs.with_raw_response.list(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        f = response.parse()
        assert_matches_type(FListResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: GboxClient) -> None:
        with client.v1.boxes.fs.with_streaming_response.list(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            f = response.parse()
            assert_matches_type(FListResponse, f, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.fs.with_raw_response.list(
                box_id="",
                path="/home/user/documents",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_exists(self, client: GboxClient) -> None:
        f = client.v1.boxes.fs.exists(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
        )
        assert_matches_type(FExistsResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_exists_with_all_params(self, client: GboxClient) -> None:
        f = client.v1.boxes.fs.exists(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
            working_dir="/home/user/documents",
        )
        assert_matches_type(FExistsResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_exists(self, client: GboxClient) -> None:
        response = client.v1.boxes.fs.with_raw_response.exists(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        f = response.parse()
        assert_matches_type(FExistsResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_exists(self, client: GboxClient) -> None:
        with client.v1.boxes.fs.with_streaming_response.exists(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            f = response.parse()
            assert_matches_type(FExistsResponse, f, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_exists(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.fs.with_raw_response.exists(
                box_id="",
                path="/home/user/documents/output.txt",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_info(self, client: GboxClient) -> None:
        f = client.v1.boxes.fs.info(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
        )
        assert_matches_type(FInfoResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_info_with_all_params(self, client: GboxClient) -> None:
        f = client.v1.boxes.fs.info(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
            working_dir="/home/user/documents",
        )
        assert_matches_type(FInfoResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_info(self, client: GboxClient) -> None:
        response = client.v1.boxes.fs.with_raw_response.info(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        f = response.parse()
        assert_matches_type(FInfoResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_info(self, client: GboxClient) -> None:
        with client.v1.boxes.fs.with_streaming_response.info(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            f = response.parse()
            assert_matches_type(FInfoResponse, f, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_info(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.fs.with_raw_response.info(
                box_id="",
                path="/home/user/documents/output.txt",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_read(self, client: GboxClient) -> None:
        f = client.v1.boxes.fs.read(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/config.json",
        )
        assert_matches_type(FReadResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_read_with_all_params(self, client: GboxClient) -> None:
        f = client.v1.boxes.fs.read(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/config.json",
            working_dir="/home/user/documents",
        )
        assert_matches_type(FReadResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_read(self, client: GboxClient) -> None:
        response = client.v1.boxes.fs.with_raw_response.read(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/config.json",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        f = response.parse()
        assert_matches_type(FReadResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_read(self, client: GboxClient) -> None:
        with client.v1.boxes.fs.with_streaming_response.read(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/config.json",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            f = response.parse()
            assert_matches_type(FReadResponse, f, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_read(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.fs.with_raw_response.read(
                box_id="",
                path="/home/user/documents/config.json",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_remove(self, client: GboxClient) -> None:
        f = client.v1.boxes.fs.remove(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
        )
        assert_matches_type(FRemoveResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_remove_with_all_params(self, client: GboxClient) -> None:
        f = client.v1.boxes.fs.remove(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
            working_dir="/home/user/documents",
        )
        assert_matches_type(FRemoveResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_remove(self, client: GboxClient) -> None:
        response = client.v1.boxes.fs.with_raw_response.remove(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        f = response.parse()
        assert_matches_type(FRemoveResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_remove(self, client: GboxClient) -> None:
        with client.v1.boxes.fs.with_streaming_response.remove(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            f = response.parse()
            assert_matches_type(FRemoveResponse, f, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_remove(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.fs.with_raw_response.remove(
                box_id="",
                path="/home/user/documents/output.txt",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_rename(self, client: GboxClient) -> None:
        f = client.v1.boxes.fs.rename(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            new_path="/home/user/documents/new-name.txt",
            old_path="/home/user/documents/output.txt",
        )
        assert_matches_type(FRenameResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_rename_with_all_params(self, client: GboxClient) -> None:
        f = client.v1.boxes.fs.rename(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            new_path="/home/user/documents/new-name.txt",
            old_path="/home/user/documents/output.txt",
            working_dir="/home/user/documents",
        )
        assert_matches_type(FRenameResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_rename(self, client: GboxClient) -> None:
        response = client.v1.boxes.fs.with_raw_response.rename(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            new_path="/home/user/documents/new-name.txt",
            old_path="/home/user/documents/output.txt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        f = response.parse()
        assert_matches_type(FRenameResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_rename(self, client: GboxClient) -> None:
        with client.v1.boxes.fs.with_streaming_response.rename(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            new_path="/home/user/documents/new-name.txt",
            old_path="/home/user/documents/output.txt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            f = response.parse()
            assert_matches_type(FRenameResponse, f, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_rename(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.fs.with_raw_response.rename(
                box_id="",
                new_path="/home/user/documents/new-name.txt",
                old_path="/home/user/documents/output.txt",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_write_overload_1(self, client: GboxClient) -> None:
        f = client.v1.boxes.fs.write(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content="Hello, World!\nThis is file content.",
            path="/home/user/documents/output.txt",
        )
        assert_matches_type(FWriteResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_write_with_all_params_overload_1(self, client: GboxClient) -> None:
        f = client.v1.boxes.fs.write(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content="Hello, World!\nThis is file content.",
            path="/home/user/documents/output.txt",
            working_dir="/home/user/documents",
        )
        assert_matches_type(FWriteResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_write_overload_1(self, client: GboxClient) -> None:
        response = client.v1.boxes.fs.with_raw_response.write(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content="Hello, World!\nThis is file content.",
            path="/home/user/documents/output.txt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        f = response.parse()
        assert_matches_type(FWriteResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_write_overload_1(self, client: GboxClient) -> None:
        with client.v1.boxes.fs.with_streaming_response.write(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content="Hello, World!\nThis is file content.",
            path="/home/user/documents/output.txt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            f = response.parse()
            assert_matches_type(FWriteResponse, f, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_write_overload_1(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.fs.with_raw_response.write(
                box_id="",
                content="Hello, World!\nThis is file content.",
                path="/home/user/documents/output.txt",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_write_overload_2(self, client: GboxClient) -> None:
        f = client.v1.boxes.fs.write(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content=b"raw file contents",
            path="/home/user/documents/output.txt",
        )
        assert_matches_type(FWriteResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_write_with_all_params_overload_2(self, client: GboxClient) -> None:
        f = client.v1.boxes.fs.write(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content=b"raw file contents",
            path="/home/user/documents/output.txt",
            working_dir="/home/user/documents",
        )
        assert_matches_type(FWriteResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_write_overload_2(self, client: GboxClient) -> None:
        response = client.v1.boxes.fs.with_raw_response.write(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content=b"raw file contents",
            path="/home/user/documents/output.txt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        f = response.parse()
        assert_matches_type(FWriteResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_write_overload_2(self, client: GboxClient) -> None:
        with client.v1.boxes.fs.with_streaming_response.write(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content=b"raw file contents",
            path="/home/user/documents/output.txt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            f = response.parse()
            assert_matches_type(FWriteResponse, f, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_write_overload_2(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.fs.with_raw_response.write(
                box_id="",
                content=b"raw file contents",
                path="/home/user/documents/output.txt",
            )


class TestAsyncFs:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncGboxClient) -> None:
        f = await async_client.v1.boxes.fs.list(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents",
        )
        assert_matches_type(FListResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncGboxClient) -> None:
        f = await async_client.v1.boxes.fs.list(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents",
            depth=2,
            working_dir="/home/user/documents",
        )
        assert_matches_type(FListResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.fs.with_raw_response.list(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        f = await response.parse()
        assert_matches_type(FListResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.fs.with_streaming_response.list(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            f = await response.parse()
            assert_matches_type(FListResponse, f, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.fs.with_raw_response.list(
                box_id="",
                path="/home/user/documents",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_exists(self, async_client: AsyncGboxClient) -> None:
        f = await async_client.v1.boxes.fs.exists(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
        )
        assert_matches_type(FExistsResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_exists_with_all_params(self, async_client: AsyncGboxClient) -> None:
        f = await async_client.v1.boxes.fs.exists(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
            working_dir="/home/user/documents",
        )
        assert_matches_type(FExistsResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_exists(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.fs.with_raw_response.exists(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        f = await response.parse()
        assert_matches_type(FExistsResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_exists(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.fs.with_streaming_response.exists(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            f = await response.parse()
            assert_matches_type(FExistsResponse, f, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_exists(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.fs.with_raw_response.exists(
                box_id="",
                path="/home/user/documents/output.txt",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_info(self, async_client: AsyncGboxClient) -> None:
        f = await async_client.v1.boxes.fs.info(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
        )
        assert_matches_type(FInfoResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_info_with_all_params(self, async_client: AsyncGboxClient) -> None:
        f = await async_client.v1.boxes.fs.info(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
            working_dir="/home/user/documents",
        )
        assert_matches_type(FInfoResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_info(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.fs.with_raw_response.info(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        f = await response.parse()
        assert_matches_type(FInfoResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_info(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.fs.with_streaming_response.info(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            f = await response.parse()
            assert_matches_type(FInfoResponse, f, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_info(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.fs.with_raw_response.info(
                box_id="",
                path="/home/user/documents/output.txt",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_read(self, async_client: AsyncGboxClient) -> None:
        f = await async_client.v1.boxes.fs.read(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/config.json",
        )
        assert_matches_type(FReadResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_read_with_all_params(self, async_client: AsyncGboxClient) -> None:
        f = await async_client.v1.boxes.fs.read(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/config.json",
            working_dir="/home/user/documents",
        )
        assert_matches_type(FReadResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_read(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.fs.with_raw_response.read(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/config.json",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        f = await response.parse()
        assert_matches_type(FReadResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_read(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.fs.with_streaming_response.read(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/config.json",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            f = await response.parse()
            assert_matches_type(FReadResponse, f, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_read(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.fs.with_raw_response.read(
                box_id="",
                path="/home/user/documents/config.json",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_remove(self, async_client: AsyncGboxClient) -> None:
        f = await async_client.v1.boxes.fs.remove(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
        )
        assert_matches_type(FRemoveResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_remove_with_all_params(self, async_client: AsyncGboxClient) -> None:
        f = await async_client.v1.boxes.fs.remove(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
            working_dir="/home/user/documents",
        )
        assert_matches_type(FRemoveResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_remove(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.fs.with_raw_response.remove(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        f = await response.parse()
        assert_matches_type(FRemoveResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_remove(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.fs.with_streaming_response.remove(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path="/home/user/documents/output.txt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            f = await response.parse()
            assert_matches_type(FRemoveResponse, f, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_remove(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.fs.with_raw_response.remove(
                box_id="",
                path="/home/user/documents/output.txt",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_rename(self, async_client: AsyncGboxClient) -> None:
        f = await async_client.v1.boxes.fs.rename(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            new_path="/home/user/documents/new-name.txt",
            old_path="/home/user/documents/output.txt",
        )
        assert_matches_type(FRenameResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_rename_with_all_params(self, async_client: AsyncGboxClient) -> None:
        f = await async_client.v1.boxes.fs.rename(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            new_path="/home/user/documents/new-name.txt",
            old_path="/home/user/documents/output.txt",
            working_dir="/home/user/documents",
        )
        assert_matches_type(FRenameResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_rename(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.fs.with_raw_response.rename(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            new_path="/home/user/documents/new-name.txt",
            old_path="/home/user/documents/output.txt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        f = await response.parse()
        assert_matches_type(FRenameResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_rename(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.fs.with_streaming_response.rename(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            new_path="/home/user/documents/new-name.txt",
            old_path="/home/user/documents/output.txt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            f = await response.parse()
            assert_matches_type(FRenameResponse, f, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_rename(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.fs.with_raw_response.rename(
                box_id="",
                new_path="/home/user/documents/new-name.txt",
                old_path="/home/user/documents/output.txt",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_write_overload_1(self, async_client: AsyncGboxClient) -> None:
        f = await async_client.v1.boxes.fs.write(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content="Hello, World!\nThis is file content.",
            path="/home/user/documents/output.txt",
        )
        assert_matches_type(FWriteResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_write_with_all_params_overload_1(self, async_client: AsyncGboxClient) -> None:
        f = await async_client.v1.boxes.fs.write(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content="Hello, World!\nThis is file content.",
            path="/home/user/documents/output.txt",
            working_dir="/home/user/documents",
        )
        assert_matches_type(FWriteResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_write_overload_1(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.fs.with_raw_response.write(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content="Hello, World!\nThis is file content.",
            path="/home/user/documents/output.txt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        f = await response.parse()
        assert_matches_type(FWriteResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_write_overload_1(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.fs.with_streaming_response.write(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content="Hello, World!\nThis is file content.",
            path="/home/user/documents/output.txt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            f = await response.parse()
            assert_matches_type(FWriteResponse, f, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_write_overload_1(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.fs.with_raw_response.write(
                box_id="",
                content="Hello, World!\nThis is file content.",
                path="/home/user/documents/output.txt",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_write_overload_2(self, async_client: AsyncGboxClient) -> None:
        f = await async_client.v1.boxes.fs.write(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content=b"raw file contents",
            path="/home/user/documents/output.txt",
        )
        assert_matches_type(FWriteResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_write_with_all_params_overload_2(self, async_client: AsyncGboxClient) -> None:
        f = await async_client.v1.boxes.fs.write(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content=b"raw file contents",
            path="/home/user/documents/output.txt",
            working_dir="/home/user/documents",
        )
        assert_matches_type(FWriteResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_write_overload_2(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.fs.with_raw_response.write(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content=b"raw file contents",
            path="/home/user/documents/output.txt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        f = await response.parse()
        assert_matches_type(FWriteResponse, f, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_write_overload_2(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.fs.with_streaming_response.write(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content=b"raw file contents",
            path="/home/user/documents/output.txt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            f = await response.parse()
            assert_matches_type(FWriteResponse, f, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_write_overload_2(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.fs.with_raw_response.write(
                box_id="",
                content=b"raw file contents",
                path="/home/user/documents/output.txt",
            )
