"""Provides the code for saving and loading the history."""

##############################################################################
# Python imports.
from json import dumps, loads
from pathlib import Path

##############################################################################
# httpx imports.
from httpx import URL

##############################################################################
# Local imports.
from ..types import HikeHistory
from .locations import data_dir


##############################################################################
def history_file() -> Path:
    """Get the path for the history file.

    Returns:
        The path for the history file.
    """
    return data_dir() / "history.json"


##############################################################################
def save_history(history: HikeHistory) -> None:
    """Save the history to storage.

    Args:
        history: The history to save.
    """
    history_file().write_text(
        dumps(
            [
                ("url" if isinstance(entry, URL) else "path", str(entry))
                for entry in history
            ],
            indent=4,
        ),
        encoding="utf-8",
    )


##############################################################################
def load_history() -> HikeHistory:
    """Load the history from storage.

    Returns:
        The loaded history.
    """
    return HikeHistory(
        [
            (URL if entry_type == "url" else Path)(entry)
            for entry_type, entry in loads(history.read_text(encoding="utf-8"))
        ]
        if (history := history_file()).exists()
        else []
    )


### history.py ends here
