import textwrap
from typing import Any, List, Literal, Optional, Tuple, Union

ANSI_COLORS = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "orange": "\033[38;5;208m",
    "purple": "\033[38;5;93m",
    "pink": "\033[38;5;206m",
    "brown": "\033[38;5;94m",
    "gray": "\033[38;5;242m",
    "reset": "\033[0m",
}

PredefinedColor = Literal[
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
    "orange",
    "purple",
    "pink",
    "brown",
    "gray",
]


def _wrap_text(text: str, width: Optional[int]) -> str:
    all_lines: List[str] = []
    for line in text.splitlines():
        if width is not None and width > 0:
            wrapped = textwrap.wrap(line, width=width, replace_whitespace=False)
            if not wrapped:
                all_lines.append("")
            else:
                all_lines.extend(wrapped)
        else:
            all_lines.append(line)
    return "\n".join(all_lines)


def _process_color(
    name: Optional[Union[PredefinedColor, str]]
) -> Tuple[str, str]:
    ansi_color = ""
    ansi_reset = ""
    if name:
        ansi_color = ANSI_COLORS.get(name, name)
        ansi_reset = ANSI_COLORS["reset"]
    return ansi_color, ansi_reset


def print9(
    *objects: Any,
    wrap: Optional[int] = None,
    color: Optional[Union[PredefinedColor, str]] = None,
    **kwargs,
) -> None:
    """
    Prints multiple objects, with optional wrapping and coloring applied
    individually to each object's string representation.

    Args:
        *objects: The objects to print. Each will be converted to a string,
                  wrapped, and colored before being passed to the native print.
        wrap (Optional[int]): The maximum width to wrap each object's lines.
                              If None or <= 0, no wrapping is performed.
                              Defaults to None.
        color (Optional[Union[PredefinedColor, str]]): The color for each
                                                        object's text. Can be
                                                        a predefined name or a
                                                        custom ANSI color code.
                                                        If None, no color is
                                                        applied. Defaults to
                                                        None.
        **kwargs: Arbitrary keyword arguments passed directly to the
                  built-in print() function (e.g., 'sep', 'end', 'file',
                  'flush').
    """
    ansi_color, ansi_reset = _process_color(color)
    processed_objects: List[str] = []

    for object_item in objects:
        object_string = str(object_item)
        wrapped_object_string = _wrap_text(object_string, wrap)
        processed_objects.append(
            f"{ansi_color}{wrapped_object_string}{ansi_reset}"
        )

    print(*processed_objects, **kwargs)