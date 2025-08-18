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
from ....types.v1.boxes import browser_cdp_url_params, browser_open_tab_params, browser_update_tab_params
from ....types.v1.boxes.browser_get_tabs_response import BrowserGetTabsResponse
from ....types.v1.boxes.browser_open_tab_response import BrowserOpenTabResponse
from ....types.v1.boxes.browser_close_tab_response import BrowserCloseTabResponse
from ....types.v1.boxes.browser_switch_tab_response import BrowserSwitchTabResponse
from ....types.v1.boxes.browser_update_tab_response import BrowserUpdateTabResponse

__all__ = ["BrowserResource", "AsyncBrowserResource"]


class BrowserResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BrowserResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return BrowserResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BrowserResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return BrowserResourceWithStreamingResponse(self)

    def cdp_url(
        self,
        box_id: str,
        *,
        expires_in: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        This endpoint allows you to generate a pre-signed URL for accessing the Chrome
        DevTools Protocol (CDP) of a running box. The URL is valid for a limited time
        and can be used to interact with the box's browser environment

        Args:
          expires_in: The CDP url will be alive for the given duration

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 120m

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/browser/connect-url/cdp",
            body=maybe_transform({"expires_in": expires_in}, browser_cdp_url_params.BrowserCdpURLParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )

    def close_tab(
        self,
        tab_id: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserCloseTabResponse:
        """Close a specific browser tab identified by its id.

        This endpoint will
        permanently close the tab and free up the associated resources. After closing a
        tab, the ids of subsequent tabs may change.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not tab_id:
            raise ValueError(f"Expected a non-empty value for `tab_id` but received {tab_id!r}")
        return self._delete(
            f"/boxes/{box_id}/browser/tabs/{tab_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserCloseTabResponse,
        )

    def get_tabs(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserGetTabsResponse:
        """
        Retrieve a comprehensive list of all currently open browser tabs in the
        specified box. This endpoint returns detailed information about each tab
        including its id, title, current URL, and favicon. The returned id can be used
        for subsequent operations like navigation, closing, or updating tabs. This is
        essential for managing multiple browser sessions and understanding the current
        state of the browser environment.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._get(
            f"/boxes/{box_id}/browser/tabs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserGetTabsResponse,
        )

    def open_tab(
        self,
        box_id: str,
        *,
        url: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserOpenTabResponse:
        """Create and open a new browser tab with the specified URL.

        This endpoint will
        navigate to the provided URL and return the new tab's information including its
        assigned id, loaded title, final URL (after any redirects), and favicon. The
        returned tab id can be used for future operations on this specific tab. The
        browser will attempt to load the page and will wait for the DOM content to be
        loaded before returning the response. If the URL is invalid or unreachable, an
        error will be returned.

        Args:
          url: The tab url

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/browser/tabs",
            body=maybe_transform({"url": url}, browser_open_tab_params.BrowserOpenTabParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserOpenTabResponse,
        )

    def switch_tab(
        self,
        tab_id: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserSwitchTabResponse:
        """
        Switch to a specific browser tab by bringing it to the foreground (making it the
        active/frontmost tab). This operation sets the specified tab as the currently
        active tab without changing its URL or content. The tab will receive focus and
        become visible to the user. This is useful for managing multiple browser
        sessions and controlling which tab is currently in focus.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not tab_id:
            raise ValueError(f"Expected a non-empty value for `tab_id` but received {tab_id!r}")
        return self._post(
            f"/boxes/{box_id}/browser/tabs/{tab_id}/switch",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserSwitchTabResponse,
        )

    def update_tab(
        self,
        tab_id: str,
        *,
        box_id: str,
        url: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserUpdateTabResponse:
        """Navigate an existing browser tab to a new URL.

        This endpoint updates the
        specified tab by navigating it to the provided URL and returns the updated tab
        information. The browser will wait for the DOM content to be loaded before
        returning the response. If the navigation fails due to an invalid URL or network
        issues, an error will be returned. The updated tab information will include the
        new title, final URL (after any redirects), and favicon from the new page.

        Args:
          url: The tab new url

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not tab_id:
            raise ValueError(f"Expected a non-empty value for `tab_id` but received {tab_id!r}")
        return self._put(
            f"/boxes/{box_id}/browser/tabs/{tab_id}",
            body=maybe_transform({"url": url}, browser_update_tab_params.BrowserUpdateTabParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserUpdateTabResponse,
        )


class AsyncBrowserResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBrowserResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncBrowserResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBrowserResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return AsyncBrowserResourceWithStreamingResponse(self)

    async def cdp_url(
        self,
        box_id: str,
        *,
        expires_in: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        This endpoint allows you to generate a pre-signed URL for accessing the Chrome
        DevTools Protocol (CDP) of a running box. The URL is valid for a limited time
        and can be used to interact with the box's browser environment

        Args:
          expires_in: The CDP url will be alive for the given duration

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 120m

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/browser/connect-url/cdp",
            body=await async_maybe_transform({"expires_in": expires_in}, browser_cdp_url_params.BrowserCdpURLParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )

    async def close_tab(
        self,
        tab_id: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserCloseTabResponse:
        """Close a specific browser tab identified by its id.

        This endpoint will
        permanently close the tab and free up the associated resources. After closing a
        tab, the ids of subsequent tabs may change.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not tab_id:
            raise ValueError(f"Expected a non-empty value for `tab_id` but received {tab_id!r}")
        return await self._delete(
            f"/boxes/{box_id}/browser/tabs/{tab_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserCloseTabResponse,
        )

    async def get_tabs(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserGetTabsResponse:
        """
        Retrieve a comprehensive list of all currently open browser tabs in the
        specified box. This endpoint returns detailed information about each tab
        including its id, title, current URL, and favicon. The returned id can be used
        for subsequent operations like navigation, closing, or updating tabs. This is
        essential for managing multiple browser sessions and understanding the current
        state of the browser environment.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._get(
            f"/boxes/{box_id}/browser/tabs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserGetTabsResponse,
        )

    async def open_tab(
        self,
        box_id: str,
        *,
        url: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserOpenTabResponse:
        """Create and open a new browser tab with the specified URL.

        This endpoint will
        navigate to the provided URL and return the new tab's information including its
        assigned id, loaded title, final URL (after any redirects), and favicon. The
        returned tab id can be used for future operations on this specific tab. The
        browser will attempt to load the page and will wait for the DOM content to be
        loaded before returning the response. If the URL is invalid or unreachable, an
        error will be returned.

        Args:
          url: The tab url

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/browser/tabs",
            body=await async_maybe_transform({"url": url}, browser_open_tab_params.BrowserOpenTabParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserOpenTabResponse,
        )

    async def switch_tab(
        self,
        tab_id: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserSwitchTabResponse:
        """
        Switch to a specific browser tab by bringing it to the foreground (making it the
        active/frontmost tab). This operation sets the specified tab as the currently
        active tab without changing its URL or content. The tab will receive focus and
        become visible to the user. This is useful for managing multiple browser
        sessions and controlling which tab is currently in focus.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not tab_id:
            raise ValueError(f"Expected a non-empty value for `tab_id` but received {tab_id!r}")
        return await self._post(
            f"/boxes/{box_id}/browser/tabs/{tab_id}/switch",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserSwitchTabResponse,
        )

    async def update_tab(
        self,
        tab_id: str,
        *,
        box_id: str,
        url: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserUpdateTabResponse:
        """Navigate an existing browser tab to a new URL.

        This endpoint updates the
        specified tab by navigating it to the provided URL and returns the updated tab
        information. The browser will wait for the DOM content to be loaded before
        returning the response. If the navigation fails due to an invalid URL or network
        issues, an error will be returned. The updated tab information will include the
        new title, final URL (after any redirects), and favicon from the new page.

        Args:
          url: The tab new url

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not tab_id:
            raise ValueError(f"Expected a non-empty value for `tab_id` but received {tab_id!r}")
        return await self._put(
            f"/boxes/{box_id}/browser/tabs/{tab_id}",
            body=await async_maybe_transform({"url": url}, browser_update_tab_params.BrowserUpdateTabParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserUpdateTabResponse,
        )


class BrowserResourceWithRawResponse:
    def __init__(self, browser: BrowserResource) -> None:
        self._browser = browser

        self.cdp_url = to_raw_response_wrapper(
            browser.cdp_url,
        )
        self.close_tab = to_raw_response_wrapper(
            browser.close_tab,
        )
        self.get_tabs = to_raw_response_wrapper(
            browser.get_tabs,
        )
        self.open_tab = to_raw_response_wrapper(
            browser.open_tab,
        )
        self.switch_tab = to_raw_response_wrapper(
            browser.switch_tab,
        )
        self.update_tab = to_raw_response_wrapper(
            browser.update_tab,
        )


class AsyncBrowserResourceWithRawResponse:
    def __init__(self, browser: AsyncBrowserResource) -> None:
        self._browser = browser

        self.cdp_url = async_to_raw_response_wrapper(
            browser.cdp_url,
        )
        self.close_tab = async_to_raw_response_wrapper(
            browser.close_tab,
        )
        self.get_tabs = async_to_raw_response_wrapper(
            browser.get_tabs,
        )
        self.open_tab = async_to_raw_response_wrapper(
            browser.open_tab,
        )
        self.switch_tab = async_to_raw_response_wrapper(
            browser.switch_tab,
        )
        self.update_tab = async_to_raw_response_wrapper(
            browser.update_tab,
        )


class BrowserResourceWithStreamingResponse:
    def __init__(self, browser: BrowserResource) -> None:
        self._browser = browser

        self.cdp_url = to_streamed_response_wrapper(
            browser.cdp_url,
        )
        self.close_tab = to_streamed_response_wrapper(
            browser.close_tab,
        )
        self.get_tabs = to_streamed_response_wrapper(
            browser.get_tabs,
        )
        self.open_tab = to_streamed_response_wrapper(
            browser.open_tab,
        )
        self.switch_tab = to_streamed_response_wrapper(
            browser.switch_tab,
        )
        self.update_tab = to_streamed_response_wrapper(
            browser.update_tab,
        )


class AsyncBrowserResourceWithStreamingResponse:
    def __init__(self, browser: AsyncBrowserResource) -> None:
        self._browser = browser

        self.cdp_url = async_to_streamed_response_wrapper(
            browser.cdp_url,
        )
        self.close_tab = async_to_streamed_response_wrapper(
            browser.close_tab,
        )
        self.get_tabs = async_to_streamed_response_wrapper(
            browser.get_tabs,
        )
        self.open_tab = async_to_streamed_response_wrapper(
            browser.open_tab,
        )
        self.switch_tab = async_to_streamed_response_wrapper(
            browser.switch_tab,
        )
        self.update_tab = async_to_streamed_response_wrapper(
            browser.update_tab,
        )
