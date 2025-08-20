"""Functions for testing location types."""

##############################################################################
# Python imports.
from functools import singledispatch
from pathlib import Path

##############################################################################
# httpx imports.
from httpx import URL

##############################################################################
from typing_extensions import TypeIs

##############################################################################
# Local imports.
from ..types import HikeLocation
from .config import load_configuration


##############################################################################
@singledispatch
def maybe_markdown(location: object) -> bool:
    """Does the given location look like it might be a Markdown file?

    Args:
        location: The location to test.

    Returns:
        `True` if the location looks like it's Markdown, `False` if not.
    """
    return False


##############################################################################
@maybe_markdown.register
def _(location: Path) -> bool:
    return location.suffix.lower() in load_configuration().markdown_extensions


##############################################################################
@maybe_markdown.register
def _(location: str) -> bool:
    return maybe_markdown(Path(location))


##############################################################################
@maybe_markdown.register
def _(location: URL) -> bool:
    return maybe_markdown(location.path)


##############################################################################
def looks_urllike(candidate: str) -> bool:
    """Does the given value look like a URL?

    Args:
        candidate: The candidate to test.

    Returns:
        `True` if the string looks like a URL, `False` if not.
    """
    return (url := URL(candidate)).is_absolute_url and url.scheme in ("http", "https")


##############################################################################
def is_editable(location: HikeLocation) -> TypeIs[Path]:
    """Is the given location one that can be edited?

    Args:
        location: The location to test.

    Returns:
        `True` if the location can be edited, `False` if not.
    """
    return isinstance(location, Path)


### location_types.py ends here
