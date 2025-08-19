import mimetypes
from io import IOBase
from pathlib import Path
from typing import Union, IO

from pydantic import BaseModel, validator

from .basemodel import APIBaseModel


class NoResponse(APIBaseModel):
    """Represents a model for no API response."""

    pass


class FilePayload(BaseModel):
    """
    Represents a file payload for handling file uploads.
    """

    filename: str
    content_type: str
    content: Union[bytes, IO, IOBase]

    class Config:
        arbitrary_types_allowed = True

    @validator("content", pre=True)
    def validate_content(cls, v):
        if isinstance(v, (bytes, IOBase)):
            return v
        raise ValueError("Content must be bytes or a file-like object (IOBase)")

    @classmethod
    def from_path(
        cls, path: Union[str, Path], content_type: str = None
    ) -> "FilePayload":
        """
        Creates a FilePayload instance from a file path.
        :param path:         The path to the file to be loaded.
        :param content_type: The content type of the file. If not provided, it
                             will be guessed based on the file extension.
        :return:             A FilePayload instance with the file information.
        """
        if not content_type:
            content_type = mimetypes.guess_type(path)[0] or "application/octet-stream"

        p = Path(path)
        return cls(filename=p.name, content_type=content_type, content=open(p, "rb"))
