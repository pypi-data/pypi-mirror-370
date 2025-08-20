"""Hike -- A Markdown viewer for the terminal."""

##############################################################################
# Python imports.
from importlib.metadata import version
from typing import Final

##############################################################################
# Main app information.
__author__ = "Dave Pearson"
__copyright__ = "Copyright 2025, Dave Pearson"
__credits__ = ["Dave Pearson"]
__maintainer__ = "Dave Pearson"
__email__ = "davep@davep.org"
__version__ = version("hike")
__licence__ = "GPLv3+"

##############################################################################
USER_AGENT: Final[str] = f"Hike v{__version__} (https://github.com/davep/hike)"
"""The user agent string for the viewer."""

### __init__.py ends here
