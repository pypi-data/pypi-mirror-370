"""Messages to do with the local view of files."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from pathlib import Path

##############################################################################
# Textual imports.
from textual.message import Message


##############################################################################
@dataclass
class SetLocalViewRoot(Message):
    """Set the local view's root to a directory."""

    root: Path
    """The root directory to set."""


### local_view.py ends here
