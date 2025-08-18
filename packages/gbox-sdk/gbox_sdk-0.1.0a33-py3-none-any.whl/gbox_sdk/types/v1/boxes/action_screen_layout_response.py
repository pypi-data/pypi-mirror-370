# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["ActionScreenLayoutResponse"]


class ActionScreenLayoutResponse(BaseModel):
    content: str
    """Screen layout content.

    Android boxes (XML):

    ```xml
    <?xml version='1.0' encoding='UTF-8' standalone='yes'?>
    <hierarchy rotation="0">
      <node ... />
    </hierarchy>
    ```

    Browser (Linux) boxes (HTML):

    ```html
    <html>
      <head>
        <title>Example</title>
      </head>
      <body>
        <h1>Hello World</h1>
      </body>
    </html>
    ```
    """
