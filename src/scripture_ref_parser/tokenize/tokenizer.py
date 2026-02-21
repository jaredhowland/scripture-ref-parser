"""Tokenizer stage: converts raw text into candidate tokens."""

import re

from scripture_ref_parser.types import Token

# Pattern for tokenizing scripture references
# Captures: words (potential book names), numbers with verse notation, separators
_TOKEN_PATTERN = re.compile(
    r"""
    (?P<num>\d+(?::\d+)?(?:-\d+(?::\d+)?)?)  # Numbers with optional verse/range notation
    |(?P<sep>[;,])                            # List separators
    |(?P<dash>[—–-])                          # Range separators (em-dash, en-dash, hyphen)
    |(?P<word>[A-Za-z]+\.?)                   # Words (potential book names)
    """,
    re.VERBOSE,
)


def tokenize(text: str) -> list[Token]:
    """Tokenize scripture reference text into candidate tokens.

    Args:
        text: Raw scripture reference text

    Returns:
        List of Token objects with type, text, and span information
    """
    tokens: list[Token] = []

    for match in _TOKEN_PATTERN.finditer(text):
        span = (match.start(), match.end())
        matched_text = match.group()

        if match.group("num"):
            tokens.append(Token(type="NUM", text=matched_text, span=span))
        elif match.group("sep"):
            tokens.append(Token(type="SEP", text=matched_text, span=span))
        elif match.group("dash"):
            tokens.append(Token(type="PUNC", text=matched_text, span=span))
        elif match.group("word"):
            # Could be a book name or part of one
            # Strip trailing period but adjust span to match
            clean_text = matched_text.rstrip(".")
            adjusted_span = (span[0], span[0] + len(clean_text))
            tokens.append(Token(type="BOOK", text=clean_text, span=adjusted_span))

    return tokens
