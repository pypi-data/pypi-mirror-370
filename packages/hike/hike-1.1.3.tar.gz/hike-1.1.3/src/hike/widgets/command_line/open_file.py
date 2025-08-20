"""Provides the command for opening a file."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Textual imports.
from textual.widget import Widget

##############################################################################
# Local imports.
from ...messages import OpenLocation
from .base_command import InputCommand


##############################################################################
class OpenFileCommand(InputCommand):
    """View the file at `<file>`"""

    COMMAND = "`<file>`"

    @classmethod
    def handle(cls, text: str, for_widget: Widget) -> bool:
        """Handle the command.

        Args:
            text: The text of the command.
            for_widget: The widget to handle the command for.

        Returns:
            `True` if the command was handled; `False` if not.
        """
        if (path := Path(text).expanduser()).is_file():
            for_widget.post_message(OpenLocation(path.resolve()))
            return True
        return False


### open_directory.py ends here
