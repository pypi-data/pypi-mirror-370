"""Provides general application commands for the command line."""

##############################################################################
# Python imports.
from functools import partial
from typing import Callable

##############################################################################
# Textual imports.
from textual.message import Message
from textual.widget import Widget

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import Help, Quit

##############################################################################
# Local imports.
from ...commands import (
    JumpToBookmarks,
    JumpToDocument,
    JumpToHistory,
    JumpToLocalBrowser,
    JumpToTableOfContents,
)
from ...messages import HandleInput
from .base_command import InputCommand


##############################################################################
class GeneralCommand(InputCommand):
    """Base class for general commands."""

    MESSAGE: Callable[[], Message]
    """The message to send for the command."""

    @classmethod
    def handle(cls, text: str, for_widget: Widget) -> bool:
        """Handle the command.

        Args:
            text: The text of the command.
            for_widget: The widget to handle the command for.

        Returns:
            `True` if the command was handled; `False` if not.
        """
        if cls.is_command(text):
            if (message := getattr(cls, "MESSAGE", None)) is not None:
                for_widget.post_message(message())
            return True
        return False


##############################################################################
class BookmarksCommand(GeneralCommand):
    """Jump to the bookmarks"""

    COMMAND = "`bookmarks`"
    ALIASES = "`b`, `bm`"
    MESSAGE = JumpToBookmarks


##############################################################################
class ContentsCommand(GeneralCommand):
    """Jump to the table of contents"""

    COMMAND = "`contents`"
    ALIASES = "`c`, `toc`"
    MESSAGE = JumpToTableOfContents


##############################################################################
class DocumentCommand(GeneralCommand):
    """Jump to the markdown document"""

    COMMAND = "`document`"
    ALIASES = "`d`, `doc`"
    MESSAGE = JumpToDocument


##############################################################################
class HelpCommand(GeneralCommand):
    """Show the help screen"""

    COMMAND = "`help`"
    ALIASES = "`?`"
    MESSAGE = Help


##############################################################################
class HistoryCommand(GeneralCommand):
    """Jump to the browsing history"""

    COMMAND = "`history`"
    ALIASES = "`h`"
    MESSAGE = JumpToHistory


##############################################################################
class LocalCommand(GeneralCommand):
    """Jump to the local file browser"""

    COMMAND = "`local`"
    ALIASES = "`l`"
    MESSAGE = JumpToLocalBrowser


##############################################################################
class QuitCommand(GeneralCommand):
    """Quit the application"""

    COMMAND = "`quit`"
    ALIASES = "`q`"
    MESSAGE = Quit


##############################################################################
class ChangeLogCommand(GeneralCommand):
    """Show Hike's ChangeLog"""

    COMMAND = "`changelog`"
    ALIASES = "`cl`"
    MESSAGE = partial(HandleInput, "github davep hike ChangeLog.md")


##############################################################################
class ReadMeCommand(GeneralCommand):
    """Show Hike's README"""

    COMMAND = "`readme`"
    MESSAGE = partial(HandleInput, "github davep hike")


### general.py ends here
