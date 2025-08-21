import os
import abc
import json
from typing import TypeAlias, Union
from pathlib import Path

from istari_digital_client.log_utils import log_method

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
PathLike = Union[str, os.PathLike, Path]


class Readable(abc.ABC):
    """
    Abstract base class for objects that expose readable file-like content.

    This interface provides convenient methods for accessing raw bytes, text content,
    JSON data, and for copying contents to a local path.
    """
    @abc.abstractmethod
    def read_bytes(self) -> bytes:
        """
        Read the contents as raw bytes.

        This method must be implemented by subclasses to define how the byte content
        is retrieved.
        """
        ...

    @log_method
    def read_text(self, encoding: str = "utf-8") -> str:
        """
        Read the contents as decoded text.

        :param encoding: Text encoding to use. Defaults to "utf-8".
        :raises UnicodeDecodeError: If the byte content cannot be decoded.
        """
        return self.read_bytes().decode(encoding)

    @log_method
    def copy_to(self, dest: PathLike) -> Path:
        """
        Copy the contents to a local file.

        :param dest: Path to write the file to. This can be a string, Path, or os.PathLike.
        :raises OSError: If the file cannot be written.
        """
        dest_path = Path(str(dest))
        dest_path.write_bytes(self.read_bytes())
        return dest_path

    @log_method
    def read_json(self, encoding: str = "utf-8") -> JSON:
        """
        Parse the contents as JSON.

        :param encoding: Text encoding to use when decoding the content. Defaults to "utf-8".
        :raises UnicodeDecodeError: If the byte content cannot be decoded.
        :raises json.JSONDecodeError: If the decoded content is not valid JSON.
        """
        return json.loads(self.read_text(encoding=encoding))
