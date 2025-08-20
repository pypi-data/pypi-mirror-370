"""Provides the bookmarks for the navigation panel."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from typing import cast

##############################################################################
# httpx imports.
from httpx import URL

##############################################################################
# Textual imports.
from textual import on, work
from textual.content import Content
from textual.message import Message
from textual.widgets.option_list import Option

##############################################################################
# Textual enhanced imports.
from textual_enhanced.binding import HelpfulBinding
from textual_enhanced.dialogs import Confirm, ModalInput
from textual_enhanced.widgets import EnhancedOptionList

##############################################################################
# Local imports.
from ...data import Bookmark, Bookmarks
from ...icons import LOCAL_FILE_ICON, REMOTE_FILE_ICON
from ...messages import OpenLocation


##############################################################################
class BookmarkView(Option):
    """The view of a bookmark."""

    def __init__(self, bookmark: Bookmark) -> None:
        """Initialise the object.

        Args:
            bookmark: The bookmark.
        """
        self.bookmark = bookmark
        """The bookmark."""
        super().__init__(
            Content.from_markup(
                f"{REMOTE_FILE_ICON if isinstance(bookmark.location, URL) else LOCAL_FILE_ICON} "
                f"[bold]{bookmark.title}[/]\n[dim]{bookmark.location}[/]",
            ),
            id=str(bookmark.location),
        )


##############################################################################
class BookmarksView(EnhancedOptionList):
    """The display of bookmarks."""

    DEFAULT_CSS = """
    BookmarksView {
        height: 1fr;
        border: none;
        text-wrap: nowrap;
        text-overflow: ellipsis;
        &:focus {
            border: none;
        }
    }
    """

    HELP = """
    ## Bookmarks

    This panel contains your bookmarks. Here you can visit them and manage them.
    """

    BINDINGS = [
        HelpfulBinding(
            "r",
            "rename",
            "Rename",
            show=False,
            tooltip="Rename the highlighted bookmark",
        ),
        HelpfulBinding(
            "delete",
            "delete",
            "Delete",
            show=False,
            tooltip="Delete the highlighted bookmark",
        ),
    ]

    def update(self, bookmarks: Bookmarks) -> None:
        """Up[date the content of the bookmarks view.

        Args:
            bookmarks: The bookmarks to show.
        """
        with self.preserved_highlight:
            self.clear_options().add_options(
                BookmarkView(bookmark) for bookmark in sorted(bookmarks)
            )

    @on(EnhancedOptionList.OptionSelected)
    def _visit_bookmark(self, message: EnhancedOptionList.OptionSelected) -> None:
        """Visit the current bookmark.

        Args:
            message: The message requesting the visit.
        """
        message.stop()
        assert isinstance(message.option, BookmarkView)
        self.post_message(OpenLocation(message.option.bookmark.location))

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Check if an action is possible to perform right now.

        Args:
            action: The action to perform.
            parameters: The parameters of the action.

        Returns:
            `True` if it can perform, `False` or `None` if not.
        """
        if action in ("edit", "delete"):
            return bool(self.option_count) and self.highlighted is not None
        return True

    @property
    def current_bookmark(self) -> Bookmark | None:
        """The currently-highlighted bookmark."""
        return (
            None
            if self.highlighted is None
            else cast(BookmarkView, self.get_option_at_index(self.highlighted)).bookmark
        )

    @dataclass
    class Renamed(Message):
        """Message sent when a bookmark is renamed."""

        renamed_from: Bookmark
        """The bookmark that was being renamed."""
        renamed_to: Bookmark
        """The renamed bookmark."""

    @work
    async def action_rename(self) -> None:
        """Rename the currently-highlighted bookmark."""
        if self.current_bookmark is None:
            return
        if title := await self.app.push_screen_wait(
            ModalInput(
                "The title for the bookmark", initial=self.current_bookmark.title
            )
        ):
            self.post_message(
                self.Renamed(
                    self.current_bookmark,
                    Bookmark(title, self.current_bookmark.location),
                )
            )

    @dataclass
    class Deleted(Message):
        """Message sent when a bookmark is deleted."""

        deleted: Bookmark
        """The bookmark that was deleted."""

    @work
    async def action_delete(self) -> None:
        """Delete the currently-highlighted bookmark."""
        if self.current_bookmark is None:
            return
        if await self.app.push_screen_wait(
            Confirm("Delete bookmark?", "Are you sure you want to delete the bookmark?")
        ):
            self.post_message(self.Deleted(self.current_bookmark))


### bookmarks_view.py ends here
