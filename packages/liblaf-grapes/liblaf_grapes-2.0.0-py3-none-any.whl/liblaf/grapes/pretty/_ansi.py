def has_ansi(s: str, /) -> bool:
    return "\x1b" in s
