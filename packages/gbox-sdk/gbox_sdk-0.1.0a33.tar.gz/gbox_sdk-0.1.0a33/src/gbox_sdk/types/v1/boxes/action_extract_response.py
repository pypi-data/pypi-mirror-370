# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict

from ...._models import BaseModel

__all__ = ["ActionExtractResponse"]


class ActionExtractResponse(BaseModel):
    data: Dict[str, object]
    """The extracted data structure that conforms to the provided JSON schema.

    The actual structure and content depend on the schema defined in the extract
    action request.
    """

    screenshot: str
    """Base64-encoded screenshot of the UI interface at the time of extraction"""
