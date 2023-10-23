"""CLI for stats module."""


from pathlib import Path
from ...statistics import Statistics , IcpuStats , IgpuStats
import click
from ...database import SlurmClusterDatabase

__all__ = ['stats']



@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
@click.option(
    "-p",
    "--path",
    required=False,
    help="The path to the database.",
    type=click.Path(path_type=Path),
    default=Path.home() / ".slurmdocs"
)
@click.option(
    "-db", "--database", required=True, help="The database to use.", type=click.STRING
)
def stats(ctx : click.Context , path : Path,  database : str) -> None:
    """_summary_.

    Args:
        ctx (click.Context): _description_
        path (Path): _description_
        database (str): _description_
    """
    ctx.obj["logger"].debug("Starting stats subcommand.")
    
    db = SlurmClusterDatabase(
        db_name=database,
        db_path=path,
    )
    # Create the database object and add to context
    ctx.obj["db"] = db
    
    # Raise error if database is empty
    if db.is_empty() and not db.check_integrity():
        raise click.ClickException(
            "Database is empty or corrupted. Please run slurmdocs collect and create a databse."
        )
         
    return



@stats.command()
@click.pass_context
def tflops(ctx : click.Context) -> None:
    """_summary_

    Args:
        ctx (click.Context): _description_
    """

    pass
