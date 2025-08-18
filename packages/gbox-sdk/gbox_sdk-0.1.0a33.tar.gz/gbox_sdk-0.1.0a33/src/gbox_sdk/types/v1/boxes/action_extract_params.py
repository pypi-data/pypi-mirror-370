# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ActionExtractParams"]


class ActionExtractParams(TypedDict, total=False):
    instruction: Required[str]
    """The instruction of the action to extract data from the UI interface"""

    schema: object
    """JSON Schema defining the structure of data to extract.

    Supports object, array, string, number, boolean types with validation rules.

    Common use cases:

    - Extract text content: { "type": "string" }
    - Extract structured data: { "type": "object", "properties": {...} }
    - Extract lists: { "type": "array", "items": {...} }
    - Extract with validation: Add constraints like "required", "enum", "pattern",
      etc.
    """
