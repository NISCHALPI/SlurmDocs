"""CLI for slurmdocs."""


import logging
import os
import sys

import click

from .submodules.collect_cli import collect
from .submodules.db_cli import database

# Set up logging.
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    level=logging.WARNING,
    handlers=[logging.StreamHandler(sys.stdout)],
)


def get_logger(name: str) -> logging.Logger:
    """Retrieves a logger instance with the specified name.

    Parameters:
        name (str): The name of the logger.

    Returns:
        logging.Logger: A logger instance with the specified name.
    """
    # Default level
    level = 40  # ERROR LEVEL

    # Get level from environment if present
    if os.getenv("LOG") is not None:
        level = int(os.getenv("LOG"))  # type: ignore

    logger = logging.getLogger(name=name)

    logger.setLevel(level=level)  # type: ignore

    return logger


# Get the logger.
logger = get_logger(name=__name__)


@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
@click.option(
    '-d', '--debug', is_flag=True, default=False, help='Enable debug logging.'
)
def main(
    ctx: click.Context,
    debug: bool = False,
) -> None:
    """Slurmdocs CLI."""
    ctx.ensure_object(dict)
    # Add the logger to the context.
    ctx.obj["logger"] = logger
    # Add the debug flag to the context.
    ctx.obj["debug"] = debug

    # Enable debug logging if specified.
    if ctx.obj["debug"]:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled.")

    # Enable debug logging if specified.
    logger.debug("Starting CLI.")

    return


# Add the subcommands.
main.add_command(database, 'database')

# Add collect subcommands.
main.add_command(collect, 'collect')

if __name__ == "__main__":
    main()
