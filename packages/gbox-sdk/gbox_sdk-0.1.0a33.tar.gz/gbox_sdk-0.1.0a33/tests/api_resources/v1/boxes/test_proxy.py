# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from gbox_sdk import GboxClient, AsyncGboxClient

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestProxy:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_clear(self, client: GboxClient) -> None:
        proxy = client.v1.boxes.proxy.clear(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert proxy is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_clear(self, client: GboxClient) -> None:
        response = client.v1.boxes.proxy.with_raw_response.clear(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        proxy = response.parse()
        assert proxy is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_clear(self, client: GboxClient) -> None:
        with client.v1.boxes.proxy.with_streaming_response.clear(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            proxy = response.parse()
            assert proxy is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_clear(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.proxy.with_raw_response.clear(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: GboxClient) -> None:
        proxy = client.v1.boxes.proxy.get(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert proxy is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: GboxClient) -> None:
        response = client.v1.boxes.proxy.with_raw_response.get(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        proxy = response.parse()
        assert proxy is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: GboxClient) -> None:
        with client.v1.boxes.proxy.with_streaming_response.get(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            proxy = response.parse()
            assert proxy is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.proxy.with_raw_response.get(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set(self, client: GboxClient) -> None:
        proxy = client.v1.boxes.proxy.set(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            auth={
                "password": "password",
                "username": "admin",
            },
            excludes=["127.0.0.1", "localhost"],
            url="http://127.0.0.1:8080",
        )
        assert proxy is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_set(self, client: GboxClient) -> None:
        response = client.v1.boxes.proxy.with_raw_response.set(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            auth={
                "password": "password",
                "username": "admin",
            },
            excludes=["127.0.0.1", "localhost"],
            url="http://127.0.0.1:8080",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        proxy = response.parse()
        assert proxy is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_set(self, client: GboxClient) -> None:
        with client.v1.boxes.proxy.with_streaming_response.set(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            auth={
                "password": "password",
                "username": "admin",
            },
            excludes=["127.0.0.1", "localhost"],
            url="http://127.0.0.1:8080",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            proxy = response.parse()
            assert proxy is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_set(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.proxy.with_raw_response.set(
                box_id="",
                auth={
                    "password": "password",
                    "username": "admin",
                },
                excludes=["127.0.0.1", "localhost"],
                url="http://127.0.0.1:8080",
            )


class TestAsyncProxy:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_clear(self, async_client: AsyncGboxClient) -> None:
        proxy = await async_client.v1.boxes.proxy.clear(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert proxy is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_clear(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.proxy.with_raw_response.clear(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        proxy = await response.parse()
        assert proxy is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_clear(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.proxy.with_streaming_response.clear(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            proxy = await response.parse()
            assert proxy is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_clear(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.proxy.with_raw_response.clear(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncGboxClient) -> None:
        proxy = await async_client.v1.boxes.proxy.get(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert proxy is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.proxy.with_raw_response.get(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        proxy = await response.parse()
        assert proxy is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.proxy.with_streaming_response.get(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            proxy = await response.parse()
            assert proxy is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.proxy.with_raw_response.get(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set(self, async_client: AsyncGboxClient) -> None:
        proxy = await async_client.v1.boxes.proxy.set(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            auth={
                "password": "password",
                "username": "admin",
            },
            excludes=["127.0.0.1", "localhost"],
            url="http://127.0.0.1:8080",
        )
        assert proxy is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_set(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.proxy.with_raw_response.set(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            auth={
                "password": "password",
                "username": "admin",
            },
            excludes=["127.0.0.1", "localhost"],
            url="http://127.0.0.1:8080",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        proxy = await response.parse()
        assert proxy is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_set(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.proxy.with_streaming_response.set(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            auth={
                "password": "password",
                "username": "admin",
            },
            excludes=["127.0.0.1", "localhost"],
            url="http://127.0.0.1:8080",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            proxy = await response.parse()
            assert proxy is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_set(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.proxy.with_raw_response.set(
                box_id="",
                auth={
                    "password": "password",
                    "username": "admin",
                },
                excludes=["127.0.0.1", "localhost"],
                url="http://127.0.0.1:8080",
            )
