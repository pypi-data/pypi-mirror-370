"""Commands related to navigation."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import Command


##############################################################################
class Forward(Command):
    """Move forward through history"""

    BINDING_KEY = "ctrl+right_square_bracket"
    SHOW_IN_FOOTER = True


##############################################################################
class Backward(Command):
    """Move backward through history"""

    BINDING_KEY = "ctrl+left_square_bracket"
    SHOW_IN_FOOTER = True


##############################################################################
class JumpToTableOfContents(Command):
    """Jump to the table of contents in the navigation panel"""

    BINDING_KEY = "ctrl+t"


##############################################################################
class JumpToLocalBrowser(Command):
    """Jump to the local filesystem browser in the navigation panel"""

    BINDING_KEY = "ctrl+l"


##############################################################################
class JumpToBookmarks(Command):
    """Jump to the bookmarks in the navigation panel"""

    BINDING_KEY = "ctrl+o"


##############################################################################
class JumpToHistory(Command):
    """Jump to the history in the navigation panel"""

    BINDING_KEY = "ctrl+y"


### navigation.py ends here
