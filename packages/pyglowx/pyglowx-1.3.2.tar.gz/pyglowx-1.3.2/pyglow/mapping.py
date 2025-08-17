import difflib
from typing import Union, Optional, Any

ANSI_RESET = "\u001B[0m"

FOREGROUND_COLORS = {
    "black": "\u001B[30m",
    "red": "\u001B[31m",
    "green": "\u001B[32m",
    "yellow": "\u001B[33m",
    "blue": "\u001B[34m",
    "magenta": "\u001B[35m",
    "cyan": "\u001B[36m",
    "white": "\u001B[37m",
    "bright-black": "\u001B[90m",
    "bright-red": "\u001B[91m",
    "bright-green": "\u001B[92m",
    "bright-yellow": "\u001B[93m",
    "bright-blue": "\u001B[94m",
    "bright-magenta": "\u001B[95m",
    "bright-cyan": "\u001B[96m",
    "bright-white": "\u001B[97m"
}

BACKGROUND_COLORS = {
    "bg-black": "\u001B[40m",
    "bg-red": "\u001B[41m",
    "bg-green": "\u001B[42m",
    "bg-yellow": "\u001B[43m",
    "bg-blue": "\u001B[44m",
    "bg-magenta": "\u001B[45m",
    "bg-cyan": "\u001B[46m",
    "bg-white": "\u001B[47m",
    "bg-bright-black": "\u001B[100m",
    "bg-bright-red": "\u001B[101m",
    "bg-bright-green": "\u001B[102m",
    "bg-bright-yellow": "\u001B[103m",
    "bg-bright-blue": "\u001B[104m",
    "bg-bright-magenta": "\u001B[105m",
    "bg-bright-cyan": "\u001B[106m",
    "bg-bright-white": "\u001B[107m"
}

STYLES = {
    "bold": "\u001B[1m",
    "dim": "\u001B[2m",
    "italic": "\u001B[3m",
    "underline": "\u001B[4m",
    "blink": "\u001B[5m",
    "reverse": "\u001B[7m",
    "hidden": "\u001B[8m",
    "strike": "\u001B[9m"
}


def preprocess(text: str) -> str:
    return text.strip()


def get_closest_match(tag: str) -> str:
    all_mappings = list(FOREGROUND_COLORS.keys()) + list(BACKGROUND_COLORS.keys()) + list(STYLES.keys())
    matches = difflib.get_close_matches(preprocess(tag), all_mappings, n=3, cutoff=0.7)
    return matches[0] if matches else None


def contains_foreground_color(tag: str) -> bool:
    return preprocess(tag) in FOREGROUND_COLORS


def contains_background_color(tag: str) -> bool:
    return preprocess(tag) in BACKGROUND_COLORS


def contains_style(tag: str) -> bool:
    return preprocess(tag) in STYLES


def get_foreground_color(tag: str) -> Union[Optional[str], Any]:
    return FOREGROUND_COLORS.get(preprocess(tag), f"{tag} not found")


def get_background_color(tag: str) -> str:
    return BACKGROUND_COLORS.get(preprocess(tag), f"{tag} not found")


def get_style(tag: str) -> str:
    return STYLES.get(preprocess(tag), f"{tag} not found")
