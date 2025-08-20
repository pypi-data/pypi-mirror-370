"""Commands for the fallback editor."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import (
    ChangeTheme,
    Command,
    CommandHits,
    CommandsProvider,
    Help,
)


##############################################################################
class Save(Command):
    """Save changes back to the document"""

    BINDING_KEY = "f2, ctrl+s"
    SHOW_IN_FOOTER = True


##############################################################################
class Close(Command):
    """Close the editor"""

    BINDING_KEY = "f10"
    SHOW_IN_FOOTER = True


##############################################################################
class EditorCommands(CommandsProvider):
    """Provides the commands for the fallback editor."""

    def commands(self) -> CommandHits:
        """Provide the main application commands for the command palette.

        Yields:
            The commands for the command palette.
        """
        yield ChangeTheme()
        yield Help()
        yield Save()
        yield Close()


### commands.py ends here
