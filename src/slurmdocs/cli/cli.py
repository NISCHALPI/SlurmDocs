"""CLI for slurmdocs."""


import logging
import os
import sys

import click

from .submodules.collect_cli import collect
from .submodules.db_cli import database
from .submodules.stats_cli import stats

# Set up logging.
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    level=logging.WARNING,
    handlers=[logging.StreamHandler(sys.stdout)],
)


def get_logger(name: str, level: int = 40) -> logging.Logger:
    """Retrieves a logger instance with the specified name.

    Parameters:
        name (str): The name of the logger.
        level (int): The level of the logger.

    Returns:
        logging.Logger: A logger instance with the specified name.
    """
    # Get level from environment if if
    if os.getenv("LOG") is not None:
        level = int(os.getenv("LOG"))  # type: ignore

    logger = logging.getLogger(name=name)

    logger.setLevel(level=level)  # type: ignore

    return logger


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.version_option()
@click.pass_context
@click.option(
    "-d", "--debug", is_flag=True, default=False, help="Enable debug logging."
)
def main(
    ctx: click.Context,
    debug: bool = False,
) -> None:
    """Slurmdocs CLI for collecting and analyzing SLURM cluster."""
    ctx.ensure_object(dict)

    # Get the logger.
    if debug:
        logger = get_logger("slurmdocs", level=logging.DEBUG)
    else:
        logger = get_logger("slurmdocs")

    # Add the logger to the context.
    ctx.obj["logger"] = logger

    # Enable debug logging if specified.
    logger.debug("Starting CLI.")

    return


# Add the subcommands.
main.add_command(database, "database")

# Add collect subcommands.
main.add_command(collect, "collect")

# Add stats subcommands.
main.add_command(stats, "stats")

if __name__ == "__main__":
    main()
