"""Type definitions for the scripture reference parser pipeline."""

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class Token:
    """A token from the tokenizer stage."""

    type: Literal["BOOK", "NUM", "SEP", "PUNC"]
    text: str
    span: tuple[int, int]


@dataclass
class CanonCandidate:
    """A candidate match from fuzzy matching."""

    key: str
    score: int


@dataclass
class NormalizedBook:
    """Result of book name normalization."""

    key: str | None
    mode: Literal["loose", "strict"]
    is_exact: bool = True
    candidates: list[CanonCandidate] | None = None


@dataclass
class ParsedRef:
    """A parsed scripture reference."""

    book_key: str | None
    start: tuple[int, int | None]  # (chapter, verse or None)
    end: tuple[int, int | None]  # (chapter, verse or None)
    raw: str
    errors: list[str] = field(default_factory=list)


@dataclass
class ResolvedRange:
    """A resolved OSIS range."""

    start: str | None
    end: str | None
    fuzzy_ratio: int | None = None
    not_found: str | None = None
