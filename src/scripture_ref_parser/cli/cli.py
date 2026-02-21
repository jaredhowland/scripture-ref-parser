"""Command-line interface for scripture reference parser."""

import json
import sys

import click

from scripture_ref_parser.api import parse_references


@click.command()
@click.argument("text")
@click.option(
    "--mode",
    type=click.Choice(["loose", "strict"]),
    default="loose",
    help="Matching mode: 'loose' allows fuzzy matching, 'strict' requires exact matches.",
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
def main(text: str, mode: str, all_candidates: bool, pretty: bool) -> None:
    """Parse scripture references and output OSIS ranges.

    TEXT is the scripture reference text to parse, e.g. "Gen 1:1-3; 1 Ne. 3:7"
    """
    try:
        results = parse_references(text, mode=mode, all_candidates=all_candidates)

        indent = 2 if pretty else None
        output = json.dumps(results, indent=indent)
        click.echo(output)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
