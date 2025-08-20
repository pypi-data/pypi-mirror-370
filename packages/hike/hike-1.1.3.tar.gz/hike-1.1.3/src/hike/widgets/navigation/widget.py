"""Provides the navigation panel widget."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass
from pathlib import Path

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.reactive import var
from textual.widgets import Markdown, TabbedContent, TabPane, Tabs, Tree
from textual.widgets.markdown import MarkdownTableOfContents, TableOfContentsType

##############################################################################
# Textual enhanced imports.
from textual_enhanced.binding import HelpfulBinding

##############################################################################
# Local imports.
from ...commands import JumpToCommandLine
from ...data import Bookmark, Bookmarks, load_configuration
from ...types import HikeHistory, HikeLocation
from .bookmarks_view import BookmarksView
from .history_view import HistoryView
from .local_view import LocalView


##############################################################################
class Navigation(Vertical):
    """The navigation panel."""

    DEFAULT_CSS = """
    Navigation {
        width: 27%;
        min-width: 38;
        dock: left;
        background: transparent;

        &.--dock-right {
            dock: right;
        }

        #tabs-list {
            background: $panel;
        }

        /* https://github.com/Textualize/textual/issues/5488 */
        MarkdownTableOfContents, &:focus-within MarkdownTableOfContents {
            background: transparent;
            width: 1fr;
            Tree {
                background: transparent;
            }
        }

        /* https://github.com/Textualize/textual/issues/5488 */
        HistoryView, &:focus-within HistoryView,
        LocalView, &:focus-within LocalView,
        BookmarksView, &:focus-within BookmarksView {
            background: transparent;
        }
    }
    """

    BINDINGS = [
        ("escape", "return_to_tabs_or_bounce_out"),
        ("down", "move_into_panel"),
        HelpfulBinding(
            "ctrl+left",
            "switch('previous_tab')",
            tooltip="Move to the previous navigation tab",
        ),
        HelpfulBinding(
            "ctrl+right",
            "switch('next_tab')",
            tooltip="Move to the next navigation tab",
        ),
        ("h", "tab_left"),
        ("j", "also_down"),
        ("k", "also_up"),
        ("l", "tab_right"),
    ]

    HELP = """
    ## The Navigation Panel

    Here you'll find panels for the current document's table of contents; a
    local file browser (use the `chdir` command in the command line at the
    bottom of the screen to change the root directory); a simple bookmark
    manager and your browsing history.

    ### Useful keys
    """

    dock_right: var[bool] = var(False)
    """Should the navigation dock to the right?"""

    table_of_contents: var[TableOfContentsType | None] = var(None)
    """The currently-displayed table of contents."""

    bookmarks: var[Bookmarks] = var(Bookmarks)
    """The bookmarks."""

    def action_return_to_tabs_or_bounce_out(self) -> None:
        """Return focus to the tabs, or to the input."""
        if self.screen.focused == (tabs := self.query_one(Tabs)):
            self.post_message(JumpToCommandLine())
        else:
            tabs.focus()

    def action_move_into_panel(self) -> None:
        """Drop focus down into a panel."""
        if (active := self.query_one(TabbedContent).active_pane) is not None:
            for widget in active.query("*"):
                if widget.can_focus:
                    widget.focus()
                    return

    async def action_switch(self, switcher: str) -> None:
        await self.query_one(Tabs).run_action(switcher)
        self.call_after_refresh(self.run_action, "move_into_panel")

    def _watch_dock_right(self) -> None:
        """React to the dock toggle being changed."""
        self.set_class(self.dock_right, "--dock-right")

    def _maybe_enable_tab(self, tab: str, data: object) -> bool:
        """Enable/disable a tab based on there being data.

        Args:
            tab: The name of the tab.
            data: The data to test.

        Returns:
            `True` if the tab was enabled, `False` if disabled.
        """
        tabs = self.query_one(TabbedContent)
        if data:
            tabs.enable_tab(tab)
            return True
        tabs.disable_tab(tab)
        if tabs.active == tab:
            tabs.active = "local"
        return False

    def _watch_table_of_contents(self) -> None:
        """React to the table of content being updated."""
        self.query_one(
            MarkdownTableOfContents
        ).table_of_contents = self.table_of_contents
        if self._maybe_enable_tab("content", self.table_of_contents):
            self.query_one("MarkdownTableOfContents Tree", Tree).cursor_line = 0

    def _watch_bookmarks(self) -> None:
        """React to the bookmarks being changed."""
        self.query_one(BookmarksView).update(self.bookmarks)
        self._maybe_enable_tab("bookmarks", self.bookmarks)

    def compose(self) -> ComposeResult:
        """Compose the content of the widget."""
        with TabbedContent():
            with TabPane("Content", id="content"):
                yield MarkdownTableOfContents(Markdown())
            with TabPane("Local", id="local"):
                yield LocalView(
                    Path(load_configuration().local_start_location).expanduser()
                )
            with TabPane("Bookmarks", id="bookmarks"):
                yield BookmarksView()
            with TabPane("History", id="history"):
                yield HistoryView()

    def update_history(self, history: HikeHistory) -> None:
        """Update the history display.

        Args:
            history: The history to display.
        """
        self.query_one(HistoryView).update(history)
        self._maybe_enable_tab("history", history)

    def highlight_history(self, history: int) -> None:
        """Highlight a specific entry in history.

        Args:
            The ID of the item of history to highlight.
        """
        self.query_one(HistoryView).highlight_location(history)

    def set_local_view_root(self, root: Path) -> None:
        """Set the root directory for the local file browser.

        Args:
            root: The new root directory.
        """
        self.query_one(LocalView).path = root

    def refresh_local_view(self) -> None:
        """Refresh the local view."""
        self.query_one(LocalView).reload()

    @dataclass
    class BookmarksUpdated(Message):
        """Message sent when the bookmarks are updated."""

        navigation: Navigation
        """The navigation widget sending the message."""

    def add_bookmark(self, title: str, location: HikeLocation) -> None:
        """Add a bookmark.

        Args:
            title: The title of the bookmark.
            location: The location to bookmark.
        """
        self.bookmarks = [Bookmark(title, location), *self.bookmarks]
        self.post_message(self.BookmarksUpdated(self))

    @on(BookmarksView.Renamed)
    def _bookmark_renamed(self, message: BookmarksView.Renamed) -> None:
        """Handle a bookmark being renamed.

        Args:
            message: The message requesting the deletion.
        """
        try:
            bookmark = self.bookmarks.index(message.renamed_from)
        except ValueError:
            self.notify(
                "Could not find the bookmark to modify it",
                title="Bookmark error",
                severity="error",
            )
            return
        (new_bookmarks := self.bookmarks.copy())[bookmark] = message.renamed_to
        self.bookmarks = new_bookmarks
        self.post_message(self.BookmarksUpdated(self))

    @on(BookmarksView.Deleted)
    def _bookmark_deleted(self, message: BookmarksView.Deleted) -> None:
        """handle a bookmark being deleted.

        Args:
            message: The message requesting the deletion.
        """
        try:
            bookmark = self.bookmarks.index(message.deleted)
        except ValueError:
            self.notify(
                "Could not find the bookmark to delete it",
                title="Bookmark error",
                severity="error",
            )
            return
        del (new_bookmarks := self.bookmarks.copy())[bookmark]
        self.bookmarks = new_bookmarks
        self.post_message(self.BookmarksUpdated(self))

    def _activate(self, panel: str) -> None:
        self.query_one(TabbedContent).active = panel
        self.call_next(self.run_action, "move_into_panel")

    def jump_to_content(self) -> None:
        """Jump into the content panel, if possible."""
        if self.table_of_contents:
            self._activate("content")

    def jump_to_local(self) -> None:
        """Jump into the local browser panel, if possible."""
        self._activate("local")

    def jump_to_bookmarks(self) -> None:
        """Jump into the bookmarks panel, if possible."""
        if self.bookmarks:
            self._activate("bookmarks")

    def jump_to_history(self) -> None:
        """Jump into the history panel, if possible."""
        if self.query_one(HistoryView).option_count:
            self._activate("history")

    async def action_also_down(self) -> None:
        """Hack in some extra cursor down support."""
        if isinstance(self.screen.focused, Tree):
            await self.screen.focused.run_action("cursor_down")
        else:
            await self.run_action("move_into_panel")

    async def action_also_up(self) -> None:
        """Hack in some extra cursor up support."""
        if isinstance(self.screen.focused, Tree):
            await self.screen.focused.run_action("cursor_up")

    async def action_tab_left(self) -> None:
        """Hack in some extra cursor left support."""
        if query := self.query("Tabs:focus"):
            await query[0].run_action("previous_tab")

    async def action_tab_right(self) -> None:
        """Hack in some extra cursor right support."""
        if query := self.query("Tabs:focus"):
            await query[0].run_action("next_tab")


### navigation.py ends here
