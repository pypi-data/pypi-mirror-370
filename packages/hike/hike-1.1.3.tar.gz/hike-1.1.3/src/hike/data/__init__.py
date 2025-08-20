"""Provides functions and classes for managing the app's data."""

##############################################################################
# Local imports.
from .bookmarks import Bookmark, Bookmarks, load_bookmarks, save_bookmarks
from .command_history import load_command_history, save_command_history
from .config import (
    Configuration,
    load_configuration,
    save_configuration,
    update_configuration,
)
from .history import load_history, save_history
from .location_types import is_editable, looks_urllike, maybe_markdown

##############################################################################
# Exports.
__all__ = [
    "Bookmark",
    "Bookmarks",
    "Configuration",
    "is_editable",
    "load_bookmarks",
    "load_command_history",
    "load_configuration",
    "load_history",
    "looks_urllike",
    "maybe_markdown",
    "save_bookmarks",
    "save_command_history",
    "save_configuration",
    "save_history",
    "update_configuration",
]

### __init__.py ends here
