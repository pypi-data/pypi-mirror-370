"""Provides a function for viewing things in the browser."""

##############################################################################
# Python imports.
from functools import singledispatch
from pathlib import Path
from webbrowser import open as open_url

##############################################################################
# httpx imports.
from httpx import URL


##############################################################################
@singledispatch
def view_in_browser(location: object) -> None:
    """View a location in the OS's web browser.

    Args:
        location: The location to view.
    """


@view_in_browser.register
def _(location: Path) -> None:
    open_url(f"file://{location}", new=2, autoraise=True)


@view_in_browser.register
def _(location: URL) -> None:
    open_url(str(location), new=2, autoraise=True)


### view_in_browser.py ends here
