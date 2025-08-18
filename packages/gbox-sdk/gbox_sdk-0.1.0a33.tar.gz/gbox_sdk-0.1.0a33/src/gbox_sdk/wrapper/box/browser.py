from typing_extensions import List

from gbox_sdk._client import GboxClient
from gbox_sdk.types.v1.boxes.browser_get_tabs_response import Data, BrowserGetTabsResponse
from gbox_sdk.types.v1.boxes.browser_open_tab_response import BrowserOpenTabResponse
from gbox_sdk.types.v1.boxes.browser_close_tab_response import BrowserCloseTabResponse
from gbox_sdk.types.v1.boxes.browser_switch_tab_response import BrowserSwitchTabResponse
from gbox_sdk.types.v1.boxes.browser_update_tab_response import BrowserUpdateTabResponse


class BrowserOperator:
    """
    Provides operations related to browser management for a specific box.

    Args:
        client (GboxClient): The GboxClient instance used to interact with the API.
        box_id (str): The unique identifier of the box.
    """

    def __init__(self, client: GboxClient, box_id: str):
        """
        Initialize a BrowserOperator instance.

        Args:
            client (GboxClient): The GboxClient instance used to interact with the API.
            box_id (str): The unique identifier of the box.
        """
        self.client = client
        self.box_id = box_id

    def cdp_url(self) -> str:
        """
        Get the Chrome DevTools Protocol (CDP) URL for the browser in the specified box.

        Returns:
            str: The CDP URL for the browser.

        Example:
            >>> box.browser.cdp_url()
        """
        return self.client.v1.boxes.browser.cdp_url(box_id=self.box_id)

    def list_tab(self) -> List["BrowserTabOperator"]:
        """
        Retrieve a comprehensive list of all currently open browser tabs in the
        specified box. This endpoint returns detailed information about each tab
        including its id, title, current URL, and favicon. The returned id can be used
        for subsequent operations like navigation, closing, or updating tabs. This is
        essential for managing multiple browser sessions and understanding the current
        state of the browser environment.

        Returns:
            list: A list of tab objects. BrowserTabOperator

        Example:
            >>> box.browser.list_tab()
        """
        tab_info = self.client.v1.boxes.browser.get_tabs(box_id=self.box_id)
        return [BrowserTabOperator(client=self.client, box_id=self.box_id, data=tab) for tab in tab_info.data]

    def list_tab_info(self) -> BrowserGetTabsResponse:
        """
        Retrieve a comprehensive list of all currently open browser tabs in the
        specified box. This endpoint returns detailed information about each tab
        including its id, title, current URL, and favicon. The returned id can be used
        for subsequent operations like navigation, closing, or updating tabs. This is
        essential for managing multiple browser sessions and understanding the current
        state of the browser environment.

        Returns:
            BrowserGetTabsResponse: The list of tab information.

        Example:
            >>> box.browser.list_tab_info()
        """
        return self.client.v1.boxes.browser.get_tabs(box_id=self.box_id)

    def update_tab(self, *, tab_id: str, url: str) -> BrowserUpdateTabResponse:
        """
        Navigate an existing browser tab to a new URL.

        This endpoint updates the
        specified tab by navigating it to the provided URL and returns the updated tab
        information. The browser will wait for the DOM content to be loaded before
        returning the response. If the navigation fails due to an invalid URL or network
        issues, an error will be returned. The updated tab information will include the
        new title, final URL (after any redirects), and favicon from the new page.

        Args:
            tab_id: The tab id
            url: The tab new url

        Example:
            >>> box.browser.update_tab(tab_id="1", url="https://www.google.com")
        """
        return self.client.v1.boxes.browser.update_tab(tab_id=tab_id, box_id=self.box_id, url=url)

    def close_tab(self, tab_id: str) -> BrowserCloseTabResponse:
        """
        Close a specific browser tab identified by its id.

        This endpoint will
        permanently close the tab and free up the associated resources. After closing a
        tab, the ids of subsequent tabs may change.

        Args:
            tab_id: The tab id

        Example:
            >>> box.browser.close_tab("1")
        """
        return self.client.v1.boxes.browser.close_tab(tab_id=tab_id, box_id=self.box_id)

    def switch_tab(self, tab_id: str) -> BrowserSwitchTabResponse:
        """
        Switch to a specific browser tab by bringing it to the foreground (making it the
        active/frontmost tab). This operation sets the specified tab as the currently
        active tab without changing its URL or content. The tab will receive focus and
        become visible to the user. This is useful for managing multiple browser
        sessions and controlling which tab is currently in focus.

        Args:
            tab_id: The tab id

        Example:
            >>> box.browser.switch_tab("1")
        """
        return self.client.v1.boxes.browser.switch_tab(tab_id=tab_id, box_id=self.box_id)

    def open_tab(self, url: str) -> BrowserOpenTabResponse:
        """
        Create and open a new browser tab with the specified URL.

        This endpoint will
        navigate to the provided URL and return the new tab's information including its
        assigned id, loaded title, final URL (after any redirects), and favicon. The
        returned tab id can be used for future operations on this specific tab. The
        browser will attempt to load the page and will wait for the DOM content to be
        loaded before returning the response. If the URL is invalid or unreachable, an
        error will be returned.

        Args:
          url: The tab url

        Example:
            >>> box.browser.open_tab("https://www.google.com")
        """
        return self.client.v1.boxes.browser.open_tab(url=url, box_id=self.box_id)


class BrowserTabOperator:
    """
    Provides operations related to browser tabs for a specific box.

    Args:
        client (GboxClient): The GboxClient instance used to interact with the API.
        box_id (str): The unique identifier of the box.
    """

    def __init__(self, *, client: GboxClient, box_id: str, data: Data):
        self.client = client
        self.box_id = box_id
        self.data = data

    def update(self, url: str) -> BrowserUpdateTabResponse:
        """
        Navigate an existing browser tab to a new URL.

        This endpoint updates the
        specified tab by navigating it to the provided URL and returns the updated tab
        information. The browser will wait for the DOM content to be loaded before
        returning the response. If the navigation fails due to an invalid URL or network
        issues, an error will be returned. The updated tab information will include the
        new title, final URL (after any redirects), and favicon from the new page.

        Args:
            url: The tab new url

        Returns:
            BrowserUpdateTabResponse: The updated tab information.

        Example:
            >>> box.browser.tab.update("https://www.google.com")
        """
        return self.client.v1.boxes.browser.update_tab(tab_id=self.data.id, box_id=self.box_id, url=url)
