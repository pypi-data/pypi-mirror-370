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
    *values: Any,
    wrap: Optional[int] = None,
    color: Optional[Union[PredefinedColor, str]] = None,
    **kwargs,
) -> None:
    """
    Prints the values to a stream, or to sys.stdout by default, with optional *text wrapping* and *terminal color*.
    
    wrap
      maximum width to wrap each value's lines.
    color
      text color, can be a predefined name or a custom ANSI color code.
      Predefined: black, red, green, yellow, blue, magenta, cyan, white, orange, purple, pink, brown, gray.

    sep
      string inserted between values, default a space.
    end
      string appended after the last value, default a newline.
    file
      a file-like object (stream); defaults to the current sys.stdout.
    flush
      whether to forcibly flush the stream.
    """
    ansi_color, ansi_reset = _process_color(color)
    processed_values: List[str] = []

    for value_item in values:
        value_string = str(value_item)
        wrapped_value_string = _wrap_text(value_string, wrap)
        processed_values.append(
            f"{ansi_color}{wrapped_value_string}{ansi_reset}"
        )

    print(*processed_values, **kwargs)
