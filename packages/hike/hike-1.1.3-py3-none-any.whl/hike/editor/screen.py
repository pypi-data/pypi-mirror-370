"""Provides a simple fallback text editor for editing some Markdown."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.reactive import var
from textual.widgets import Footer, Header, TextArea

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import ChangeTheme, Command, Help
from textual_enhanced.dialogs import Confirm
from textual_enhanced.screen import EnhancedScreen

##############################################################################
# Local imports.
from .commands import Close, EditorCommands, Save


##############################################################################
class Editor(EnhancedScreen[None]):
    """A fallback editor for editing some Markdown."""

    DEFAULT_CSS = """
    Editor {
        TextArea, TextArea:focus {
            border: none;
        }
    }
    """

    COMMAND_MESSAGES = (
        Help,
        Save,
        ChangeTheme,
        Close,
    )

    BINDINGS = Command.bindings(*COMMAND_MESSAGES)
    COMMANDS = {EditorCommands}

    HELP = """
    ## Markdown Editor

    This is a simple built-in editor for Markdown. If you wish to use your
    own editor set either the `$VISUAL` or `$EDITOR` environment variables
    to suit your taste.

    Commands available in the editor are:
    """

    _dirty: var[bool | None] = var(None)
    """Is the document dirty?"""

    def __init__(self, location: Path) -> None:
        """Initialise the screen.

        Args:
            location: The location to edit.
        """
        self._location = location
        """The location to edit."""
        super().__init__()
        self.title = str(location)

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header()
        yield TextArea.code_editor(language="markdown")
        yield Footer()

    def on_mount(self) -> None:
        """Configure the screen when the DOM is mounted."""
        try:
            self.query_one(TextArea).text = self._location.read_text(encoding="utf-8")
        except IOError as error:
            self.notify(
                str(error),
                title=f"Error reading from {self._location}",
                severity="error",
                timeout=8,
            )

    def _watch__dirty(self) -> None:
        """Handle the dirty flag being modified."""
        self.sub_title = "Edited" if self._dirty else ""

    @on(TextArea.Changed)
    def _go_dirty(self) -> None:
        """Mark that the document is dirty."""
        # We'll get a Changed event on startup, so we start with None, then
        # go to False, then go to True otherwise.
        self._dirty = False if self._dirty is None else True

    @on(Save)
    def action_save_command(self) -> None:
        """Save the editor content."""
        try:
            self._location.write_text(self.query_one(TextArea).text, encoding="utf-8")
        except IOError as error:
            self.notify(
                str(error),
                title=f"Error writing to {self._location}",
                severity="error",
                timeout=8,
            )
            return
        self._dirty = False

    @on(Close)
    @work
    async def action_close_command(self) -> None:
        """Close the editor."""
        if self._dirty:
            if not await self.app.push_screen_wait(
                Confirm(
                    "Unsaved changes",
                    "You have unsaved changed in your document. Are you sure you want to quit?",
                )
            ):
                return
        self.dismiss()


### screen.py ends here
