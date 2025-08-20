"""Application-wide types."""

##############################################################################
# Python imports.
from pathlib import Path
from typing import TypeAlias

##############################################################################
# httpx imports.
from httpx import URL

##############################################################################
# Textual enhanced imports.
from textual_enhanced.tools import History

##############################################################################
HikeLocation: TypeAlias = Path | URL
"""The type of a location."""

##############################################################################
HikeHistory: TypeAlias = History[HikeLocation]
"""The type of the browsing history."""

##############################################################################
CommandHistory: TypeAlias = History[str]
"""The type of the command history."""

### types.py ends here
