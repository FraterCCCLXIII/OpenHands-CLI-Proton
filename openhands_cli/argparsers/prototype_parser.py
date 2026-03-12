"""Argument parser for prototype subcommand."""

import argparse


def add_prototype_parser(
    subparsers: argparse._SubParsersAction,
) -> argparse.ArgumentParser:
    """Add prototype subcommand parser.

    Args:
        subparsers: The subparsers object to add the prototype parser to

    Returns:
        The prototype argument parser
    """
    prototype_parser = subparsers.add_parser(
        "prototype",
        help="Run the UI prototype app (experimental screens, dummy flows)",
    )
    prototype_parser.add_argument(
        "--demo",
        action="store_true",
        default=True,
        help="Use demo/mock data for flows without real backend (default: True)",
    )
    return prototype_parser
