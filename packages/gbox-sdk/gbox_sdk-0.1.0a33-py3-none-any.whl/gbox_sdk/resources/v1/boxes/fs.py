# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Mapping, cast
from typing_extensions import overload

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven, FileTypes
from ...._utils import extract_files, required_args, maybe_transform, deepcopy_minimal, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v1.boxes import (
    f_info_params,
    f_list_params,
    f_read_params,
    f_write_params,
    f_exists_params,
    f_remove_params,
    f_rename_params,
)
from ....types.v1.boxes.f_info_response import FInfoResponse
from ....types.v1.boxes.f_list_response import FListResponse
from ....types.v1.boxes.f_read_response import FReadResponse
from ....types.v1.boxes.f_write_response import FWriteResponse
from ....types.v1.boxes.f_exists_response import FExistsResponse
from ....types.v1.boxes.f_remove_response import FRemoveResponse
from ....types.v1.boxes.f_rename_response import FRenameResponse

__all__ = ["FsResource", "AsyncFsResource"]


class FsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return FsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return FsResourceWithStreamingResponse(self)

    def list(
        self,
        box_id: str,
        *,
        path: str,
        depth: float | NotGiven = NOT_GIVEN,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FListResponse:
        """
        List box files

        Args:
          path: Target directory path in the box

          depth: Depth of the directory

          working_dir: Working directory. If not provided, the file will be read from the
              `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._get(
            f"/boxes/{box_id}/fs/list",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "path": path,
                        "depth": depth,
                        "working_dir": working_dir,
                    },
                    f_list_params.FListParams,
                ),
            ),
            cast_to=FListResponse,
        )

    def exists(
        self,
        box_id: str,
        *,
        path: str,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FExistsResponse:
        """Check if file/dir exists

        Args:
          path: Target path in the box.

        If the path does not start with '/', the file/directory
              will be checked relative to the working directory

          working_dir: Working directory. If not provided, the file will be read from the
              `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            FExistsResponse,
            self._post(
                f"/boxes/{box_id}/fs/exists",
                body=maybe_transform(
                    {
                        "path": path,
                        "working_dir": working_dir,
                    },
                    f_exists_params.FExistsParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, FExistsResponse),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def info(
        self,
        box_id: str,
        *,
        path: str,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FInfoResponse:
        """Get file/dir

        Args:
          path: Target path in the box.

        If the path does not start with '/', the file/directory
              will be checked relative to the working directory

          working_dir: Working directory. If not provided, the file will be read from the
              `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            FInfoResponse,
            self._get(
                f"/boxes/{box_id}/fs/info",
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    query=maybe_transform(
                        {
                            "path": path,
                            "working_dir": working_dir,
                        },
                        f_info_params.FInfoParams,
                    ),
                ),
                cast_to=cast(Any, FInfoResponse),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def read(
        self,
        box_id: str,
        *,
        path: str,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FReadResponse:
        """Read box file

        Args:
          path: Target path in the box.

        If the path does not start with '/', the file will be
              read from the working directory.

          working_dir: Working directory. If not provided, the file will be read from the
              `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._get(
            f"/boxes/{box_id}/fs/read",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "path": path,
                        "working_dir": working_dir,
                    },
                    f_read_params.FReadParams,
                ),
            ),
            cast_to=FReadResponse,
        )

    def remove(
        self,
        box_id: str,
        *,
        path: str,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FRemoveResponse:
        """Delete a file or dir.

        If target path is not exists, the delete will be failed.

        Args:
          path: Target path in the box. If the path does not start with '/', the file/directory
              will be deleted relative to the working directory. If the target path does not
              exist, the delete will fail.

          working_dir: Working directory. If not provided, the file will be read from the
              `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._delete(
            f"/boxes/{box_id}/fs",
            body=maybe_transform(
                {
                    "path": path,
                    "working_dir": working_dir,
                },
                f_remove_params.FRemoveParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FRemoveResponse,
        )

    def rename(
        self,
        box_id: str,
        *,
        new_path: str,
        old_path: str,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FRenameResponse:
        """Rename a file or dir.

        If target newPath is already exists, the rename will be
        failed.

        Args:
          new_path: New path in the box. If the path does not start with '/', the file/directory
              will be renamed relative to the working directory. If the newPath already
              exists, the rename will fail.

          old_path: Old path in the box. If the path does not start with '/', the file/directory
              will be renamed relative to the working directory. If the oldPath does not
              exist, the rename will fail.

          working_dir: Working directory. If not provided, the file will be read from the
              `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            FRenameResponse,
            self._post(
                f"/boxes/{box_id}/fs/rename",
                body=maybe_transform(
                    {
                        "new_path": new_path,
                        "old_path": old_path,
                        "working_dir": working_dir,
                    },
                    f_rename_params.FRenameParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, FRenameResponse),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    @overload
    def write(
        self,
        box_id: str,
        *,
        content: str,
        path: str,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FWriteResponse:
        """Creates or overwrites a file.

        Creates necessary directories in the path if they
        don't exist. If target path is already exists, the write will be failed.

        Args:
          content: Content of the file (Max size: 512MB)

          path: Target path in the box. If the path does not start with '/', the file will be
              written relative to the working directory. Creates necessary directories in the
              path if they don't exist. If the target path already exists, the write will
              fail.

          working_dir: Working directory. If not provided, the file will be read from the
              `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def write(
        self,
        box_id: str,
        *,
        content: FileTypes,
        path: str,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FWriteResponse:
        """Creates or overwrites a file.

        Creates necessary directories in the path if they
        don't exist. If target path is already exists, the write will be failed.

        Args:
          content: Binary content of the file (Max file size: 512MB)

          path: Target path in the box. If the path does not start with '/', the file will be
              written relative to the working directory. Creates necessary directories in the
              path if they don't exist. If the target path already exists, the write will
              fail.

          working_dir: Working directory. If not provided, the file will be read from the
              `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["content", "path"])
    def write(
        self,
        box_id: str,
        *,
        content: str | FileTypes,
        path: str,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FWriteResponse:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        body = deepcopy_minimal(
            {
                "content": content,
                "path": path,
                "working_dir": working_dir,
            }
        )
        if isinstance(content, str):
            return self._post(
                f"/boxes/{box_id}/fs/write",
                body=maybe_transform(body, f_write_params.FWriteParams),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=FWriteResponse,
            )
        else:
            files = extract_files(cast(Mapping[str, object], body), paths=[["content"]])
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
            return self._post(
                f"/boxes/{box_id}/fs/write",
                body=maybe_transform(body, f_write_params.FWriteParams),
                files=files,
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=FWriteResponse,
            )


class AsyncFsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncFsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return AsyncFsResourceWithStreamingResponse(self)

    async def list(
        self,
        box_id: str,
        *,
        path: str,
        depth: float | NotGiven = NOT_GIVEN,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FListResponse:
        """
        List box files

        Args:
          path: Target directory path in the box

          depth: Depth of the directory

          working_dir: Working directory. If not provided, the file will be read from the
              `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._get(
            f"/boxes/{box_id}/fs/list",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "path": path,
                        "depth": depth,
                        "working_dir": working_dir,
                    },
                    f_list_params.FListParams,
                ),
            ),
            cast_to=FListResponse,
        )

    async def exists(
        self,
        box_id: str,
        *,
        path: str,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FExistsResponse:
        """Check if file/dir exists

        Args:
          path: Target path in the box.

        If the path does not start with '/', the file/directory
              will be checked relative to the working directory

          working_dir: Working directory. If not provided, the file will be read from the
              `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            FExistsResponse,
            await self._post(
                f"/boxes/{box_id}/fs/exists",
                body=await async_maybe_transform(
                    {
                        "path": path,
                        "working_dir": working_dir,
                    },
                    f_exists_params.FExistsParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, FExistsResponse),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def info(
        self,
        box_id: str,
        *,
        path: str,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FInfoResponse:
        """Get file/dir

        Args:
          path: Target path in the box.

        If the path does not start with '/', the file/directory
              will be checked relative to the working directory

          working_dir: Working directory. If not provided, the file will be read from the
              `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            FInfoResponse,
            await self._get(
                f"/boxes/{box_id}/fs/info",
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    query=await async_maybe_transform(
                        {
                            "path": path,
                            "working_dir": working_dir,
                        },
                        f_info_params.FInfoParams,
                    ),
                ),
                cast_to=cast(Any, FInfoResponse),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def read(
        self,
        box_id: str,
        *,
        path: str,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FReadResponse:
        """Read box file

        Args:
          path: Target path in the box.

        If the path does not start with '/', the file will be
              read from the working directory.

          working_dir: Working directory. If not provided, the file will be read from the
              `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._get(
            f"/boxes/{box_id}/fs/read",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "path": path,
                        "working_dir": working_dir,
                    },
                    f_read_params.FReadParams,
                ),
            ),
            cast_to=FReadResponse,
        )

    async def remove(
        self,
        box_id: str,
        *,
        path: str,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FRemoveResponse:
        """Delete a file or dir.

        If target path is not exists, the delete will be failed.

        Args:
          path: Target path in the box. If the path does not start with '/', the file/directory
              will be deleted relative to the working directory. If the target path does not
              exist, the delete will fail.

          working_dir: Working directory. If not provided, the file will be read from the
              `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._delete(
            f"/boxes/{box_id}/fs",
            body=await async_maybe_transform(
                {
                    "path": path,
                    "working_dir": working_dir,
                },
                f_remove_params.FRemoveParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FRemoveResponse,
        )

    async def rename(
        self,
        box_id: str,
        *,
        new_path: str,
        old_path: str,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FRenameResponse:
        """Rename a file or dir.

        If target newPath is already exists, the rename will be
        failed.

        Args:
          new_path: New path in the box. If the path does not start with '/', the file/directory
              will be renamed relative to the working directory. If the newPath already
              exists, the rename will fail.

          old_path: Old path in the box. If the path does not start with '/', the file/directory
              will be renamed relative to the working directory. If the oldPath does not
              exist, the rename will fail.

          working_dir: Working directory. If not provided, the file will be read from the
              `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return cast(
            FRenameResponse,
            await self._post(
                f"/boxes/{box_id}/fs/rename",
                body=await async_maybe_transform(
                    {
                        "new_path": new_path,
                        "old_path": old_path,
                        "working_dir": working_dir,
                    },
                    f_rename_params.FRenameParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, FRenameResponse),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    @overload
    async def write(
        self,
        box_id: str,
        *,
        content: str,
        path: str,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FWriteResponse:
        """Creates or overwrites a file.

        Creates necessary directories in the path if they
        don't exist. If target path is already exists, the write will be failed.

        Args:
          content: Content of the file (Max size: 512MB)

          path: Target path in the box. If the path does not start with '/', the file will be
              written relative to the working directory. Creates necessary directories in the
              path if they don't exist. If the target path already exists, the write will
              fail.

          working_dir: Working directory. If not provided, the file will be read from the
              `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def write(
        self,
        box_id: str,
        *,
        content: FileTypes,
        path: str,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FWriteResponse:
        """Creates or overwrites a file.

        Creates necessary directories in the path if they
        don't exist. If target path is already exists, the write will be failed.

        Args:
          content: Binary content of the file (Max file size: 512MB)

          path: Target path in the box. If the path does not start with '/', the file will be
              written relative to the working directory. Creates necessary directories in the
              path if they don't exist. If the target path already exists, the write will
              fail.

          working_dir: Working directory. If not provided, the file will be read from the
              `box.config.workingDir` directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["content", "path"])
    async def write(
        self,
        box_id: str,
        *,
        content: str | FileTypes,
        path: str,
        working_dir: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FWriteResponse:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        body = deepcopy_minimal(
            {
                "content": content,
                "path": path,
                "working_dir": working_dir,
            }
        )
        if isinstance(content, str):
            return await self._post(
                f"/boxes/{box_id}/fs/write",
                body=await async_maybe_transform(body, f_write_params.FWriteParams),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=FWriteResponse,
            )
        else:
            files = extract_files(cast(Mapping[str, object], body), paths=[["content"]])
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
            return await self._post(
                f"/boxes/{box_id}/fs/write",
                body=await async_maybe_transform(body, f_write_params.FWriteParams),
                files=files,
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=FWriteResponse,
            )


class FsResourceWithRawResponse:
    def __init__(self, fs: FsResource) -> None:
        self._fs = fs

        self.list = to_raw_response_wrapper(
            fs.list,
        )
        self.exists = to_raw_response_wrapper(
            fs.exists,
        )
        self.info = to_raw_response_wrapper(
            fs.info,
        )
        self.read = to_raw_response_wrapper(
            fs.read,
        )
        self.remove = to_raw_response_wrapper(
            fs.remove,
        )
        self.rename = to_raw_response_wrapper(
            fs.rename,
        )
        self.write = to_raw_response_wrapper(
            fs.write,
        )


class AsyncFsResourceWithRawResponse:
    def __init__(self, fs: AsyncFsResource) -> None:
        self._fs = fs

        self.list = async_to_raw_response_wrapper(
            fs.list,
        )
        self.exists = async_to_raw_response_wrapper(
            fs.exists,
        )
        self.info = async_to_raw_response_wrapper(
            fs.info,
        )
        self.read = async_to_raw_response_wrapper(
            fs.read,
        )
        self.remove = async_to_raw_response_wrapper(
            fs.remove,
        )
        self.rename = async_to_raw_response_wrapper(
            fs.rename,
        )
        self.write = async_to_raw_response_wrapper(
            fs.write,
        )


class FsResourceWithStreamingResponse:
    def __init__(self, fs: FsResource) -> None:
        self._fs = fs

        self.list = to_streamed_response_wrapper(
            fs.list,
        )
        self.exists = to_streamed_response_wrapper(
            fs.exists,
        )
        self.info = to_streamed_response_wrapper(
            fs.info,
        )
        self.read = to_streamed_response_wrapper(
            fs.read,
        )
        self.remove = to_streamed_response_wrapper(
            fs.remove,
        )
        self.rename = to_streamed_response_wrapper(
            fs.rename,
        )
        self.write = to_streamed_response_wrapper(
            fs.write,
        )


class AsyncFsResourceWithStreamingResponse:
    def __init__(self, fs: AsyncFsResource) -> None:
        self._fs = fs

        self.list = async_to_streamed_response_wrapper(
            fs.list,
        )
        self.exists = async_to_streamed_response_wrapper(
            fs.exists,
        )
        self.info = async_to_streamed_response_wrapper(
            fs.info,
        )
        self.read = async_to_streamed_response_wrapper(
            fs.read,
        )
        self.remove = async_to_streamed_response_wrapper(
            fs.remove,
        )
        self.rename = async_to_streamed_response_wrapper(
            fs.rename,
        )
        self.write = async_to_streamed_response_wrapper(
            fs.write,
        )
