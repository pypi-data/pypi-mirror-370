"""Provides code for holding, saving and loading bookmarks."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass
from functools import total_ordering
from json import dumps, loads
from pathlib import Path
from typing import TypeAlias

##############################################################################
# httpx imports.
from httpx import URL

##############################################################################
# Local imports.
from ..types import HikeLocation
from .locations import data_dir


##############################################################################
@dataclass(frozen=True)
@total_ordering
class Bookmark:
    """A Hike bookmark."""

    title: str
    """The bookmark's title."""

    location: HikeLocation
    """The location of the bookmark."""

    @classmethod
    def from_json(cls, data: dict[str, str]) -> Bookmark:
        """Load a bookmark from some JSON data.

        Args:
            data: The data to load from.

        Returns:
            A fresh instance of a bookmark.
        """
        location_type = data.get("type", "path")
        return cls(
            data.get("title", ""),
            (URL if location_type == "url" else Path)(data.get("location", "")),
        )

    @property
    def as_json(self) -> dict[str, str]:
        """The bookmark in a JSON-friendly format."""
        return {
            "title": self.title,
            "type": "url" if isinstance(self.location, URL) else "path",
            "location": str(self.location),
        }

    def __gt__(self, value: object, /) -> bool:
        if isinstance(value, Bookmark):
            return self.title.casefold() > value.title.casefold()
        raise NotImplementedError

    def __eq__(self, value: object, /) -> bool:
        if isinstance(value, Bookmark):
            return self.title.casefold() == value.title.casefold()
        if isinstance(value, str):
            return self.title.casefold() == value.casefold()
        if isinstance(value, Path):
            return isinstance(self.location, Path) and self.location == value
        if isinstance(value, URL):
            return isinstance(self.location, URL) and self.location == value
        raise NotImplementedError


##############################################################################
Bookmarks: TypeAlias = list[Bookmark]
"""The type for a collection of bookmarks."""


##############################################################################
def bookmarks_file() -> Path:
    """The path of the bookmarks file.

    Returns:
        The path for the bookmarks file.
    """
    return data_dir() / "bookmarks.json"


##############################################################################
def save_bookmarks(bookmarks: Bookmarks) -> None:
    """Save the bookmarks to storage.

    Args:
        bookmarks: The bookmarks to save.
    """
    bookmarks_file().write_text(
        dumps([bookmark.as_json for bookmark in bookmarks], indent=4), encoding="utf-8"
    )


##############################################################################
def load_bookmarks() -> Bookmarks:
    """Load bookmarks from storage.

    Returns:
        The bookmarks.
    """
    return (
        [
            Bookmark.from_json(data)
            for data in loads(bookmarks_file().read_text(encoding="utf-8"))
        ]
        if bookmarks_file().exists()
        else []
    )


### bookmarks.py ends here
