# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["AndroidGetConnectAddressResponse"]


class AndroidGetConnectAddressResponse(BaseModel):
    adb: str
    """Android adb connect address.

    use `adb connect <adbConnectAddress>` to connect to the Android device
    """
