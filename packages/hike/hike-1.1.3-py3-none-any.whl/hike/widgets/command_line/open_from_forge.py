"""Provides the command for opening a file from a forge."""

##############################################################################
# Python imports.
from re import Pattern, compile
from typing import Final

##############################################################################
# Textual imports.
from textual.widget import Widget

##############################################################################
# Local imports.
from ...data import load_configuration
from ...messages import OpenFromForge
from .base_command import InputCommand


##############################################################################
class OpenFromForgeCommand(InputCommand):
    """Base class for commands that open a file from a forge."""

    ARGUMENTS = "`<remote-file>`¹"

    WITHOUT_BRANCH: Final[Pattern[str]] = compile(
        r"^(?P<owner>[^/ ]+)[/ ](?P<repo>[^ :]+)(?: +(?P<file>[^ ]+))?$"
    )
    """Regular expression for finding forge details without a branch."""

    WITH_BRANCH: Final[Pattern[str]] = compile(
        r"^(?P<owner>[^/ ]+)[/ ](?P<repo>[^ :]+):(?P<branch>[^ ]+)(?: +(?P<file>[^ ]+))?$"
    )
    """Regular expression for finding forge details with a branch."""

    FORGE = ""
    """The name of the forge."""

    URL_FORMAT = ""
    """The format of the raw URL for the forge."""

    HELP = f"""
    | Format | Effect |
    | -- | -- |
    | `<owner>/<repo>` | Open `README.md` from a repository |
    | `<owner> <repo>` | Open `README.md` from a repository |
    | `<owner>/<repo> <file>` | Open a specific file from a repository |
    | `<owner> <repo> <file>` | Open a specific file from a repository |
    | `<owner>/<repo>:<branch>` | Open `README.md` from a specific branch of a repository |
    | `<owner> <repo>:<branch>` | Open `README.md` from a specific branch of a repository |
    | `<owner>/<repo>:<branch> <file>` | Open a specific file from a specific branch of a repository |
    | `<owner> <repo>:<branch> <file>` | Open a specific file from a specific branch of a repository |

    If `<branch>` is omitted the requested file is looked for in the following branches:
    {", ".join(f"`{branch}`" for branch in load_configuration().main_branches)}.
    """

    @classmethod
    def maybe_request(cls, arguments: str, for_widget: Widget) -> bool:
        """Maybe request a file be opened from the given forge.

        Args:
            arguments: The arguments to parse.
            for_widget: The widget to send the request to.

        Returns:
            `True` if the arguments could be parsed, `False` if not.
        """
        if details := cls.WITHOUT_BRANCH.match(arguments):
            for_widget.post_message(
                OpenFromForge(
                    cls.FORGE,
                    cls.URL_FORMAT,
                    details["owner"],
                    details["repo"],
                    filename=details["file"],
                )
            )
            return True
        if details := cls.WITH_BRANCH.match(arguments):
            for_widget.post_message(
                OpenFromForge(
                    cls.FORGE,
                    cls.URL_FORMAT,
                    details["owner"],
                    details["repo"],
                    details["branch"],
                    details["file"],
                )
            )
            return True
        return False

    @classmethod
    def handle(cls, text: str, for_widget: Widget) -> bool:
        """Handle the forge command.

        Args:
            text: The text of the command.
            for_widget: The widget to handle the command for.

        Returns:
            `True` if the command was handled; `False` if not.
        """
        command, arguments = cls.split_command(text)
        return cls.is_command(command) and cls.maybe_request(arguments, for_widget)


##############################################################################
class OpenFromBitbucket(OpenFromForgeCommand):
    """Open a file from Bitbucket"""

    COMMAND = "`bitbucket`"
    ALIASES = "`bb`"
    FORGE = "Bitbucket"
    URL_FORMAT = "https://bitbucket.org/{owner}/{repository}/raw/{branch}/{file}"


##############################################################################
class OpenFromCodeberg(OpenFromForgeCommand):
    """Open a file from Codeberg"""

    COMMAND = "`codeberg`"
    ALIASES = "`cb`"
    FORGE = "Codeberg"
    URL_FORMAT = "https://codeberg.org/{owner}/{repository}/raw//branch/{branch}/{file}"


##############################################################################
class OpenFromGitHub(OpenFromForgeCommand):
    """Open a file from GitHub"""

    COMMAND = "`github`"
    ALIASES = "`gh`"
    FORGE = "GitHub"
    URL_FORMAT = (
        "https://raw.githubusercontent.com/{owner}/{repository}/{branch}/{file}"
    )


##############################################################################
class OpenFromGitLab(OpenFromForgeCommand):
    """Open a file from GitLab"""

    COMMAND = "`gitlab`"
    ALIASES = "`gl`"
    FORGE = "GitLab"
    URL_FORMAT = "https://gitlab.com/{owner}/{repository}/-/raw/{branch}/{file}"


### open_from_forge.py ends here
