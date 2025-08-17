import re
from .mapping import (
    ANSI_RESET,
    contains_foreground_color,
    contains_background_color,
    contains_style,
    get_foreground_color,
    get_background_color,
    get_style,
    get_closest_match
)
from .utils import is_terminal_supports_hyperlink

rgb_pattern = re.compile(r"^rgb\((\d{1,3}),(\d{1,3}),(\d{1,3})\)$")
hex_pattern = re.compile(r"^hex\(#([A-Fa-f0-9]{6})\)$")


class PyGlowParser:
    @staticmethod
    def parse_recursively(input_str: str, start=0):
        output = []
        i = start

        while i < len(input_str):
            if input_str.startswith("[/", i):
                end = input_str.find("]", i)
                if end == -1:
                    break
                return "".join(output), end + 1

            if input_str[i] == '[':
                end = input_str.find("]", i)
                if end == -1:
                    break

                tag_string = input_str[i + 1:end].strip()
                tag_lower = tag_string.lower()

                if tag_lower.startswith("link="):
                    url = tag_string[5:]
                    inner_result, next_index = PyGlowParser.parse_recursively(input_str, end + 1)

                    if is_terminal_supports_hyperlink():
                        output.append(f"\033]8;;{url}\033\\{inner_result}\033]8;;\033\\")
                    else:
                        output.append(f"\033]8;;{url}\033\\{inner_result}\033]8;;\033\\")
                    i = next_index
                    continue

                tags = tag_string.split()
                ansi = []

                for tag in tags:
                    tag_lower = tag.lower()
                    rgb_match = rgb_pattern.match(tag_lower)
                    hex_match = hex_pattern.match(tag_lower)

                    if rgb_match:
                        r, g, b = map(int, rgb_match.groups())
                        ansi.append(f"\u001b[38;2;{r};{g};{b}m")
                    elif hex_match:
                        hex_code = hex_match.group(1)
                        r = int(hex_code[0:2], 16)
                        g = int(hex_code[2:4], 16)
                        b = int(hex_code[4:6], 16)
                        ansi.append(f"\u001b[38;2;{r};{g};{b}m")
                    elif contains_foreground_color(tag_lower):
                        ansi.append(get_foreground_color(tag_lower))
                    elif contains_background_color(tag_lower):
                        ansi.append(get_background_color(tag_lower))
                    elif contains_style(tag_lower):
                        ansi.append(get_style(tag_lower))
                    else:
                        suggestion = get_closest_match(tag_lower)
                        if suggestion is not None:
                            return f"{tag} not found. Did you mean {suggestion}?", i
                        else:
                            raise ValueError(f"tag {tag} not found.")

                inner_result, next_index = PyGlowParser.parse_recursively(input_str, end + 1)
                output.append("".join(ansi))
                output.append(inner_result)
                output.append(ANSI_RESET)
                i = next_index

            else:
                output.append(input_str[i])
                i += 1

        return "".join(output), i
