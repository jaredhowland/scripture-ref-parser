"""Parser stage: converts tokens into parsed references."""

import re

from scripture_ref_parser.types import ParsedRef, Token

# Pattern for parsing number tokens
# Matches: chapter, chapter:verse, chapter-chapter, chapter:verse-verse, chapter:verse-chapter:verse
_NUM_PATTERN = re.compile(
    r"^(?P<start_chap>\d+)(?::(?P<start_verse>\d+))?(?:-(?P<end_chap>\d+)?(?::(?P<end_verse>\d+))?)?$"
)


def _parse_num_token(
    text: str,
) -> tuple[tuple[int, int | None], tuple[int, int | None]]:
    """Parse a NUM token into start and end tuples.

    Returns:
        (start, end) where each is (chapter, verse_or_None)
    """
    match = _NUM_PATTERN.match(text)
    if not match:
        # Fallback for unparseable
        return ((1, None), (1, None))

    start_chap = int(match.group("start_chap"))
    start_verse = (
        int(match.group("start_verse")) if match.group("start_verse") else None
    )
    end_chap_str = match.group("end_chap")
    end_verse_str = match.group("end_verse")

    # Determine end based on what's present
    if end_chap_str is None and end_verse_str is None:
        # Single reference: Gen 1 or Gen 1:1
        end_chap = start_chap
        end_verse = start_verse
    elif end_verse_str and not end_chap_str:
        # Verse range: Gen 1:1-3
        end_chap = start_chap
        end_verse = int(end_verse_str)
    elif end_chap_str and not end_verse_str:
        # Chapter range: Gen 1-3, or verse range like 1:1-3
        if start_verse is not None:
            # This is actually a verse range: 1:1-3
            end_chap = start_chap
            end_verse = int(end_chap_str)
        else:
            # Chapter range: 1-3
            end_chap = int(end_chap_str)
            end_verse = None
    else:
        # Full range: Gen 1:1-2:3
        end_chap = int(end_chap_str)
        end_verse = int(end_verse_str) if end_verse_str else None

    return ((start_chap, start_verse), (end_chap, end_verse))


def _is_book_number_prefix(num_text: str) -> bool:
    """Check if a NUM token is a book number prefix (1, 2, 3, etc.)."""
    return num_text.isdigit() and int(num_text) <= 4


def parse_tokens(tokens: list[Token]) -> list[ParsedRef]:
    """Parse a list of tokens into structured references.

    Args:
        tokens: List of Token objects from tokenizer

    Returns:
        List of ParsedRef objects
    """
    results: list[ParsedRef] = []
    current_book: str | None = None
    pending_book_tokens: list[Token] = []

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token.type == "BOOK":
            # Accumulate book name tokens (for "1 Nephi" etc.)
            pending_book_tokens.append(token)
            i += 1
            continue

        elif token.type == "NUM":
            # Check if this is a book number prefix (e.g., "1" in "1 Nephi")
            # Look ahead to see if next token is a BOOK token
            if (
                _is_book_number_prefix(token.text)
                and i + 1 < len(tokens)
                and tokens[i + 1].type == "BOOK"
            ):
                # This is a book number prefix - treat it as part of the book name
                pending_book_tokens.append(token)
                i += 1
                continue

            # We have a number - time to create a reference
            if pending_book_tokens:
                # Use accumulated book tokens
                book_text = " ".join(t.text for t in pending_book_tokens)
                current_book = book_text
                pending_book_tokens = []

            start, end = _parse_num_token(token.text)

            results.append(
                ParsedRef(
                    book_key=current_book,
                    start=start,
                    end=end,
                    raw=f"{current_book} {token.text}" if current_book else token.text,
                )
            )
            i += 1

        elif token.type == "SEP":
            # Separator - clear pending book tokens for semicolon (new reference)
            if token.text == ";":
                pending_book_tokens = []
            i += 1

        else:
            i += 1

    return results
