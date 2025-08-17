import os


def is_terminal_supports_hyperlink() -> bool:
    if "WT_SESSION" in os.environ:
        return True
    if os.environ.get("TERM_PROGRAM") == "iTerm.app":
        return True
    term = os.environ.get("TERM", "").strip().lower()
    if any(x in term for x in ["xterm", "gnome", "vte", "kitty", "wezterm"]):
        return True
    return False
