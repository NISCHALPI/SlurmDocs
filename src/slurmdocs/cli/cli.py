"""CLI for slurmdocs."""


import logging
import os
import pathlib
import sys

import click

# Set up logging.
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    level=logging.WARNING,
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Create a base directory for slurmdocs.
if not os.path.exists(os.path.join(os.path.expanduser("~"), ".slurmdocs", "database")):
    os.mkdir(os.path.join(os.path.expanduser("~"), ".slurmdocs", "database"))


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
    '-db',
    '--database',
    type=click.Path(exists=True , writable=True, readable=True, resolve_path=True, path_type=pathlib.Path),
    default=os.path.join(os.path.expanduser("~"), ".slurmdocs", "database"),
    help='Path to the database.(Default: ~/.slurmdocs/database/)',
)
@click.option(
    '-d', '--debug', is_flag=True, default=False, help='Enable debug logging.'
)
def main(
    ctx: click.Context,
    database: click.Path,
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



if __name__ == "__main__":
    main()