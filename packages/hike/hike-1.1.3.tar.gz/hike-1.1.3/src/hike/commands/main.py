"""Main commands for the application."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import Command


##############################################################################
class ToggleNavigation(Command):
    """Show/hide the navigation panel"""

    BINDING_KEY = "f2"
    SHOW_IN_FOOTER = True
    FOOTER_TEXT = "Nav"


##############################################################################
class ChangeNavigationSide(Command):
    """Change which side the navigation panel lives on"""

    BINDING_KEY = "shift+f2"


##############################################################################
class JumpToCommandLine(Command):
    """Jump to the command line"""

    BINDING_KEY = "/"


##############################################################################
class JumpToDocument(Command):
    """Jump to the markdown document"""

    BINDING_KEY = "ctrl+slash, ctrl+g"


##############################################################################
class ChangeCommandLineLocation(Command):
    """Swap the position of the command line between top and bottom"""

    BINDING_KEY = "ctrl+up, ctrl+down"


##############################################################################
class BookmarkLocation(Command):
    """Bookmark the current location"""

    BINDING_KEY = "ctrl+b"


##############################################################################
class Reload(Command):
    """Reload the current document"""

    BINDING_KEY = "ctrl+r"


##############################################################################
class SearchBookmarks(Command):
    """Search the bookmarks"""

    BINDING_KEY = "f3"


##############################################################################
class SearchHistory(Command):
    """Search the history"""

    BINDING_KEY = "shift+f3"


##############################################################################
class CopyLocationToClipboard(Command):
    """Copy the location to the clipboard"""

    BINDING_KEY = "f4"


##############################################################################
class CopyMarkdownToClipboard(Command):
    """Copy the Markdown source to the clipboard"""

    BINDING_KEY = "shift+f4"


##############################################################################
class Edit(Command):
    """Edit the current markdown document"""

    BINDING_KEY = "f5"
    SHOW_IN_FOOTER = True


##############################################################################
class SaveCopy(Command):
    """Save a copy of the current document"""

    BINDING_KEY = "ctrl+s"


### navigation.py ends here
