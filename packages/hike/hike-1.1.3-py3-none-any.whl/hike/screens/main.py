"""The main screen for the application."""

##############################################################################
# Python imports.
from argparse import Namespace
from functools import partial

##############################################################################
# Pyperclip imports.
from pyperclip import PyperclipException
from pyperclip import copy as copy_to_clipboard

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalGroup
from textual.reactive import var
from textual.widgets import Footer, Header, Markdown

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import ChangeTheme, Command, Help, Quit
from textual_enhanced.dialogs import ModalInput
from textual_enhanced.screen import EnhancedScreen
from textual_enhanced.tools import add_key

##############################################################################
# Textual fspicker imports.
from textual_fspicker import FileOpen, FileSave, Filters

##############################################################################
# Local imports.
from .. import __version__
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
from ..data import (
    load_bookmarks,
    load_command_history,
    load_configuration,
    load_history,
    maybe_markdown,
    save_bookmarks,
    save_command_history,
    save_history,
    update_configuration,
)
from ..messages import (
    ClearHistory,
    CopyToClipboard,
    DeduplicateHistory,
    HandleInput,
    OpenFrom,
    OpenFromForge,
    OpenFromHistory,
    OpenLocation,
    RemoveHistoryEntry,
    SetLocalViewRoot,
)
from ..providers import BookmarkCommands, HistoryCommands, MainCommands
from ..support import view_in_browser
from ..widgets import CommandLine, Navigation, Viewer


