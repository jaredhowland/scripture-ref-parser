"""Command-line interface for scripture reference parser."""

import json
import sys
from typing import Literal

import click

from scripture_ref_parser.api import parse_references


@click.command(
    help=(
        "Parse scripture reference text and output OSIS ranges.\n\n"
        "This CLI accepts freeform scripture references (examples: \"Gen 1:1-3\", "
        "\"1 Ne. 3:7\", \"Exodis 1:1\") and returns OSIS-style start/end "
        "identifiers such as 'Gen.1.1'. By default the parser runs in 'loose' "
        "mode, which enables fuzzy-book-name matching. Use `--mode strict` to "
        "require exact book name matches.\n\n"
        "Output is JSON. Use `--pretty` to pretty-print. Use `--all-candidates` "
        "to return all fuzzy-match candidates instead of only the top match.\n\n"
        "Examples:\n  scripture-ref-parser \"Gen 1:1-3; 1 Ne. 3:7\" --pretty\n"
        "  scripture-ref-parser \"Exodis 1:1\" --mode loose\n"
        "  scripture-ref-parser \"E 1:1\" --all-candidates --pretty\n"
    ),
)
@click.argument("text")
@click.option(
    "--mode",
    type=click.Choice(["loose", "strict"]),
    default="loose",
    help="Matching mode: 'loose' allows fuzzy matching, 'strict' requires exact matches.",
)
@click.option(
    "--loose",
    is_flag=True,
    default=False,
    help="Shorthand for `--mode loose` (mutually exclusive with `--strict`).",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Shorthand for `--mode strict` (mutually exclusive with `--loose`).",
)
@click.option(
    "--all-candidates",
    is_flag=True,
    default=False,
    help="Return all fuzzy match candidates instead of just the top match.",
)
@click.option(
    "--pretty",
    is_flag=True,
    default=False,
    help="Pretty-print JSON output.",
)
def main(
    text: str,
    mode: str,
    loose: bool,
    strict: bool,
    all_candidates: bool,
    pretty: bool,
) -> None:
    """Entry point for the CLI command.

    `--help` shows usage, examples, and available options. Provide the
    scripture reference text as the single positional `TEXT` argument.
    """
    try:
        # Resolve mode: explicit flags take precedence, mutual-exclusion enforced
        if loose and strict:
            click.echo("Error: --loose and --strict are mutually exclusive", err=True)
            sys.exit(2)

        if loose:
            mode_literal: Literal["loose", "strict"] = "loose"
        elif strict:
            mode_literal = "strict"
        else:
            # Cast mode to Literal type for type checker
            mode_literal = "loose" if mode == "loose" else "strict"
        results = parse_references(
            text, mode=mode_literal, all_candidates=all_candidates
        )

        indent = 2 if pretty else None
        output = json.dumps(results, indent=indent)
        click.echo(output)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
