from typing import Literal

from .config import _logger, _base_log_level, LogLevel

# ==========================================================================================
#                                       LOGGER
# ==========================================================================================

def print_log(
    text: str, 
    end: str = "\n", 
    log_level: LogLevel = _base_log_level
) -> None:
    if _logger:
        # get he correct level and if not listed use info
        log_func = getattr(_logger, log_level, _logger.info)
        log_func(text)
    else:
        print(text, end=end)


# ==========================================================================================
#                                       GENERAL
# ==========================================================================================
_separators_max_length = 128
_separators = {
    "short" : "_"*int(_separators_max_length/4),
    "normal": "_"*int(_separators_max_length/2),
    "long"  : "_"*int(_separators_max_length),
    "super" : "="*int(_separators_max_length),
    "start" : "="*int(_separators_max_length),
}
SepType = Literal["SHORT", "NORMAL", "LONG", "SUPER", "START"]

_colors = {
    "red":    "\033[31m",
    "green":  "\033[32m",
    "yellow": "\033[33m",
    "blue":   "\033[34m",
    "white":  "\033[0m",
}
Colors = Literal["red", "green", "blue", "yellow", "white"]

def print_separator(text: str = None, sep_type: SepType = "NORMAL") -> None:
    """Prints a text with a line that separes the bash outputs. The size of this line is controled by sep_type

    Args:
        text (str): Text to print.
        sep_type (Literal['SHORT', 'NORMAL', 'LONG', 'SUPER', 'START'], optional): Type of the separation line. Defaults to "NORMAL".
    """

    sep = _separators.get(sep_type.lower(), "") # If the separator is not there do it with ''
    if not sep:
        print_warn("WARNING: No separator with that label")

    if sep_type == "SUPER":
        print_log(sep)
        if text:
            print_log(f"{text:^{len(sep)}}")
        print_log(sep + "\n")
    elif sep_type == "START":
        print_color(sep + "\n", color="blue")
        if text:
            print_color(f"{text:^{len(sep)}}\n", color="blue")
        print_color(sep + "\n", color="blue")
    else:
        print_log(sep)
        if text:
            print_log(f"{text:^{len(sep)}}\n")


def print_color(text: str, color: Colors = "white", log_level: LogLevel = 'info', print_text: bool = True) -> str:
    """Prints the text with a certain color

    Args:
        text (str): Text to print
        color (Literal['red', 'green', 'blue', 'white'], optional): Color to use. Defaults to "white".
        print_text bool: Whether or not to print the color text (if false it will return it)

    Return: 
        str: Text with colors
    """
    color =  _colors.get(color, _colors['white'])
    text: str = f"{color}{text}{_colors['white']}"

    if print_text:
        print_log(f"{text}", log_level=log_level)

    return text


def print_warn(text: str, color: Colors = "yellow") -> str:
    """Adds the text between teh following emoji ⚠️...⚠️

    Args:
        text (str): Text to print in warn
        color (Colors, optional): Color of the warning text. Defaults to "yellow".

    Returns:
        str: Text with color and emojis
    """
    return print_color(f"⚠️{text}⚠️", color=color, log_level="warning")

def print_error(text: str, color: Colors = "red") -> str:
    """Adds the text between teh following emoji ❌...❌

    Args:
        text (str): Text to print in warn
        color (Colors, optional): Color of the error text. Defaults to "red".

    Returns:
        str: Text with color and emojis
    """
    return print_color(f"❌{text}❌", color=color, log_level="warning")


# ==========================================================================================
#                                    CLEAR LINES
# ==========================================================================================
def print_status(msg: str, log_level: LogLevel = _base_log_level):
    """Prints a dynamic status message on the same terminal line.

    Useful for updating progress or status in-place (e.g. during loops),
    preventing multiple lines of output.

    Args:
        msg (str): Message to display.
    """
    clear_line = " " * _separators_max_length  # assume max 120 chars per line
    print_log(f"{clear_line}\r{msg}\r", end="\r", log_level=log_level)

def clear_status(log_level: LogLevel = _base_log_level):
    """Clears the previous status line
    """
    print_status("", log_level=log_level)

def clear_bash(n_lines: int = 1) -> None:
    """Cleans the bash output by removing the last n lines.

    Args:
        n_lines (int, optional): Number of lines to remove. Defaults to 1.
    """
    print_log("\033[F\033[K"*n_lines, end="")  # Move cursor up one line and clear that line

def print_clear_bash(text: str, n_lines: int = 1, log_level: LogLevel = _base_log_level) -> None:
    """Cleans the bash output by removing the last n lines.

    Args:
        n_lines (int, optional): Number of lines to remove. Defaults to 1.
    """
    clear_bash(n_lines)
    print_log(text, log_level=log_level)