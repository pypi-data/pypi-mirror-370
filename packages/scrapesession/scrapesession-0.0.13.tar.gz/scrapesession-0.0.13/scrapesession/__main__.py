"""The CLI for interfacing to the scrape session."""

import argparse
import logging

from . import __VERSION__
from .functions import Function
from .scrapesession import create_scrape_session


def main() -> None:
    """The main CLI function."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--name",
        required=True,
        help="The name of the cache to use.",
    )
    parser.add_argument(
        "function",
        choices=list(Function),
        help="The function to perform.",
    )
    parser.add_argument(
        "urls",
        action="store",
        type=str,
        nargs="+",
        help="The URLs to perform the function on.",
    )
    args = parser.parse_args()

    logging.info("--- scrapesession %s ---", __VERSION__)

    session = create_scrape_session(name=args.name)
    if args.function == str(Function.DELETE):
        session.cache.delete(urls=args.urls)


if __name__ == "__main__":
    main()
