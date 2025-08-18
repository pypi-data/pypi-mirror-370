# color print for shell

COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "reset": "\033[0m",
}


def cprint(text: str, color="white", end="\n") -> None:
    """
    Print text in color
    Args:
        text: Text to print
        color: Color to print in, color options are
            red, green, yellow, blue, magenta, cyan, white, reset
        end: End character
    """
    print(COLORS[color] + text + COLORS["reset"], end=end)
