"""Module for slurmdocs database operations.

This module provides a command-line interface for collecting data from a cluster using SSH.
It includes subcommands for collecting node information and CPU information.

"""
from pathlib import Path

import click

from ...collecter import Collecter, IlscpuCollecter, IscontrolColllecter
from ...session import SSHSessionAuth

__all__ = ['collect']


# TO DO : Fill up the commands for the database subcommand.
@click.group(invoke_without_command=True)
@click.pass_context
@click.option(
    '-u', '--username', required=True, help='The username to use.', type=click.STRING
)
@click.option(
    '-s', '--server', required=True, help='The server to use.', type=click.STRING
)
@click.option(
    '-p', '--port', required=False, help='The port to use.', type=click.INT, default=22
)
@click.option(
    '-k',
    '--key-path',
    required=False,
    help='The key to use.',
    type=click.Path(exists=True, readable=True, resolve_path=True),
    default=Path.home() / '.ssh' / 'id_rsa',
)
def collect(
    ctx: click.Context, username: str, server: str, port: int, key_path: str
) -> None:
    """Subcommand for the slurmdocs database operations.

    Args:
        ctx (click.Context): Click context.
        username (str): The username to use for the SSH session.
        server (str): The server to connect to.
        port (int): The port to use for the SSH connection.
        key_path (str): The path to the SSH key file.

    Returns:
        None

    """
    ctx.obj['logger'].debug('Starting collect subcommand.')

    # Create an SSH session | Lazy connect | # TO DO : Add password authentication
    session = SSHSessionAuth(
        server=server,
        remote_username=username,
        port=port,
        use_key_base_aut=True,
        path_to_priv_key=key_path,
        no_ping=False,
    )
    ctx.obj['logger'].debug('Lazy SSH session created.')

    # Add to contex the session
    ctx.obj['session'] = session
    # Close after subcommand execution
    ctx.call_on_close(session.close)
    return


@collect.command()
@click.pass_context
@click.option(
    '-save',
    '--save-dir',
    required=False,
    help='The directory to save the collection.',
    type=click.Path(exists=True, readable=True, resolve_path=True),
    default=Path.cwd(),
)
def node(ctx: click.Context, save_dir: str) -> None:
    """Collect the node info file from the cluster.

    Args:
        ctx (click.Context): Click context.
        save_dir (str): The directory to save the collection.

    Returns:
        None
    """
    # Create a Collecter
    collecter = Collecter(
        icollecter=IscontrolColllecter(timeout=10),
        save_dir=save_dir,
    )

    # Connect to the cluster
    ctx.obj['session'].connect()

    # Collect the data
    collecter(session=ctx.obj['session'], filename='node_info.txt')

    return


@collect.command()
@click.pass_context
@click.option(
    '-n',
    '--node-name',
    required=True,
    help='The node name to collect CPU info.',
    type=click.STRING,
)
@click.option(
    '-p',
    '--partition',
    required=False,
    help='The partition to collect CPU info.',
    type=click.STRING,
    default='debug',
)
@click.option(
    '-qos',
    '--quality-of-service',
    required=False,
    help='The quality of service to use to collect CPU info.',
    type=click.STRING,
    default='debug',
)
@click.option(
    '-save',
    '--save-dir',
    required=False,
    help='The directory to save the collection.',
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
    """Collect CPU information for a specific node.

    Args:
        ctx (click.Context): Click context.
        node_name (str): The node name to collect CPU info.
        partition (str): The partition to collect CPU info.
        quality_of_service (str): The quality of service to use to collect CPU info.
        save_dir (str): The directory to save the collection.

    Returns:
        None
    """
    # Create a Collecter
    collecter = Collecter(icollecter=IlscpuCollecter(timeout=10), save_dir=save_dir)

    # Connect to the cluster
    ctx.obj['session'].connect()

    # Collect the cpu info
    collecter(
        session=ctx.obj['session'],
        filename=f'{node_name}.txt',
        partition=partition,
        qos=quality_of_service,
        node=node_name,
    )

    return
