# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v1.boxes import storage_presigned_url_params

__all__ = ["StorageResource", "AsyncStorageResource"]


class StorageResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> StorageResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return StorageResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StorageResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return StorageResourceWithStreamingResponse(self)

    def presigned_url(
        self,
        box_id: str,
        *,
        storage_key: str,
        expires_in: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """Create a presigned url for a storage key.

        This endpoint provides a presigned url
        for a storage key, which can be used to download the file from the storage.

        Args:
          storage_key: Storage key

          expires_in: Presigned url expires in

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m Maximum allowed: 6h

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/storage/presigned-url",
            body=maybe_transform(
                {
                    "storage_key": storage_key,
                    "expires_in": expires_in,
                },
                storage_presigned_url_params.StoragePresignedURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )


class AsyncStorageResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncStorageResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncStorageResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStorageResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return AsyncStorageResourceWithStreamingResponse(self)

    async def presigned_url(
        self,
        box_id: str,
        *,
        storage_key: str,
        expires_in: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """Create a presigned url for a storage key.

        This endpoint provides a presigned url
        for a storage key, which can be used to download the file from the storage.

        Args:
          storage_key: Storage key

          expires_in: Presigned url expires in

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m Maximum allowed: 6h

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/storage/presigned-url",
            body=await async_maybe_transform(
                {
                    "storage_key": storage_key,
                    "expires_in": expires_in,
                },
                storage_presigned_url_params.StoragePresignedURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )


class StorageResourceWithRawResponse:
    def __init__(self, storage: StorageResource) -> None:
        self._storage = storage

        self.presigned_url = to_raw_response_wrapper(
            storage.presigned_url,
        )


class AsyncStorageResourceWithRawResponse:
    def __init__(self, storage: AsyncStorageResource) -> None:
        self._storage = storage

        self.presigned_url = async_to_raw_response_wrapper(
            storage.presigned_url,
        )


class StorageResourceWithStreamingResponse:
    def __init__(self, storage: StorageResource) -> None:
        self._storage = storage

        self.presigned_url = to_streamed_response_wrapper(
            storage.presigned_url,
        )


class AsyncStorageResourceWithStreamingResponse:
    def __init__(self, storage: AsyncStorageResource) -> None:
        self._storage = storage

        self.presigned_url = async_to_streamed_response_wrapper(
            storage.presigned_url,
        )
