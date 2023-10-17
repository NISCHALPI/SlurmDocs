"""Iscontrol Class.

Implement the Iscontrol class, which collects information using the 'scontrol show node' command from a Slurm cluster.

Classes:
    - 'Iscontrol': Collects information using the 'scontrol show node' command.

Attributes:
    None

Methods:
    __init__(self, timeout: float = 10) -> None: Initializes the Iscontrol instance.
    _collect(self, session: SSHSessionAuth, **kwargs) -> str: Collects information using the 'scontrol show node' command.

Usage:
    To collect information from a Slurm cluster using the 'scontrol show node' command, create an instance of the 'Iscontrol' class and call it with the required arguments.

Example:
    ```python
    from my_module import Iscontrol
    from my_ssh_session_module import SSHSessionAuth

    # Instantiate the Iscontrol collector
    iscontrol_collector = Iscontrol()

    # Create an SSH session
    ssh_session = SSHSessionAuth(host='slurm-cluster.example.com', username='user', password='password')

    # Collect information using the 'scontrol show node' command
    node_info = iscontrol_collector(ssh_session)
    ```

Raises:
    - RuntimeError: If there is an error in the 'scontrol show node' command or if the server does not have Slurm installed.

Returns:
    - 'str': The collected information as a string.

Author:
    Your Name

Version:
    1.0.0

"""
from slurmdocs.session.ssh_session import SSHSessionAuth

from .icollecter import ICollecter

__all__ = ["IscontrolColllecter"]


class IscontrolColllecter(ICollecter):
    """Iscontrol Class.

    Collects information from a Slurm cluster using the 'scontrol show node' command.

    Attributes:
        None

    Methods:
        __init__(self, timeout: float = 10) -> None: Initializes the Iscontrol instance.
        _collect(self, session: SSHSessionAuth, **kwargs) -> str: Collects information using the 'scontrol show node' command.

    Usage:
        To collect information from a Slurm cluster using the 'scontrol show node' command, create an instance of the 'Iscontrol' class and call it with the required arguments.
    """

    def __init__(self, timeout: float = 10) -> None:
        """Initialize the Iscontrol instance.

        Args:
            timeout (float, optional): Timeout time for the SSH session. Defaults to 10.
        """
        super().__init__(timeout, feature="lscpu")

    def _collect(self, session: SSHSessionAuth, **kwargs) -> str:  # noqa : ARG002
        """Collect information using the 'scontrol show node' command.

        Args:
            session (SSHSessionAuth): The SSH session to the Slurm cluster.
            **kwargs: Additional keyword arguments (not used in this implementation).

        Raises:
            RuntimeError: If there is an error in the 'scontrol show node' command or if the server does not have Slurm installed.

        Returns:
            str: The collected information as a string.
        """
        # Run the scontrol show node command
        try:
            stdin, stdout, stderr = session.session.exec_command(
                "scontrol show node", timeout=self._timeout
            )
        except TimeoutError:
            raise TimeoutError("Timeout occured! See if the server is available")

        # Read the output and error
        output = stdout.read().decode("utf-8")
        error = stderr.read().decode("utf-8")

        # Check if there was an error
        if "error" in error.lower():
            raise RuntimeError(
                "Error in scontrol show node command. Please check server has Slurm installed."
            )

        return output
