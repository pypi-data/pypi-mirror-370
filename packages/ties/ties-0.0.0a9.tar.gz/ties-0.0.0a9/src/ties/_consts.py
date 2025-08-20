import sys

APP_NAME = "ties"
DEFAULT_SCRIPT_DIR = ".ties/"
SUCCESS = 0
ERROR = 1


# --- Terminal Colors & Emojis ---
class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


IS_TTY = sys.stdout.isatty()


def cprint(text: str, color: str | None = None, bold: bool = False) -> None:
    """Print colored text to the console."""
    if not IS_TTY:
        print(text)
        return
    style = Colors.BOLD if bold else ""
    color_code = color if color else ""
    end_code = Colors.END if color_code or style else ""
    print(f"{style}{color_code}{text}{end_code}")
