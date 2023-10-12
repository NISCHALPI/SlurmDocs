"""CLI for the slurmdocs database."""


import click
from ...database import SlurmClusterDatabase

__all__ = ['database']


# TO DO : Fill up the commands for the database subcommand.
@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
@click.option(
    '-db', '--database', required=True, help='The database to use.', type=click.STRING
)
@click.option(
    '-p', '--path', required=False, help='The path to the database.', type=click.STRING, default=SlurmClusterDatabase._defaut_path.absolute.__str__()
)
def database(ctx: click.Context, database: str, path : str) -> None:
    """Subcommand for the slurmdocs database operations."""
    ctx.obj['logger'].debug('Starting database subcommand.')

    #Create a database object 
    db = SlurmClusterDatabase(
        db_name=database,
        db_path=path
        )
    
    # Add to contex 
    ctx.obj['database'] = db

    print(ctx.obj['database'].db_name) 

    pass


@database.command()
@click.pass_context
def create(ctx: click.Context) -> None:
    """Create the database."""
    pass


@database.command()
@click.pass_context
def remove(ctx: click.Context, data: dict) -> None:
    """Remove the database."""
    pass


@database.command()
@click.pass_context
def coverage(ctx: click.Context) -> None:
    """Cover the database."""
    pass


@database.command()
@click.pass_context
def query(ctx: click.Context, query: dict) -> None:
    """Query the database."""
    pass


@database.command()
@click.pass_context
def list(ctx: click.Context) -> None:
    """List the databases."""
    pass


@database.command()
@click.pass_context
@click.option(
    '-db', '--database', required=True, help='Name of The Database', type=click.STRING
)
def integrity(ctx: click.Context, database: str) -> None:
    """Check the integrity of the database."""
    pass


@database.command()
@click.pass_context
def update(ctx: click.Context, query: dict) -> None:
    """Update the database."""
    pass
