"""Provides the command palette command provides for the application."""

##############################################################################
# Local imports.
from .bookmarks import BookmarkCommands
from .history import HistoryCommands
from .main import MainCommands

##############################################################################
# Exports.
__all__ = [
    "BookmarkCommands",
    "HistoryCommands",
    "MainCommands",
]

### __init__.py ends here
