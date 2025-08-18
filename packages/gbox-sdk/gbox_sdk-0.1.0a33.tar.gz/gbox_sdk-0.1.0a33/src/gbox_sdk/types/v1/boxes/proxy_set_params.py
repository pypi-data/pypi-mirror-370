# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, TypedDict

__all__ = ["ProxySetParams", "Auth"]


class ProxySetParams(TypedDict, total=False):
    auth: Required[Auth]
    """Box Proxy Auth"""

    excludes: Required[List[str]]
    """Exclude IPs from the proxy. Default is ['127.0.0.1', 'localhost']"""

    url: Required[str]
    """Proxy URL"""


class Auth(TypedDict, total=False):
    password: Required[str]
    """Password for the proxy"""

    username: Required[str]
    """Username for the proxy"""
