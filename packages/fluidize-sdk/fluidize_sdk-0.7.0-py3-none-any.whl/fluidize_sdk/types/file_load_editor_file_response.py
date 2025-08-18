# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["FileLoadEditorFileResponse"]


class FileLoadEditorFileResponse(BaseModel):
    filename: str

    language: str

    mime_type: str

    path: str

    size: int
