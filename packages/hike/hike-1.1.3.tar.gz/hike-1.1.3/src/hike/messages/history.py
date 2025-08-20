"""Messages to do with manipulating history."""

##############################################################################
# Python imports.
from dataclasses import dataclass

##############################################################################
# Textual imports.
from textual.message import Message


##############################################################################
@dataclass
class RemoveHistoryEntry(Message):
    """Remove an item from history."""

    location: int
    """The location in the history to remove."""


##############################################################################
class ClearHistory(Message):
    """Clear all items from history."""


##############################################################################
class DeduplicateHistory(Message):
    """Deduplicate the history."""


### history.py ends here
