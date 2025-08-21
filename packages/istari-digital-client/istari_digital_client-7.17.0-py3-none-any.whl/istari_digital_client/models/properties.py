import abc
from functools import cached_property
from pathlib import Path

import istari_digital_core


class Properties:
    """
    Class for holding file properties.

    Properties represent metadata about a file — information that describes the file,
    such as its name, size, extension, and other attributes, but not its actual content.

    These properties are typically stored in the filesystem or metadata layers and are
    exposed by Istari's core API.
    """

    def __init__(self, native: istari_digital_core.Properties) -> None:
        self.native: istari_digital_core.Properties = native

    @cached_property
    def name(self) -> str:
        """
        Return the full name of the file, including the extension.

        This is reconstructed from the file name and its extension. If the file name
        already ends with the correct extension (case-insensitive), it is returned
        directly. Otherwise, the extension is appended.

        Examples:
            >>> x.name
            "foo.JPG"
            >>> x.stem
            "foo"
            >>> x.extension
            "jpg"
            >>> x.suffix
            ".JPG"
        """
        file_name = str(self.native.file_name)
        if file_name.lower().endswith(f".{self.extension}"):
            return file_name
        return ".".join([file_name, self.extension])

    @cached_property
    def stem(self) -> str:
        """
        Return the stem of the file name, excluding its suffix.

        This is the name without the extension. Equivalent to `Path(name).stem`.

        Examples:
            >>> x.name
            "foo.jpg"
            >>> x.stem
        """
        return Path(self.name).stem

    @property
    def size(self) -> int:
        """
        Return the size of the file in bytes.
        """
        return self.native.size

    @property
    def mime_type(self) -> str:
        """
        Return the MIME type of the file, if known.

        Examples include 'application/pdf', 'image/jpeg', etc.
        """
        return str(self.native.mime)

    @cached_property
    def suffix(self) -> str:
        """
        Return the suffix (extension with dot) from the file name.

        Preserves original casing and includes the dot prefix.

        Examples:
            >>> x.name
            "foo.JPG"
            >>> x.suffix
            ".JPG"
        """
        return Path(self.name).suffix

    @property
    def extension(self: "Properties") -> str:
        """
        Return the lowercase file extension, without the dot.

        Examples:
            >>> x.extension
            "jpg"
            >>> x.name
            "foo.JPG"
        """
        return self.native.extension.lower()

    @property
    def description(self) -> str | None:
        """
        Return the file's description, if one was set.

        Returns None if the description is not set.
        """

        return self.native.description or None

    @property
    def version_name(self) -> str | None:
        """
        Return the version name for this file, if available.

        Returns None if no version name was provided.
        """

        return self.native.version_name or None

    @property
    def external_identifier(self) -> str | None:
        """
        Return the external identifier, if set.

        Returns None if no external identifier is set.
        """
        return self.native.external_identifier or None

    @property
    def display_name(self) -> str | None:
        """
        Return the human-readable display name for the file, if set.

        Returns None if no display name is assigned.
        """
        return self.native.display_name or None


class PropertiesHaving(abc.ABC):
    """
    Abstract base class for objects that expose file-like properties.

    Any implementing class must provide a `properties` attribute,
    which provides access to the full `Properties` object.
    """
    @property
    @abc.abstractmethod
    def properties(self) -> "Properties": ...

    @property
    def extension(self) -> str:
        """
        Shortcut for accessing the file extension.
        """
        return self.properties.extension

    @property
    def name(self) -> str:
        """
        Shortcut for accessing the full file name.
        """
        return self.properties.name

    @property
    def stem(self) -> str:
        """
        Shortcut for accessing the file stem (name without extension).
        """
        return self.properties.stem

    @property
    def description(self) -> str | None:
        """
        Shortcut for accessing the file description.
        """
        return self.properties.description

    @property
    def size(self) -> int:
        """
        Shortcut for accessing the file size in bytes.
        """
        return self.properties.size

    @property
    def mime_type(self) -> str:
        """
        Shortcut for accessing the file MIME type.
        """
        return self.properties.mime_type

    @property
    def version_name(self) -> str | None:
        """
        Shortcut for accessing the version name.
        """
        return self.properties.version_name

    @property
    def external_identifier(self) -> str | None:
        """
        Shortcut for accessing the external identifier.
        """
        return self.properties.external_identifier

    @property
    def display_name(self) -> str | None:
        """
        Shortcut for accessing the display name.
        """
        return self.properties.display_name
