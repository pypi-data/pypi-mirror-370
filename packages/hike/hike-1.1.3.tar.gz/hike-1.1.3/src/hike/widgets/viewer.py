"""Provides the Markdown viewer widget."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass
from functools import singledispatchmethod
from os import getenv
from pathlib import Path
from subprocess import run

##############################################################################
# httpx imports.
from httpx import URL, AsyncClient, HTTPStatusError, RequestError

##############################################################################
# MarkdownIt imports.
from markdown_it import MarkdownIt
from mdit_py_plugins import front_matter

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.events import Click
from textual.message import Message
from textual.reactive import var
from textual.widgets import Label, Markdown, Rule

##############################################################################
# Textual enhanced imports.
from textual_enhanced.containers import EnhancedVerticalScroll

##############################################################################
# Typing extensions imports.
from typing_extensions import Self

##############################################################################
# Local imports.
from .. import USER_AGENT
from ..commands import JumpToCommandLine
from ..data import is_editable, load_configuration, looks_urllike
from ..editor import Editor
from ..messages import CopyToClipboard, OpenLocation
from ..support import is_copy_request_click, view_in_browser
from ..types import HikeHistory, HikeLocation


##############################################################################
class ViewerTitle(Label):
    """Widget to display the viewer's title."""

    DEFAULT_CSS = """
    ViewerTitle {
        background: $panel;
        color: $foreground;
        content-align: right middle;
        width: 1fr;
        height: 1;
    }
    """

    location: var[HikeLocation | None] = var(None, always_update=True)
    """The location to display."""

    def _watch_location(self) -> None:
        """React to the location changing."""
        if (
            len(
                display := ""
                if self.location is None
                else str(self.location)[-self.size.width :]
            )
            >= self.size.width
        ):
            display = f"…{display[1:]}"
        self.update(display)

    def on_resize(self) -> None:
        """Handle the widget being resized."""
        self.location = self.location

    @on(Click)
    def _maybe_clipboard(self, message: Click) -> None:
        """Maybe copy to the clipboard.

        Args:
            message: The mouse click message.
        """
        if is_copy_request_click(message) and self.location:
            message.stop()
            self.post_message(CopyToClipboard(str(self.location)))


##############################################################################
class MarkdownScroll(EnhancedVerticalScroll):
    """The scrolling container for the Markdown document."""

    HELP = """
    ## Movement

    As well as using the common set of cursor and page keys, the following
    keys are available for movement within the markdown document:
    """


