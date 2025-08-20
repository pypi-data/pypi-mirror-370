"""Messages to do with the command line."""

##############################################################################
# Python imports.
from dataclasses import dataclass

##############################################################################
# Textual imports.
from textual.message import Message


##############################################################################
@dataclass
class HandleInput(Message):
    """Ask the command line to handle some input."""

    user_input: str
    """The input to handle as if the user had entered it."""


### command_line.py ends here
