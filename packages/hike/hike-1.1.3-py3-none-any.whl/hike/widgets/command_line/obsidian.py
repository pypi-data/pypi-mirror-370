"""Provides a command for browsing Obsidian vaults."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Textual imports.
from textual.widget import Widget

##############################################################################
# Local imports.
from ...data import load_configuration
from ...messages import SetLocalViewRoot
from .base_command import InputCommand


##############################################################################
class ObsidianCommand(InputCommand):
    """Change the root directory to your Obsidian vaults"""

    COMMAND = "`obsidian`"
    ALIASES = "`obs`"

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
            if vaults := Path(load_configuration().obsidian_vaults).expanduser():
                if vaults.exists() and vaults.is_dir():
                    for_widget.post_message(SetLocalViewRoot(vaults.resolve()))
                    return True
        return False


### obsidian.py ends here
