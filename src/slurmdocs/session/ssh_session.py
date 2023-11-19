"""SSH Session Authentication Module.

This module provides a class for establishing SSH sessions with remote servers using key-based or password-based
authentication. The `SessionAuth` class allows creating SSH connections while handling key management and
server reachability checks.

Classes:
    SessionAuth: A class for establishing SSH sessions with various authentication methods.

Dependencies:
    - os
    - paramiko
    - getpass
    - warnings
"""


import os
import warnings
from getpass import getpass

import paramiko  # type: ignore

__all__ = ["SSHSessionAuth"]


class SSHSessionAuth:
    """A class for establishing SSH sessions with remote servers using various authentication methods.

    This class provides functionality to create SSH sessions to remote servers either using key-based
    authentication or password-based authentication. It also supports checking server reachability
    before attempting to establish a connection.

    Args:
        server (str): The hostname or IP address of the remote server.
        remote_username (str): The username for the remote server authentication.
        port (int, optional): The port number for the SSH connection. Default is 22.
        use_key_base_aut (bool, optional): If True, uses key-based authentication. Default is True.
        path_to_priv_key (str | None, optional): Path to the private key file for key-based authentication.
            If None, a default path will be used. Default is None.

    Raises:
        ConnectionError: If the server is not reachable.
        FileNotFoundError: If the provided path_to_priv_key does not exist.

    Attributes:
        server (str): The hostname or IP address of the remote server.
        remote_username (str): The username for the remote server authentication.
        use_key_base_aut (bool): Whether key-based authentication is used.
        path_to_key (str): Path to the private key file for key-based authentication.
        port (int): The port number for the SSH connection.
        session (paramiko.SSHClient): The SSH session object.

    Methods:
        _create_session(): Creates an SSH session with the remote server.

    """

    def __init__(
        self,
        server: str,
        remote_username: str,
        port: int = 22,
        use_key_base_aut: bool = True,
        path_to_priv_key: str | None = None,
        no_ping: bool = False,
    ) -> None:
        """Initialize an SSH session authentication object.

        Args:
        server (str): The hostname or IP address of the remote server.
        remote_username (str): The username for remote server authentication.
        port (int, optional): The port number for the SSH connection. Default is 22.
        use_key_base_aut (bool, optional): If True, uses key-based authentication.
            If False, password-based authentication will be used. Default is True.
        path_to_priv_key (str | None, optional): Path to the private key file for key-based authentication.
            If None, the default path will be used. Default is None.
        no_ping (bool, optional): If True, the server reachability check will be skipped. Default is False.

        Raises:
        ConnectionError: If the server is not reachable.
        FileNotFoundError: If path_to_priv_key is provided and the file does not exist.
        AssertionError: If the port number is invalid.

        Warnings:
        UserWarning: If password-based authentication is used, it is not recommended.

        Attributes:
        server (str): The hostname or IP address of the remote server.
        remote_username (str): The username for remote server authentication.
        use_key_base_aut (bool): Whether key-based authentication is used.
        path_to_key (str): Path to the private key file for key-based authentication.
        port (int): The port number for the SSH connection.
        session (paramiko.SSHClient): The SSH session object.

        Example:
        session = SessionAuth("example.com", "username", port=2222)
        # Use the session object for further interactions with the remote server
        """
        # Set the server name
        self.server = server

        # Ping the server to check if it is reachable
        if not no_ping:
            response = os.system("ping -c 1 " + self.server)
            if response != 0:
                raise ConnectionError("Server not reachable")

        # Get the Remote Username
        self.remote_username = remote_username
        # Which authentication to use
        self.use_key_base_aut = use_key_base_aut

        # Get the password if not using key based authentication
        if not use_key_base_aut:
            warnings.warn(" Need Password Authentication! Not Preffered", stacklevel=1)
            self.password = getpass()

        # Key Based Authentication
        if use_key_base_aut:
            if path_to_priv_key is None:
                warnings.warn(
                    "Using Key Based Authentication, but no path to key is given. Using default path",
                    stacklevel=1,
                )
                if os.path.exists(f"/home/{os.getlogin()}/.ssh/id_rsa"):
                    self.path_to_key = f"/home/{os.getlogin()}/.ssh/id_rsa"
                else:
                    raise FileNotFoundError(
                        "No key found in default path. Please provide the path to key"
                    )
            else:
                self.path_to_key = path_to_priv_key

        # port number for ssh connection
        assert port > 0 and port < 65535, "Invalid port number"
        self.port = port

    def _create_session(self) -> paramiko.SSHClient:
        """Create a session with the server."""
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if self.use_key_base_aut:
                private_key = paramiko.RSAKey.from_private_key_file(self.path_to_key)

                ssh_client.connect(
                    hostname=self.server,
                    port=self.port,
                    username=self.remote_username,
                    pkey=private_key,
                )
            else:
                ssh_client.connect(
                    hostname=self.server,
                    port=self.port,
                    username=self.remote_username,
                    password=self.password,
                )
        except paramiko.AuthenticationException:
            print("Authentication failed, please verify your credentials")
        except paramiko.SSHException as sshException:
            print("Unable to establish SSH connection: %s " % sshException)

        except Exception as e:
            print("Error: %s" % e)

        return ssh_client

    def is_connected(self) -> bool:
        """Check if the session is connected."""
        # If the session is not created, return False
        if not hasattr(self, "session"):
            return False

        return self.session.get_transport().is_active()

    def connect(self) -> None:
        """Connect to the remote server."""
        # connection Guard
        if not self.is_connected():
            self.session = self._create_session()

        return

    def close(self) -> None:
        """Close the session."""
        if self.is_connected():
            self.session.close()
        return

    def is_alive(self) -> bool:
        """Check if the session is alive."""
        if self.is_connected():
            return self.session.get_transport().is_alive()

        return False
