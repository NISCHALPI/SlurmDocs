"""CLI for the slurmdocs database."""


import os
from pathlib import Path

import click

from ...database import SlurmClusterDatabase

__all__ = ["database"]


# Create the database subcommand
@click.group(no_args_is_help=True, invoke_without_command=True, name="database")
@click.version_option()
@click.pass_context
@click.option(
    "-p",
    "--path",
    required=False,
    help="The path to the database.",
    type=click.Path(),
    default=Path.home() / ".slurmdocs",
)
def database(ctx: click.Context, path: Path) -> None:
    """Subcommand for the slurmdocs database operations."""
    ctx.obj["logger"].debug("Starting database subcommand.")
    # Create the database object
    ctx.obj["database_path"] = path

    # If db_path does not exist, create it
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        ctx.obj["logger"].debug(f"Database {path} path created.")

    return


# Helper function to get the database object from the context
def get_database(ctx: click.Context, db_name: str) -> SlurmClusterDatabase:
    """Get the database object from the context."""
    return SlurmClusterDatabase(
        db_name=db_name,
        db_path=ctx.obj["database_path"],
    )


@database.command()
@click.pass_context
def avail(ctx: click.Context) -> None:
    """List the available databases."""
    # Get the database path from the context
    db_path = ctx.obj["database_path"]

    # List the databases
    dirs = [d for d in os.listdir(db_path)]

    # if no databases are found
    if len(dirs) == 0:
        print("No databases found.")
        return
    # List the databases in bulleted form with a emoji in front and emoji for integrity
    print("Available databases:")
    for d in dirs:
        db = SlurmClusterDatabase(db_name=d, db_path=db_path)
        print(
            f"""📁 {d}- {
            '✅' if not db.is_empty() and db.check_integrity(supress=True) else '❌'
        }"""
        )

    return


@database.command()
@click.pass_context
@click.option(
    "-db", "--database", required=True, help="The database to use.", type=click.STRING
)
def destroy(ctx: click.Context, database: str) -> None:
    """Destroy the database including it's subdirectory."""
    # Get the database
    db = get_database(ctx, database)
    # Destroy the database subdirectories
    db.delete()
    # Delete the parent directory
    db._delete(ctx.obj["database_path"] / database)

    # Print the success message
    print("Database destroyed successfully.")
    return


@database.command()
@click.pass_context
def clean(ctx: click.Context) -> None:
    """Clean the empty databases."""
    # Get all the databases
    dirs = [d for d in os.listdir(ctx.obj["database_path"])]

    counter = 0
    # Destroy the empty databases
    for d in dirs:
        db = SlurmClusterDatabase(db_name=d, db_path=ctx.obj["database_path"])
        if db.is_empty():
            counter += 1
            print(f"Deleting {d} database.")
            db._delete(ctx.obj["database_path"] / d)

    print(f"Succesfully cleaned {counter} databases.")


@database.command()
@click.pass_context
@click.option(
    "-db", "--database", required=True, help="The database to use.", type=click.STRING
)
def create(ctx: click.Context, database: str) -> None:
    """Create the database subdirectories."""
    # Get the database
    db = get_database(ctx, database)
    # Create the database
    db.create()
    return


@database.command()
@click.pass_context
@click.option(
    "-db", "--database", required=True, help="The database to use.", type=click.STRING
)
@click.option(
    "-k",
    "--key",
    required=True,
    help="The key for the database.(node | cpu)",
    type=click.STRING,
)
@click.option(
    "-f",
    "--filename",
    required=True,
    help="The filename to remove.",
    type=click.STRING,
)
@click.option(
    "-fp",
    "--filepath",
    required=True,
    help="The filepath to insert.",
    type=click.Path(exists=True, file_okay=True, readable=True, resolve_path=True),
)
def insert(
    ctx: click.Context, database: str, key: str, filename: str, filepath: str
) -> None:
    """Insert the file into the database."""
    # Get the database object
    db = get_database(ctx, database)

    # if empty database, create the database
    if db.is_empty():
        db.create()

    # Read the file
    with open(filepath) as f:
        file_content = f.read()

    # Insert the file into the database
    db.insert(query={"key": key, "filename": filename, "data": file_content})

    return


@database.command()
@click.pass_context
@click.option(
    "-db", "--database", required=True, help="The database to use.", type=click.STRING
)
@click.option(
    "-k",
    "--key",
    required=True,
    help="The key for the database.(node | cpu)",
    type=click.STRING,
)
@click.option(
    "-f",
    "--filename",
    required=True,
    help="The filename to remove.",
    type=click.STRING,
)
def remove(ctx: click.Context, database: str, key: str, filename: str) -> None:
    """Remove the entries from the database."""
    query_dict = {"key": key, "filename": filename}

    # Get the database object from the context
    db = get_database(ctx, database)

    # Remove file from the database
    db.remove(query_dict)

    return


@database.command()
@click.pass_context
@click.option(
    "-db", "--database", required=True, help="The database to use.", type=click.STRING
)
def coverage(ctx: click.Context, database: str) -> None:
    """Cover the database."""
    # Get the database object from the context
    db = get_database(ctx, database)

    # Cover the database
    try:
        print(f"Coverage: {db.coverage():.1f}%")
    except FileNotFoundError:
        print("Node file not found. Cannot calculate coverage.")

    return


@database.command()
@click.option(
    "-db", "--database", required=True, help="The database to use.", type=click.STRING
)
@click.option(
    "-k",
    "--key",
    required=True,
    help="The key for the database.(node | cpu)",
    type=click.STRING,
)
@click.option(
    "-f",
    "--filename",
    required=True,
    help="The filename to remove.",
    type=click.STRING,
)
@click.pass_context
def query(ctx: click.Context, database: str, key: str, filename: str) -> None:
    """Query the database."""
    # Get the database object from the context
    db = get_database(ctx, database)
    # Query the database
    query_dict = {"key": key, "filename": filename}

    # Print the query
    print(db.query(query_dict))

    return


@database.command()
@click.option(
    "-db", "--database", required=True, help="The database to use.", type=click.STRING
)
@click.pass_context
def list(ctx: click.Context, database: str) -> None:
    """List the databases tree structure."""
    # Get the database object from the context
    db = get_database(ctx, database)
    # List the databases
    db.print()

    return


@database.command()
@click.pass_context
@click.option(
    "-db", "--database", required=True, help="The database to use.", type=click.STRING
)
def integrity(ctx: click.Context, database: str) -> None:
    """Check the integrity of the database."""
    # Get the database object from the context
    db = get_database(ctx, database)
    # Check the integrity of the database
    db.check_integrity(supress=False)

    return


@database.command()
@click.pass_context
@click.option(
    "-db", "--database", required=True, help="The database to use.", type=click.STRING
)
@click.option(
    "-k",
    "--key",
    required=True,
    help="The key for the database.(node | cpu)",
    type=click.STRING,
)
@click.option(
    "-f",
    "--filename",
    required=True,
    help="The filename to remove.",
    type=click.STRING,
)
@click.option(
    "-fp",
    "--filepath",
    required=True,
    help="The filepath to insert.",
    type=click.Path(exists=True, file_okay=True, readable=True, resolve_path=True),
)
def update(
    ctx: click.Context, database: str, key: str, filename: str, filepath: str
) -> None:
    """Update the certan pre-exiting data file."""
    # Get the database object from the context
    db = get_database(ctx, database)

    # Query the database
    query_dict = {"key": key, "filename": filename, "data": filepath}

    # Update the database
    db.update(query_dict)

    return
