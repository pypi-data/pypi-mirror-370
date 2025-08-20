"""Mouse support functions."""

##############################################################################
# Textual imports.
from textual.events import Click


##############################################################################
def is_copy_request_click(event: Click) -> bool:
    """Does the mouse click look like it's a copy request?

    Args:
        event: The mouse click event.

    Returns:
        `True` if the click was a copy request, `False` if not.
    """
    return (event.chain == 1 and event.ctrl) or (event.chain == 3 and not event.ctrl)


### mouse.py ends here
