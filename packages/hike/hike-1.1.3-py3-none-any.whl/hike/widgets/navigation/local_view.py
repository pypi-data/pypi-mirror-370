"""Provides a widget for browsing the local filesystem."""

##############################################################################
# Python imports.
from pathlib import Path
from typing import Iterable

##############################################################################
# Textual imports.
from textual import on
from textual.widgets import DirectoryTree

##############################################################################
# Local imports.
from ...data import maybe_markdown
from ...messages import OpenLocation


##############################################################################
class LocalView(DirectoryTree):
    """A browser for the local filesystem."""

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        """Filter a directory for things that look like Markdown.

        Args:
            paths: The paths to filter down.

        Returns:
            The paths filtered as useful for Markdown viewing.
        """
        return (
            path
            for path in paths
            if (path.is_dir() and not path.name.startswith("."))
            or (path.is_file() and maybe_markdown(path))
        )

    @on(DirectoryTree.FileSelected)
    def view_file(self, message: DirectoryTree.FileSelected) -> None:
        """View the selected file.

        Args:
            message: The message requesting that the file be viewed.
        """
        message.stop()
        self.post_message(OpenLocation(message.path))


### local_view.py ends here
