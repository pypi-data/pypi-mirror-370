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
    MediaGetMediaResponse,
    MediaListMediaResponse,
    MediaListAlbumsResponse,
    MediaCreateAlbumResponse,
    MediaUpdateAlbumResponse,
    MediaGetAlbumDetailResponse,
    MediaGetMediaSupportResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMedia:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_album(self, client: GboxClient) -> None:
        media = client.v1.boxes.media.create_album(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            name="Vacation Photos",
        )
        assert_matches_type(MediaCreateAlbumResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_album_with_all_params(self, client: GboxClient) -> None:
        media = client.v1.boxes.media.create_album(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            name="Vacation Photos",
            media=[b"raw file contents"],
        )
        assert_matches_type(MediaCreateAlbumResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_album(self, client: GboxClient) -> None:
        response = client.v1.boxes.media.with_raw_response.create_album(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            name="Vacation Photos",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        media = response.parse()
        assert_matches_type(MediaCreateAlbumResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_album(self, client: GboxClient) -> None:
        with client.v1.boxes.media.with_streaming_response.create_album(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            name="Vacation Photos",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            media = response.parse()
            assert_matches_type(MediaCreateAlbumResponse, media, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_album(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.media.with_raw_response.create_album(
                box_id="",
                name="Vacation Photos",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_album(self, client: GboxClient) -> None:
        media = client.v1.boxes.media.delete_album(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert media is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete_album(self, client: GboxClient) -> None:
        response = client.v1.boxes.media.with_raw_response.delete_album(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        media = response.parse()
        assert media is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete_album(self, client: GboxClient) -> None:
        with client.v1.boxes.media.with_streaming_response.delete_album(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            media = response.parse()
            assert media is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete_album(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.media.with_raw_response.delete_album(
                album_name="Pictures",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `album_name` but received ''"):
            client.v1.boxes.media.with_raw_response.delete_album(
                album_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_media(self, client: GboxClient) -> None:
        media = client.v1.boxes.media.delete_media(
            media_name="IMG_001.jpg",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            album_name="Pictures",
        )
        assert media is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete_media(self, client: GboxClient) -> None:
        response = client.v1.boxes.media.with_raw_response.delete_media(
            media_name="IMG_001.jpg",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            album_name="Pictures",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        media = response.parse()
        assert media is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete_media(self, client: GboxClient) -> None:
        with client.v1.boxes.media.with_streaming_response.delete_media(
            media_name="IMG_001.jpg",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            album_name="Pictures",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            media = response.parse()
            assert media is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete_media(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.media.with_raw_response.delete_media(
                media_name="IMG_001.jpg",
                box_id="",
                album_name="Pictures",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `album_name` but received ''"):
            client.v1.boxes.media.with_raw_response.delete_media(
                media_name="IMG_001.jpg",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
                album_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `media_name` but received ''"):
            client.v1.boxes.media.with_raw_response.delete_media(
                media_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
                album_name="Pictures",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_download_media(self, client: GboxClient, respx_mock: MockRouter) -> None:
        respx_mock.get(
            "/boxes/c9bdc193-b54b-4ddb-a035-5ac0c598d32d/media/albums/Pictures/media/IMG_001.jpg/download"
        ).mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        media = client.v1.boxes.media.download_media(
            media_name="IMG_001.jpg",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            album_name="Pictures",
        )
        assert media.is_closed
        assert media.json() == {"foo": "bar"}
        assert cast(Any, media.is_closed) is True
        assert isinstance(media, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_download_media(self, client: GboxClient, respx_mock: MockRouter) -> None:
        respx_mock.get(
            "/boxes/c9bdc193-b54b-4ddb-a035-5ac0c598d32d/media/albums/Pictures/media/IMG_001.jpg/download"
        ).mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        media = client.v1.boxes.media.with_raw_response.download_media(
            media_name="IMG_001.jpg",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            album_name="Pictures",
        )

        assert media.is_closed is True
        assert media.http_request.headers.get("X-Stainless-Lang") == "python"
        assert media.json() == {"foo": "bar"}
        assert isinstance(media, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_download_media(self, client: GboxClient, respx_mock: MockRouter) -> None:
        respx_mock.get(
            "/boxes/c9bdc193-b54b-4ddb-a035-5ac0c598d32d/media/albums/Pictures/media/IMG_001.jpg/download"
        ).mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.v1.boxes.media.with_streaming_response.download_media(
            media_name="IMG_001.jpg",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            album_name="Pictures",
        ) as media:
            assert not media.is_closed
            assert media.http_request.headers.get("X-Stainless-Lang") == "python"

            assert media.json() == {"foo": "bar"}
            assert cast(Any, media.is_closed) is True
            assert isinstance(media, StreamedBinaryAPIResponse)

        assert cast(Any, media.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_download_media(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.media.with_raw_response.download_media(
                media_name="IMG_001.jpg",
                box_id="",
                album_name="Pictures",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `album_name` but received ''"):
            client.v1.boxes.media.with_raw_response.download_media(
                media_name="IMG_001.jpg",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
                album_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `media_name` but received ''"):
            client.v1.boxes.media.with_raw_response.download_media(
                media_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
                album_name="Pictures",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_album_detail(self, client: GboxClient) -> None:
        media = client.v1.boxes.media.get_album_detail(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(MediaGetAlbumDetailResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_album_detail(self, client: GboxClient) -> None:
        response = client.v1.boxes.media.with_raw_response.get_album_detail(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        media = response.parse()
        assert_matches_type(MediaGetAlbumDetailResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_album_detail(self, client: GboxClient) -> None:
        with client.v1.boxes.media.with_streaming_response.get_album_detail(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            media = response.parse()
            assert_matches_type(MediaGetAlbumDetailResponse, media, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_album_detail(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.media.with_raw_response.get_album_detail(
                album_name="Pictures",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `album_name` but received ''"):
            client.v1.boxes.media.with_raw_response.get_album_detail(
                album_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_media(self, client: GboxClient) -> None:
        media = client.v1.boxes.media.get_media(
            media_name="IMG_001.jpg",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            album_name="Pictures",
        )
        assert_matches_type(MediaGetMediaResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_media(self, client: GboxClient) -> None:
        response = client.v1.boxes.media.with_raw_response.get_media(
            media_name="IMG_001.jpg",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            album_name="Pictures",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        media = response.parse()
        assert_matches_type(MediaGetMediaResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_media(self, client: GboxClient) -> None:
        with client.v1.boxes.media.with_streaming_response.get_media(
            media_name="IMG_001.jpg",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            album_name="Pictures",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            media = response.parse()
            assert_matches_type(MediaGetMediaResponse, media, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_media(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.media.with_raw_response.get_media(
                media_name="IMG_001.jpg",
                box_id="",
                album_name="Pictures",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `album_name` but received ''"):
            client.v1.boxes.media.with_raw_response.get_media(
                media_name="IMG_001.jpg",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
                album_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `media_name` but received ''"):
            client.v1.boxes.media.with_raw_response.get_media(
                media_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
                album_name="Pictures",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_media_support(self, client: GboxClient) -> None:
        media = client.v1.boxes.media.get_media_support(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(MediaGetMediaSupportResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_media_support(self, client: GboxClient) -> None:
        response = client.v1.boxes.media.with_raw_response.get_media_support(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        media = response.parse()
        assert_matches_type(MediaGetMediaSupportResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_media_support(self, client: GboxClient) -> None:
        with client.v1.boxes.media.with_streaming_response.get_media_support(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            media = response.parse()
            assert_matches_type(MediaGetMediaSupportResponse, media, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_media_support(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.media.with_raw_response.get_media_support(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_albums(self, client: GboxClient) -> None:
        media = client.v1.boxes.media.list_albums(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(MediaListAlbumsResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_albums(self, client: GboxClient) -> None:
        response = client.v1.boxes.media.with_raw_response.list_albums(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        media = response.parse()
        assert_matches_type(MediaListAlbumsResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_albums(self, client: GboxClient) -> None:
        with client.v1.boxes.media.with_streaming_response.list_albums(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            media = response.parse()
            assert_matches_type(MediaListAlbumsResponse, media, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_albums(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.media.with_raw_response.list_albums(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_media(self, client: GboxClient) -> None:
        media = client.v1.boxes.media.list_media(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(MediaListMediaResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_media(self, client: GboxClient) -> None:
        response = client.v1.boxes.media.with_raw_response.list_media(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        media = response.parse()
        assert_matches_type(MediaListMediaResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_media(self, client: GboxClient) -> None:
        with client.v1.boxes.media.with_streaming_response.list_media(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            media = response.parse()
            assert_matches_type(MediaListMediaResponse, media, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_media(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.media.with_raw_response.list_media(
                album_name="Pictures",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `album_name` but received ''"):
            client.v1.boxes.media.with_raw_response.list_media(
                album_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_album(self, client: GboxClient) -> None:
        media = client.v1.boxes.media.update_album(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            media=[b"raw file contents"],
        )
        assert_matches_type(MediaUpdateAlbumResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_album(self, client: GboxClient) -> None:
        response = client.v1.boxes.media.with_raw_response.update_album(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            media=[b"raw file contents"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        media = response.parse()
        assert_matches_type(MediaUpdateAlbumResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_album(self, client: GboxClient) -> None:
        with client.v1.boxes.media.with_streaming_response.update_album(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            media=[b"raw file contents"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            media = response.parse()
            assert_matches_type(MediaUpdateAlbumResponse, media, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_album(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.media.with_raw_response.update_album(
                album_name="Pictures",
                box_id="",
                media=[b"raw file contents"],
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `album_name` but received ''"):
            client.v1.boxes.media.with_raw_response.update_album(
                album_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
                media=[b"raw file contents"],
            )


class TestAsyncMedia:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_album(self, async_client: AsyncGboxClient) -> None:
        media = await async_client.v1.boxes.media.create_album(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            name="Vacation Photos",
        )
        assert_matches_type(MediaCreateAlbumResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_album_with_all_params(self, async_client: AsyncGboxClient) -> None:
        media = await async_client.v1.boxes.media.create_album(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            name="Vacation Photos",
            media=[b"raw file contents"],
        )
        assert_matches_type(MediaCreateAlbumResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_album(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.media.with_raw_response.create_album(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            name="Vacation Photos",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        media = await response.parse()
        assert_matches_type(MediaCreateAlbumResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_album(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.media.with_streaming_response.create_album(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            name="Vacation Photos",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            media = await response.parse()
            assert_matches_type(MediaCreateAlbumResponse, media, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_album(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.create_album(
                box_id="",
                name="Vacation Photos",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_album(self, async_client: AsyncGboxClient) -> None:
        media = await async_client.v1.boxes.media.delete_album(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert media is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete_album(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.media.with_raw_response.delete_album(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        media = await response.parse()
        assert media is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete_album(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.media.with_streaming_response.delete_album(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            media = await response.parse()
            assert media is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete_album(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.delete_album(
                album_name="Pictures",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `album_name` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.delete_album(
                album_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_media(self, async_client: AsyncGboxClient) -> None:
        media = await async_client.v1.boxes.media.delete_media(
            media_name="IMG_001.jpg",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            album_name="Pictures",
        )
        assert media is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete_media(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.media.with_raw_response.delete_media(
            media_name="IMG_001.jpg",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            album_name="Pictures",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        media = await response.parse()
        assert media is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete_media(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.media.with_streaming_response.delete_media(
            media_name="IMG_001.jpg",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            album_name="Pictures",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            media = await response.parse()
            assert media is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete_media(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.delete_media(
                media_name="IMG_001.jpg",
                box_id="",
                album_name="Pictures",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `album_name` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.delete_media(
                media_name="IMG_001.jpg",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
                album_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `media_name` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.delete_media(
                media_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
                album_name="Pictures",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_download_media(self, async_client: AsyncGboxClient, respx_mock: MockRouter) -> None:
        respx_mock.get(
            "/boxes/c9bdc193-b54b-4ddb-a035-5ac0c598d32d/media/albums/Pictures/media/IMG_001.jpg/download"
        ).mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        media = await async_client.v1.boxes.media.download_media(
            media_name="IMG_001.jpg",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            album_name="Pictures",
        )
        assert media.is_closed
        assert await media.json() == {"foo": "bar"}
        assert cast(Any, media.is_closed) is True
        assert isinstance(media, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_download_media(self, async_client: AsyncGboxClient, respx_mock: MockRouter) -> None:
        respx_mock.get(
            "/boxes/c9bdc193-b54b-4ddb-a035-5ac0c598d32d/media/albums/Pictures/media/IMG_001.jpg/download"
        ).mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        media = await async_client.v1.boxes.media.with_raw_response.download_media(
            media_name="IMG_001.jpg",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            album_name="Pictures",
        )

        assert media.is_closed is True
        assert media.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await media.json() == {"foo": "bar"}
        assert isinstance(media, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_download_media(
        self, async_client: AsyncGboxClient, respx_mock: MockRouter
    ) -> None:
        respx_mock.get(
            "/boxes/c9bdc193-b54b-4ddb-a035-5ac0c598d32d/media/albums/Pictures/media/IMG_001.jpg/download"
        ).mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.v1.boxes.media.with_streaming_response.download_media(
            media_name="IMG_001.jpg",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            album_name="Pictures",
        ) as media:
            assert not media.is_closed
            assert media.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await media.json() == {"foo": "bar"}
            assert cast(Any, media.is_closed) is True
            assert isinstance(media, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, media.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_download_media(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.download_media(
                media_name="IMG_001.jpg",
                box_id="",
                album_name="Pictures",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `album_name` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.download_media(
                media_name="IMG_001.jpg",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
                album_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `media_name` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.download_media(
                media_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
                album_name="Pictures",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_album_detail(self, async_client: AsyncGboxClient) -> None:
        media = await async_client.v1.boxes.media.get_album_detail(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(MediaGetAlbumDetailResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_album_detail(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.media.with_raw_response.get_album_detail(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        media = await response.parse()
        assert_matches_type(MediaGetAlbumDetailResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_album_detail(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.media.with_streaming_response.get_album_detail(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            media = await response.parse()
            assert_matches_type(MediaGetAlbumDetailResponse, media, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_album_detail(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.get_album_detail(
                album_name="Pictures",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `album_name` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.get_album_detail(
                album_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_media(self, async_client: AsyncGboxClient) -> None:
        media = await async_client.v1.boxes.media.get_media(
            media_name="IMG_001.jpg",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            album_name="Pictures",
        )
        assert_matches_type(MediaGetMediaResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_media(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.media.with_raw_response.get_media(
            media_name="IMG_001.jpg",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            album_name="Pictures",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        media = await response.parse()
        assert_matches_type(MediaGetMediaResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_media(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.media.with_streaming_response.get_media(
            media_name="IMG_001.jpg",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            album_name="Pictures",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            media = await response.parse()
            assert_matches_type(MediaGetMediaResponse, media, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_media(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.get_media(
                media_name="IMG_001.jpg",
                box_id="",
                album_name="Pictures",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `album_name` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.get_media(
                media_name="IMG_001.jpg",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
                album_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `media_name` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.get_media(
                media_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
                album_name="Pictures",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_media_support(self, async_client: AsyncGboxClient) -> None:
        media = await async_client.v1.boxes.media.get_media_support(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(MediaGetMediaSupportResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_media_support(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.media.with_raw_response.get_media_support(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        media = await response.parse()
        assert_matches_type(MediaGetMediaSupportResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_media_support(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.media.with_streaming_response.get_media_support(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            media = await response.parse()
            assert_matches_type(MediaGetMediaSupportResponse, media, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_media_support(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.get_media_support(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_albums(self, async_client: AsyncGboxClient) -> None:
        media = await async_client.v1.boxes.media.list_albums(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(MediaListAlbumsResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_albums(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.media.with_raw_response.list_albums(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        media = await response.parse()
        assert_matches_type(MediaListAlbumsResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_albums(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.media.with_streaming_response.list_albums(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            media = await response.parse()
            assert_matches_type(MediaListAlbumsResponse, media, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_albums(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.list_albums(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_media(self, async_client: AsyncGboxClient) -> None:
        media = await async_client.v1.boxes.media.list_media(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(MediaListMediaResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_media(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.media.with_raw_response.list_media(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        media = await response.parse()
        assert_matches_type(MediaListMediaResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_media(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.media.with_streaming_response.list_media(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            media = await response.parse()
            assert_matches_type(MediaListMediaResponse, media, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_media(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.list_media(
                album_name="Pictures",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `album_name` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.list_media(
                album_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_album(self, async_client: AsyncGboxClient) -> None:
        media = await async_client.v1.boxes.media.update_album(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            media=[b"raw file contents"],
        )
        assert_matches_type(MediaUpdateAlbumResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_album(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.media.with_raw_response.update_album(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            media=[b"raw file contents"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        media = await response.parse()
        assert_matches_type(MediaUpdateAlbumResponse, media, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_album(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.media.with_streaming_response.update_album(
            album_name="Pictures",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            media=[b"raw file contents"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            media = await response.parse()
            assert_matches_type(MediaUpdateAlbumResponse, media, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_album(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.update_album(
                album_name="Pictures",
                box_id="",
                media=[b"raw file contents"],
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `album_name` but received ''"):
            await async_client.v1.boxes.media.with_raw_response.update_album(
                album_name="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
                media=[b"raw file contents"],
            )
