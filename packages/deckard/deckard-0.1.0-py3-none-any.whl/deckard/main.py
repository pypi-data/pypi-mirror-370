import regex
from typing import Iterable


def search(patterns: Iterable[str], string: str) -> regex.Match[str] | None:
    lookaheads = "".join(rf"(?:(?=.*?{p}))?" for p in patterns)
    combined = rf"(?s)^{lookaheads}.*$"
    return regex.search(combined, string)
