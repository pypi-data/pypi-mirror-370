"""Provides the main application commands for the command palette."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import (
    ChangeTheme,
    CommandHits,
    CommandsProvider,
    Help,
    Quit,
)

##############################################################################
# Local imports.
from ..commands import (
    Backward,
    BookmarkLocation,
    ChangeCommandLineLocation,
    ChangeNavigationSide,
    CopyLocationToClipboard,
    CopyMarkdownToClipboard,
    Edit,
    Forward,
    JumpToBookmarks,
    JumpToCommandLine,
    JumpToDocument,
    JumpToHistory,
    JumpToLocalBrowser,
    JumpToTableOfContents,
    Reload,
    SaveCopy,
    SearchBookmarks,
    SearchHistory,
    ToggleNavigation,
)


##############################################################################
class MainCommands(CommandsProvider):
    """Provides some top-level commands for the application."""

    def commands(self) -> CommandHits:
        """Provide the main application commands for the command palette.

        Yields:
            The commands for the command palette.
        """
        yield from self.maybe(Backward)
        yield from self.maybe(BookmarkLocation)
        yield ChangeCommandLineLocation()
        yield ChangeNavigationSide()
        yield ChangeTheme()
        yield from self.maybe(CopyLocationToClipboard)
        yield from self.maybe(CopyMarkdownToClipboard)
        yield from self.maybe(Edit)
        yield from self.maybe(Forward)
        yield Help()
        yield JumpToBookmarks()
        yield JumpToCommandLine()
        yield JumpToDocument()
        yield JumpToHistory()
        yield JumpToLocalBrowser()
        yield JumpToTableOfContents()
        yield Quit()
        yield from self.maybe(Reload)
        yield from self.maybe(SaveCopy)
        yield SearchBookmarks()
        yield SearchHistory()
        yield ToggleNavigation()


### main.py ends here
