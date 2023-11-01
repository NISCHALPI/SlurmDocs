"""Module for slurmdocs database operations.

This module provides a command-line interface for collecting data from a cluster using SSH.
It includes subcommands for collecting node information and CPU information.

"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import click

from ...collecter import Collecter, IlscpuCollecter, IscontrolColllecter
from ...database import SlurmClusterDatabase
from ...session import SSHSessionAuth

__all__ = ["collect"]


# TO DO : Fill up the commands for the database subcommand.
@click.group(invoke_without_command=True)
@click.pass_context
@click.option(
    "-u", "--username", required=True, help="The username to use.", type=click.STRING
)
@click.option(
    "-s", "--server", required=True, help="The server to use.", type=click.STRING
)
@click.option(
    "-p", "--port", required=False, help="The port to use.", type=click.INT, default=22
)
@click.option(
    "-k",
    "--key-path",
    required=False,
    help="The key to use.",
    type=click.Path(exists=True, readable=True, resolve_path=True),
    default=Path.home() / ".ssh" / "id_rsa",
)
def collect(
    ctx: click.Context, username: str, server: str, port: int, key_path: str
) -> None:
    """Subcommand for the slurmdocs database operations."""
    ctx.obj["logger"].debug("Starting collect subcommand.")

    # Create an SSH session | Lazy connect | # TO DO : Add password authentication
    session = SSHSessionAuth(
        server=server,
        remote_username=username,
        port=port,
        use_key_base_aut=True,
        path_to_priv_key=key_path,
        no_ping=False,
    )
    ctx.obj["logger"].debug("Lazy SSH session created.")

    # Add to contex the session
    ctx.obj["session"] = session
    # Close after subcommand execution
    ctx.call_on_close(session.close)
    return


@collect.command()
@click.pass_context
@click.option(
    "-save",
    "--save-dir",
    required=False,
    help="The directory to save the collection.",
    type=click.Path(exists=True, readable=True, resolve_path=True),
    default=Path.cwd(),
)
def node(ctx: click.Context, save_dir: str) -> None:
    """Collect the node info file from the cluster."""
    # Create a Collecter
    collecter = Collecter(
        icollecter=IscontrolColllecter(timeout=10),
        save_dir=save_dir,
    )

    # Connect to the cluster
    ctx.obj["session"].connect()

    # Collect the data
    collecter(session=ctx.obj["session"], filename="node_info.txt")

    return


@collect.command()
@click.pass_context
@click.option(
    "-n",
    "--node-name",
    required=True,
    help="The node name to collect CPU info.",
    type=click.STRING,
)
@click.option(
    "-p",
    "--partition",
    required=False,
    help="The partition to collect CPU info.",
    type=click.STRING,
    default="debug",
)
@click.option(
    "-qos",
    "--quality-of-service",
    required=False,
    help="The quality of service to use to collect CPU info.",
    type=click.STRING,
    default="debug",
)
@click.option(
    "-save",
    "--save-dir",
    required=False,
    help="The directory to save the collection.",
    type=click.Path(exists=True, readable=True, resolve_path=True),
    default=Path.cwd(),
)
def cpu(
    ctx: click.Context,
    node_name: str,
    partition: str,
    quality_of_service: str,
    save_dir: str,
) -> None:
    """Collect CPU information for a specific node."""
    # Create a Collecter
    collecter = Collecter(icollecter=IlscpuCollecter(timeout=10), save_dir=save_dir)

    # Connect to the cluster
    ctx.obj["session"].connect()

    # Collect the cpu info
    collecter(
        session=ctx.obj["session"],
        filename=f"{node_name}.txt",
        partition=partition,
        qos=quality_of_service,
        node=node_name,
    )

    return


@collect.command()
@click.pass_context
@click.option(
    "-db",
    "--database",
    required=True,
    help="The database to populate.",
    type=click.STRING,
)
@click.option(
    "-p",
    "--db-path",
    required=False,
    help="The path to the database.",
    type=click.Path(exists=True, readable=True, resolve_path=True, path_type=Path),
    default=Path.home() / ".slurmdocs",
)
@click.option(
    "-t",
    "--threads",
    required=False,
    help="The number of threads to use for collection.",
    type=click.INT,
    default=10,
)
@click.option(
    "-p",
    "--partition",
    required=False,
    help="The partition to collect CPU info.",
    type=click.STRING,
    default="debug",
)
@click.option(
    "-qos",
    "--quality-of-service",
    required=False,
    help="The quality of service to use to collect CPU info.",
    type=click.STRING,
    default="debug",
)
@click.option(
    "-o",
    "--override",
    required=False,
    help="Override the auto partitioning and use the supplied partition",
    type=click.BOOL,
    default=False,
)
def sweep(
    ctx: click.Context,
    database: str,
    db_path: str,
    threads: int,
    partition: str,
    quality_of_service: str,
    override: bool,
) -> None:
    """Populate the database with all the collected data. Database must be empty."""
    # Get the database
    db = SlurmClusterDatabase(db_name=database, db_path=db_path)

    # Check if the database is empty
    if not db.is_empty():
        raise ValueError(
            "Database is not empty. Use the delete command to delete the database."
        )

    # Create the database
    db.create()

    # Get the session
    session = ctx.obj["session"]
    # Connect to the cluster
    session.connect()

    # Create a Collecter
    collecter = Collecter(
        icollecter=IscontrolColllecter(timeout=10), save_dir=db.db_path / "node"
    )

    # Collect the node info
    collecter(
        session=session,
        filename="node_info.txt",
    )

    # Swap the Icollecter
    collecter._icollecter = IlscpuCollecter(timeout=10)
    collecter._save_dir = db.db_path / "cpu"

    # Get the node names and partitions from node file
    node_db = db.get_node_file()

    # Create a thread pool executor for multithreaded collection
    with ThreadPoolExecutor(max_workers=threads) as executor:
        # Get the valid partitions
        valid_partitions = [
            part
            for part in node_db.columns
            if part.endswith("_PRT") and not part.isupper()
        ]
        # Collect the cpu info
        for idx, noderw in node_db.iterrows():
            for part in valid_partitions:
                # If override is false , use auto partitioning
                if not override:
                    if noderw[part]:
                        executor.submit(
                            collecter,
                            session=session,
                            filename=f"{noderw['NodeName']}.txt",
                            partition=part[:-3],
                            qos=part[:-3],
                            node=noderw["NodeName"],
                        )
                        continue
                else:
                    executor.submit(
                        collecter,
                        session=session,
                        filename=f"{noderw['NodeName']}.txt",
                        partition=partition,
                        qos=quality_of_service,
                        node=noderw["NodeName"],
                    )
                    continue

    return