##############################################################################
class Main(EnhancedScreen[None]):
    """The main screen for the application."""

    TITLE = f"Hike v{__version__}"

    DEFAULT_CSS = """
    Main {
        #workspace {
            hatch: right $surface;
            .panel {
                border-left: solid $panel;
                &:focus, &:focus-within {
                    border-left: solid $border;
                }
            }
        }

        .panel {
            background: $surface;
            &:focus-within {
                background: $panel 80%;
            }
            * {
                scrollbar-background: $surface;
                scrollbar-background-hover: $surface;
                scrollbar-background-active: $surface;
            }
            &:focus-within * {
                scrollbar-background: $panel;
                scrollbar-background-hover: $panel;
                scrollbar-background-active: $panel;
            }
        }

        Navigation {
            display: none;
        }
        &.navigation Navigation {
            display: block;
        }
    }
    """

    HELP = """
    ## Main application keys and commands

    The following key bindings and commands are available:
    """

    COMMAND_MESSAGES = (
        # Keep these together as they're bound to function keys and destined
        # for the footer.
        Help,
        ToggleNavigation,
        Edit,
        ChangeTheme,
        Quit,
        # Everything else.
        Backward,
        BookmarkLocation,
        ChangeCommandLineLocation,
        ChangeNavigationSide,
        CopyLocationToClipboard,
        CopyMarkdownToClipboard,
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
    )

    BINDINGS = Command.bindings(*COMMAND_MESSAGES)
    COMMANDS = {MainCommands}

    AUTO_FOCUS = "CommandLine Input"

    navigation_visible: var[bool] = var(True)
    """Set if the navigation panel is visible or not."""

    def __init__(self, arguments: Namespace) -> None:
        """Initialise the main screen.

        Args:
            arguments: The arguments passed to the application on the command line.
        """
        self._arguments = arguments
        """The arguments passed on the command line."""
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the content of the screen."""
        yield Header()
        with VerticalGroup():
            with Horizontal(id="workspace"):
                yield Navigation(classes="panel")
                yield Viewer(classes="panel")
            yield CommandLine(classes="panel")
        yield Footer()

    def on_mount(self) -> None:
        """Configure the screen once the DOM is mounted."""
        config = load_configuration()
        self.navigation_visible = (
            config.navigation_visible
            if self._arguments.navigation is None
            else self._arguments.navigation
        )
        self.query_one(Navigation).dock_right = config.navigation_on_right
        self.query_one(Navigation).bookmarks = (bookmarks := load_bookmarks())
        BookmarkCommands.bookmarks = bookmarks
        self.query_one(Viewer).history = load_history()
        self.query_one(CommandLine).history = load_command_history()
        self.query_one(CommandLine).dock_top = config.command_line_on_top
        if self._arguments.command:
            self.post_message(HandleInput(" ".join(self._arguments.command)))

    def _watch_navigation_visible(self) -> None:
        """React to the navigation visible property being set."""
        self.set_class(self.navigation_visible, "navigation")
        with update_configuration() as config:
            config.navigation_visible = self.navigation_visible

    @on(Help)
    async def _show_help(self) -> None:
        """Handle the help action."""
        await self.run_action("help_command")

    @on(HandleInput)
    def _handle_input(self, message: HandleInput) -> None:
        """Handle input as if the user had typed it in.

        Args:
            message: The message requesting the input be handled.
        """
        self.query_one(CommandLine).handle_input(message.user_input)

    @on(CopyToClipboard)
    def _copy_text_to_clipbaord(self, message: CopyToClipboard) -> None:
        """Copy some text into the clipboard.

        Args:
            message: The message requesting the text be copied.
        """
        # First off, use Textual's own copy to clipboard facility. Generally
        # this will work in most terminals, and if it does it'll likely work
        # best, getting the text through remote connections to the user's
        # own environment.
        self.app.copy_to_clipboard(message.text)
        # However, as a backup, use pyerclip too. If the above did fail due
        # to the terminal not supporting the operation, this might.
        try:
            copy_to_clipboard(message.text)
        except PyperclipException:
            pass
        # Give the user some feedback.
        self.notify("Copied")

    @on(OpenLocation)
    def _open_markdown(self, message: OpenLocation) -> None:
        """Open a file for viewing.

        Args:
            message: The message requesting the file be opened.
        """
        if maybe_markdown(message.to_open):
            self.query_one(Viewer).location = message.to_open
            if load_configuration().focus_viewer_on_load:
                self.query_one(Viewer).focus()
        else:
            view_in_browser(message.to_open)

    @on(OpenFrom)
    @work
    async def _browse_for_file(self, message: OpenFrom) -> None:
        """Browse for a markdown file with a file open dialog.

        Args:
            message: The message requesting the operation.
        """
        if chosen := await self.app.push_screen_wait(
            FileOpen(
                message.location,
                filters=Filters(
                    (
                        "Markdown",
                        maybe_markdown,
                    ),
                    ("All files", lambda _: True),
                ),
                cancel_button=partial(add_key, key="Esc", context=self),
            )
        ):
            self.post_message(OpenLocation(chosen))

    @on(OpenFromHistory)
    def _open_from_history(self, message: OpenFromHistory) -> None:
        """Open a location from the history.

        Args:
            message: The message requesting the history open.
        """
        self.query_one(Viewer).goto(message.location)

    @on(OpenFromForge)
    @work
    async def _open_from_forge(self, message: OpenFromForge) -> None:
        """Open a file from a git forge.

        Args:
            message: The message requesting the operation.
        """
        if (url := await message.url()) is None:
            self.notify(
                "The file you were after could not be located.\n\n"
                "Check the spelling of the owner, repository and file; "
                "also consider what branch it might be on.",
                title=f"No suitable {message.forge} target found",
                severity="error",
                timeout=8,
            )
        else:
            self.post_message(OpenLocation(url))

    @on(RemoveHistoryEntry)
    def _remove_location_from_history(self, message: RemoveHistoryEntry) -> None:
        """Remove a specific location from history.

        Args:
            message: The message requesting the location be removed.
        """
        self.query_one(Viewer).remove_from_history(message.location)

    @on(ClearHistory)
    def _clear_down_history(self) -> None:
        """Clear all items from history."""
        self.query_one(Viewer).clear_history()

    @on(DeduplicateHistory)
    def _deduplicate_history(self) -> None:
        """Deduplicate the history."""
        self.query_one(Viewer).deduplicate_history()

    @on(SetLocalViewRoot)
    def _set_local_root(self, message: SetLocalViewRoot) -> None:
        """Change the root directory of the local file browser.

        Args:
            message: The message requesting the root be changed.
        """
        self.query_one(Navigation).set_local_view_root(message.root)

    @on(Markdown.TableOfContentsUpdated)
    def _update_navigation_contents(
        self, message: Markdown.TableOfContentsUpdated
    ) -> None:
        """Handle the table of contents being updated.

        Args:
            message: The message broadcasting that the ToC is updated.
        """
        self.query_one(Navigation).table_of_contents = message.table_of_contents

    @on(Markdown.TableOfContentsSelected)
    def _jump_to_content(self, message: Markdown.TableOfContentsSelected) -> None:
        """Jump to a specific location in the current document.

        Args:
            message: The message request the jump.
        """
        self.query_one(Viewer).jump_to_content(message.block_id)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Check if an action is possible to perform right now.

        Args:
            action: The action to perform.
            parameters: The parameters of the action.

        Returns:
            `True` if it can perform, `False` or `None` if not.
        """
        if not self.is_mounted:
            # Surprisingly it seems that Textual's "dynamic bindings" can
            # cause this method to be called before the DOM is up and
            # running. This breaks the rule of least astonishment, I'd say,
            # but okay let's be defensive... (when I can come up with a nice
            # little MRE I'll report it).
            return True
        if action == Forward.action_name():
            return self.query_one(Viewer).history.can_go_forward or None
        if action == Backward.action_name():
            return self.query_one(Viewer).history.can_go_backward or None
        if action == Edit.action_name():
            return self.query_one(Viewer).is_editable or None
        if action in (
            command.action_name()
            for command in (
                BookmarkLocation,
                CopyLocationToClipboard,
                CopyMarkdownToClipboard,
                Reload,
                SaveCopy,
            )
        ):
            return self.query_one(Viewer).location is not None
        return True

    def action_reload_command(self) -> None:
        """Reload the current document."""
        self.query_one(Viewer).reload()

    def action_search_bookmarks_command(self) -> None:
        """Search the bookmarks in the command palette."""
        self.show_palette(BookmarkCommands)

    def action_search_history_command(self) -> None:
        """search the history in the command palette."""
        self.show_palette(HistoryCommands)

    def action_toggle_navigation_command(self) -> None:
        """Toggle the display of the navigation panel."""
        self.navigation_visible = not self.navigation_visible

    def action_change_navigation_side_command(self) -> None:
        """Change the side that the navigation panel lives on."""
        navigation = self.query_one(Navigation)
        navigation.dock_right = not navigation.dock_right
        with update_configuration() as config:
            config.navigation_on_right = navigation.dock_right

    def action_change_command_line_location_command(self) -> None:
        """Change the location of the command line."""
        command_line = self.query_one(CommandLine)
        command_line.dock_top = not command_line.dock_top
        with update_configuration() as config:
            config.command_line_on_top = command_line.dock_top

    def action_jump_to_command_line_command(self) -> None:
        """Jump to the command line."""
        if self.AUTO_FOCUS:
            self.query_one(self.AUTO_FOCUS).focus()

    def action_jump_to_document_command(self) -> None:
        """Jump to the document."""
        self.query_one(Viewer).focus()

    def action_backward_command(self) -> None:
        """Move backward through history."""
        self.query_one(Viewer).backward()

    def action_forward_command(self) -> None:
        """Move forward through history."""
        self.query_one(Viewer).forward()

    @work
    async def action_bookmark_location_command(self) -> None:
        """Add the current location to the bookmarks."""
        if (location := self.query_one(Viewer).location) is None:
            self.notify(
                "Please visit a file or URL to bookmark it.", severity="warning"
            )
            return
        if location in self.query_one(Navigation).bookmarks:
            self.notify(
                "This location is already in your bookmarks", severity="warning"
            )
            return
        if title := await self.app.push_screen_wait(
            ModalInput("Enter a title for the bookmark")
        ):
            self.query_one(Navigation).add_bookmark(title, location)
            self.notify("Bookmark added")

    def _with_navigation_visible(self) -> Navigation:
        """Ensure navigation is visible.

        Returns:
            The navigation widget.
        """
        self.navigation_visible = True
        return self.query_one(Navigation)

    @on(Quit)
    def action_quit_command(self) -> None:
        """Quit the application."""
        self.app.exit()

    @on(JumpToTableOfContents)
    def action_jump_to_table_of_contents_command(self) -> None:
        """Jump to the table of contents."""
        self._with_navigation_visible().jump_to_content()

    @on(JumpToLocalBrowser)
    def action_jump_to_local_browser_command(self) -> None:
        """Jump to the local browser."""
        self._with_navigation_visible().jump_to_local()

    @on(JumpToBookmarks)
    def action_jump_to_bookmarks_command(self) -> None:
        """Jump to the bookmarks."""
        self._with_navigation_visible().jump_to_bookmarks()

    @on(JumpToHistory)
    def action_jump_to_history_command(self) -> None:
        """Jump to the history."""
        self._with_navigation_visible().jump_to_history()

    def action_copy_location_to_clipboard_command(self) -> None:
        """Copy the current location to the clipboard."""
        self.post_message(CopyToClipboard(str(self.query_one(Viewer).location)))

    def action_copy_markdown_to_clipboard_command(self) -> None:
        """Copy the current markdown to the clipboard."""
        self.post_message(CopyToClipboard(self.query_one(Viewer).source))

    def action_edit_command(self) -> None:
        """Edit the current markdown document, if possible."""
        self.query_one(Viewer).edit()

    @work
    async def action_save_copy_command(self) -> None:
        """Save a copy of the current document to a new file."""
        if (suggested := self.query_one(Viewer).filename) is None:
            return
        if save_to := await self.app.push_screen_wait(
            FileSave(
                default_file=suggested,
                cancel_button=partial(add_key, key="Esc", context=self),
            )
        ):
            try:
                save_to.write_text(self.query_one(Viewer).source, encoding="utf-8")
            except IOError as error:
                self.notify(str(error), title="Save Error", severity="error", timeout=8)
                return
            self.notify(f"Saved {save_to}")
            self.query_one(Navigation).refresh_local_view()

    @on(Viewer.HistoryUpdated)
    def _update_history(self, message: Viewer.HistoryUpdated) -> None:
        """Update the view of history when it changes.

        Args:
            message: The message to say that history changed.
        """
        HistoryCommands.history = message.viewer.history
        self.query_one(Navigation).update_history(message.viewer.history)
        save_history(message.viewer.history)

    @on(Viewer.HistoryVisit)
    def _move_history(self, message: Viewer.HistoryVisit) -> None:
        """React to a new location in history being visited."""
        if (location := message.viewer.history.current_location) is not None:
            self.query_one(Navigation).highlight_history(location)

    @on(Navigation.BookmarksUpdated)
    def _update_bookmarks(self, message: Navigation.BookmarksUpdated) -> None:
        """Handle the bookmarks being updated."""
        save_bookmarks(message.navigation.bookmarks)
        BookmarkCommands.bookmarks = message.navigation.bookmarks

    @on(CommandLine.HistoryUpdated)
    def _save_command_line_history(self, message: CommandLine.HistoryUpdated) -> None:
        """Save the command line history to storage when it changes.

        Args:
            message: The message requesting the same.
        """
        save_command_history(message.command_line.history)


### main.py ends here
