"""Defines icons that are commonly-used in the application."""

##############################################################################
# Python imports.
from typing import Final

##############################################################################
# Rich imports.
from rich.emoji import Emoji

##############################################################################
LOCAL_FILE_ICON: Final[str] = Emoji.replace(":page_facing_up:")
"""Icon to use for a local file."""

##############################################################################
REMOTE_FILE_ICON: Final[str] = Emoji.replace(":globe_with_meridians:")
"""icon to sue for a remote file."""

### icons.py ends here