##############################################################################
class Viewer(Vertical, can_focus=False):
    """The Markdown viewer widget."""

    DEFAULT_CSS = """
    Viewer {
        display: block;
        &.empty {
            display: none;
        }
        EnhancedVerticalScroll {
            background: transparent;
        }
        Markdown {
            background: transparent;
        }
        Rule {
            height: 1;
            margin: 0 !important;
            color: $foreground 10%;
        }
    }
    """

    HELP = """
    ## Viewer

    This is the main Markdown viewer.

    ### Copying to the clipboard

    See the main help and the command palette for commands for copying to
    the clipboard; you can also copy with the mouse by either clicking once
    while holding down <kbd>ctrl</kbd>, or click 3 times. Doing so on the
    location will copy the location, doing so on the main document will copy
    the markdown's source.

    Locally-useful keys include:
    """

    BINDINGS = [
        ("escape", "bounce_out"),
    ]

    location: var[HikeLocation | None] = var(None)
    """The location of the markdown being displayed."""

    history: var[HikeHistory] = var(HikeHistory)
    """The history for the viewer."""

    _source: var[str] = var("")
    """The source of the Markdown we're viewing."""

    def compose(self) -> ComposeResult:
        """Compose the content of the viewer."""
        yield ViewerTitle()
        yield Rule(line_style="heavy")
        with MarkdownScroll(id="document"):
            yield Markdown(
                open_links=False,
                parser_factory=lambda: MarkdownIt("gfm-like").use(
                    front_matter.front_matter_plugin
                ),
            )

    def focus(self, scroll_visible: bool = True) -> Self:
        """Focus the viewer.

        Args:
            scroll_visible: Should the widget be scrolled to be visible?

        Returns:
            Self.
        """
        self.query_one("#document").focus(scroll_visible)
        return self

    @property
    def source(self) -> str:
        """The source of the markdown being viewed."""
        return self._source

    @property
    def filename(self) -> Path | None:
        """The name of the file being viewed.

        Notes:
            This is just the name of the file itself, without any path. If
            no file is being viewed at the moment then the value is `None`.
        """
        if isinstance(self.location, Path):
            return Path(self.location.name)
        if isinstance(self.location, URL):
            return Path(Path(self.location.path).name)
        return None

    def action_bounce_out(self) -> None:
        """Bounce back out to the input."""
        self.post_message(JumpToCommandLine())

    @dataclass
    class Loaded(Message):
        """Class posted when the markdown content is loaded."""

        viewer: Viewer
        """The viewer."""

        markdown: str
        """The markdown content."""

        remember: bool
        """Should this load be remembered?"""

    @dataclass
    class HistoryUpdated(Message):
        """Class posted when the history is updated."""

        viewer: Viewer
        """The viewer."""

    @dataclass
    class HistoryVisit(Message):
        """Class posted when a location in history is visited."""

        viewer: Viewer
        """The viewer."""

    @on(HistoryUpdated)
    def _history_updated(self) -> None:
        """React to the bindings being updated."""
        self.refresh_bindings()
        # Given that the content of history has changed, we need to update
        # the display. If we have history...
        if self.history:
            # ...visit whatever is now current.
            self._visit_from_history()
        else:
            # ...otherwise there's nothing to display.
            self.location = None

    def _watch_history(self) -> None:
        """React to the history being updated."""
        self.post_message(self.HistoryUpdated(self))

    @work(thread=True, exclusive=True)
    def _load_from_file(self, location: Path, remember: bool) -> None:
        """Load up markdown content from a file.

        Args:
            location: The path to load the content from.
            remember: Should this location go into history?
        """
        try:
            self.post_message(
                self.Loaded(self, Path(location).read_text(encoding="utf-8"), remember)
            )
        except OSError as error:
            self.notify(str(error), title="Load error", severity="error", timeout=8)

    @work(exclusive=True)
    async def _load_from_url(self, location: URL, remember: bool) -> None:
        """Load up markdown content from a URL.

        Args:
            location: The URL to load the content from.
            remember: Should this location go into history?
        """

        # Download the data from the remote location.
        try:
            async with AsyncClient() as client:
                response = await client.get(
                    location,
                    follow_redirects=True,
                    headers={"user-agent": USER_AGENT},
                )
        except RequestError as error:
            self.notify(str(error), title="Request error", severity="error", timeout=8)
            return

        # We got a response, left's check it's a good one.
        try:
            response.raise_for_status()
        except HTTPStatusError as error:
            self.notify(str(error), title="Response error", severity="error", timeout=8)
            return

        # At this point we've got a good response. Now let's be sure that
        # what we got back is something that admits to being markdown, or at
        # least a form of plain text we can render.
        if content_type := response.headers.get("content-type"):
            if any(
                content_type.startswith(allowed_type)
                for allowed_type in load_configuration().markdown_content_types
            ):
                self.post_message(self.Loaded(self, response.text, remember))
                return

        # It doesn't look like Markdown, so let's open it in the browser.
        self.notify(
            "That location doesn't look like a Markdown file, opening in your browser..."
        )
        view_in_browser(location)

    @singledispatchmethod
    def _load_markdown(self, location: Path, remember: bool) -> None:
        """Load markdown from a location.

        Args:
            location: The location to load the markdown from.
            remember: Should this location go into history?
        """
        self._load_from_file(location, remember)

    @_load_markdown.register
    def _(self, location: URL, remember: bool) -> None:
        self._load_from_url(location, remember)

    @_load_markdown.register
    def _(self, location: None, remember: bool) -> None:
        self.post_message(self.Loaded(self, "", remember))

    def _visit(
        self,
        location: HikeLocation | None,
        remember: bool = True,
        preserve_position: bool = False,
    ) -> None:
        """Visit the given location.

        Args:
            location: The location to visit.
            remember: Should this location go into history?
            preserve_position: Attempt to preserve the scroll position?
        """
        self.set_class(location is None, "empty")
        self._load_markdown(location, remember)
        if not preserve_position:
            self.query_one("#document").scroll_home(animate=False)

    def _watch_location(self) -> None:
        """Handle changes to the location to view."""
        if self.is_mounted:
            self._visit(self.location)

    @on(Loaded)
    def _update_markdown(self, message: Loaded) -> None:
        """Update the markdown once some new content is loaded.

        Args:
            message: The message requesting the update.
        """
        self.query_one(ViewerTitle).location = self.location
        self._source = message.markdown
        self.query_one(Markdown).update(message.markdown)
        if (
            message.remember
            and self.location
            and self.location != self.history.current_item
        ):
            self.history.add(self.location)
            self.post_message(self.HistoryUpdated(self))

    def _visit_from_history(self) -> None:
        """Visit the current location in history."""
        self.set_reactive(Viewer.location, self.history.current_item)
        self._visit(self.location, remember=False)
        self.post_message(self.HistoryVisit(self))
        self.refresh_bindings()

    def reload(self) -> None:
        """Reload the current document."""
        self._visit(self.location, remember=False, preserve_position=True)

    def goto(self, history_location: int) -> None:
        """Go to a specific location in history."""
        if self.history.current_location != history_location:
            self.history.goto(history_location)
            self._visit_from_history()

    def backward(self) -> None:
        """Go backward through the history."""
        if self.history.backward():
            self._visit_from_history()

    def forward(self) -> None:
        """Go forward through the history."""
        if self.history.forward():
            self._visit_from_history()

    def jump_to_content(self, block_id: str) -> None:
        """Jump to some content in the current document.

        Args:
            block_id: The ID of the content to jump to.
        """
        self.scroll_to_widget(self.query_one(f"#{block_id}"), top=True)

    def remove_from_history(self, history: int) -> None:
        """Remove a specific location from history.

        Args:
            history: The ID of the location in history to remove.
        """
        del self.history[history]
        self.post_message(self.HistoryUpdated(self))

    def clear_history(self) -> None:
        """Clear all locations from history."""
        self.history = HikeHistory()

    def deduplicate_history(self) -> None:
        """Squish history down so that there are no duplicates."""
        self.history = HikeHistory(list(dict.fromkeys(self.history)))

    @on(Markdown.LinkClicked)
    def _handle_link(self, message: Markdown.LinkClicked) -> None:
        """Handle a link being clicked in the Markdown widget.

        Args:
            message: The message requesting the link be handled.
        """
        message.stop()

        # Outright URL?
        if looks_urllike(message.href):
            self.post_message(OpenLocation(URL(message.href)))
            return

        # Possibly a relative path to a currently-visited URL?
        if isinstance(self.location, URL):
            self.post_message(
                OpenLocation(self.location.copy_with().join(message.href))
            )
            return

        # A local file that exists?
        if (local_file := Path(message.href).expanduser()).exists():
            self.post_message(OpenLocation(local_file.resolve()))
            return

        # A local file relative to the current location?
        if (
            isinstance(self.location, Path)
            and (local_file := self.location.parent / Path(message.href))
            .absolute()
            .exists()
        ):
            self.post_message(OpenLocation(local_file))
            return

        # Some sort of internal anchor perhaps?
        if message.href.startswith("#") and message.markdown.goto_anchor(
            message.href[1:]
        ):
            return

        self.notify(
            f"The clicked link could not be handled:\n\n{message.href}",
            title="Unknown link type",
            severity="error",
        )

    @on(Click)
    def _maybe_clipboard(self, message: Click) -> None:
        """Maybe copy to the clipboard.

        Args:
            message: The mouse click message.
        """
        if is_copy_request_click(message) and self._source:
            message.stop()
            self.post_message(CopyToClipboard(self._source))

    @property
    def is_editable(self) -> bool:
        """Is the current location editable?"""
        return self.location is not None and is_editable(self.location)

    def edit(self) -> None:
        """Edit the current document."""

        # There's no point in even attempting to edit if we're not looking a
        # something.
        if self.location is None:
            return

        # We can't edit something that isn't local.
        if not is_editable(self.location):
            self.notify(
                "Editing is only supported for Markdown files in the local filesystem.",
                title="Not Supported",
                severity="warning",
            )
            return

        # We need an editor to edit things.
        if editor := (getenv("VISUAL") or getenv("EDITOR") or ""):
            # Run the editor.
            with self.app.suspend():
                run((editor, str(self.location)))
            # Given we did an edit, we should now reload.
            self.reload()
        else:
            self.app.push_screen(
                Editor(self.location), callback=lambda _: self.reload()
            )


### viewer.py ends here
