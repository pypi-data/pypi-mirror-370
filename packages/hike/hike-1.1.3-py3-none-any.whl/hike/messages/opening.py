"""Messages to do with opening things."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from pathlib import Path

##############################################################################
# httpx imports.
from httpx import URL, AsyncClient, HTTPStatusError, RequestError

##############################################################################
# Textual imports.
from textual.message import Message

##############################################################################
# Local imports.
from .. import USER_AGENT
from ..data import load_configuration
from ..types import HikeLocation


##############################################################################
@dataclass
class OpenFrom(Message):
    """Open a file starting at a particular location."""

    location: Path = Path(".")
    """The location to start browsing for a file."""


##############################################################################
@dataclass
class OpenLocation(Message):
    """Open a given location for viewing."""

    to_open: HikeLocation
    """The location to open."""


##############################################################################
@dataclass
class OpenFromHistory(Message):
    """Open a location found in history."""

    location: int
    """The location in the history to open."""


##############################################################################
@dataclass
class OpenFromForge(Message):
    """Open a file from a forge."""

    forge: str
    """The name of the forge."""

    raw_url_format: str
    """The format of the raw URL for the forge."""

    owner: str
    """The owner of the repository to open from."""

    repository: str
    """The repository to open the file from."""

    branch: str | None = None
    """The optional branch to open from."""

    filename: str | None = None
    """The optional name of the file to open."""

    async def url(self) -> URL | None:
        """The URL for the file on the forge.

        Returns:
            The URL if one could be worked out, or `None` if not.
        """
        filename = self.filename or "README.md"
        async with AsyncClient() as client:
            for candidate_branch in (
                [self.branch] if self.branch else load_configuration().main_branches
            ):
                url = self.raw_url_format.format(
                    owner=self.owner,
                    repository=self.repository,
                    branch=candidate_branch,
                    file=filename,
                )
                try:
                    response = await client.head(
                        url, follow_redirects=True, headers={"user-agent": USER_AGENT}
                    )
                except RequestError:
                    # A failed request would suggest further attempts aren't
                    # going to work so let's GTFO now.
                    return None
                try:
                    response.raise_for_status()
                except HTTPStatusError:
                    # Some sort of status error means we at least managed to
                    # contact the server, but didn't quite hit it with the
                    # URL we had; so let's go around again.
                    continue
                # If we're here we got a working URL, so let's go with that.
                return URL(url)
        return None


### opening.py ends here
