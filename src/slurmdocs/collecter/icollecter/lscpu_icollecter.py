"""Ilscpu Class.

Implement the Ilscpu class, which collects 'lscpu' information from a specific Slurm cluster node.

Classes:
    - 'Ilscpu': Collects 'lscpu' information.

Usage:
    To collect 'lscpu' information from a Slurm cluster node, create an instance of the 'Ilscpu' class and call it with the required arguments.

Example:
    ```python
    from my_module import Ilscpu
    from my_ssh_session_module import SSHSessionAuth

    # Instantiate the Ilscpu collector
    ilscpu_collector = Ilscpu()

    # Create an SSH session
    ssh_session = SSHSessionAuth(host='slurm-cluster.example.com', username='user', password='password')

    # Collect 'lscpu' information for a specific node
    node_info = ilscpu_collector(ssh_session, partition='my_partition', qos='my_qos', node='my_node')
    ```

Attributes:
    - None

Methods:
    - '__init__(self, timeout: float = 10) -> None': Initializes the Ilscpu instance.
    - '_collect(self, session: SSHSessionAuth, **kwargs) -> str': Collects 'lscpu' information from the Slurm cluster node.

Raises:
    - 'ValueError': If required arguments ('partition', 'qos', 'node') are missing or invalid.

Returns:
    - 'str': The collected 'lscpu' information as a string.

"""


from slurmdocs.session.ssh_session import SSHSessionAuth

from .icollecter import ICollecter

__all__ = ["IlscpuCollecter"]


class IlscpuCollecter(ICollecter):
    """Collect the lscpu information."""

    def __init__(self, timeout: float = 10) -> None:
        """Initialize the Ilscpu instance.

        Args:
            timeout (float, optional): Timeout time. Defaults to 10.
        """
        super().__init__(timeout, feature="lscpu")

    def _collect(self, session: SSHSessionAuth, **kwargs) -> str:
        """Collect 'lscpu' information from the Slurm cluster node.

        Args:
            session (SSHSessionAuth): The SSH session to the Slurm cluster.
            kwargs (dict): Keyword arguments to pass to the collect method.

        Raises:
            ValueError: If required arguments ('partition', 'qos', 'node') are missing or invalid.

        Returns:
            str: The collected 'lscpu' information as a string.
        """
        # Connect to the session
        session.connect()

        # Check for additional arguments
        if "node" not in kwargs:
            raise ValueError("node argument is required.")
        if "partition" not in kwargs:
            raise ValueError("partition argument is required.")
        if "qos" not in kwargs:
            raise ValueError("qos argument is required.")

        # Get the partition, qos, and node
        partition = kwargs["partition"]
        qos = kwargs["qos"]
        node = kwargs["node"]

        # Slurm srun command to run lscpu on the node
        cmd = f"srun -n 1 -c 1 -p {partition} --qos {qos} -J {node[-1:-5]} --nodelist={node} lscpu"

        # Run the command
        try:
            stdin, stdout, stderr = session.session.exec_command(
                cmd, timeout=self._timeout
            )
        except TimeoutError:
            session.session.exec_command(
                f"scancel -n {node[-1:-5]} -u {session.remote_username}"
            )
            raise TimeoutError(
                f"""Timeout when running the command: {cmd}.
                               Check if the node {node} is available under partition : {partition} and QOS: {qos}.
                               Check if the node is not busy."""
            )

        # Read the output
        stdout = stdout.read().decode("utf-8")

        # Check if there is any output
        if len(stdout) == 0:
            raise ValueError(
                f"No output from lscpu command. Check if the node {node} is available under partition : {partition} and QOS: {qos}."
            )

        return stdout
