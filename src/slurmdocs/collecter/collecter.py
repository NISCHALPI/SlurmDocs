"""The collector module that collects data from the Slurm cluster.

This module defines the 'AbstractCollecter' class, which is responsible for collecting data from the Slurm cluster. It provides a framework for implementing data collection methods by extending the 'ICollecter' interface.

Classes:
    - 'AbstractCollecter': An abstract base class for collecting data from the Slurm cluster.

Usage:
    1. Create a custom collector class by subclassing 'AbstractCollecter' and implementing the '_collect' method.
    2. Instantiate the custom collector with an 'ICollecter' object and an optional save directory.
    3. Use the collector to collect data from the Slurm cluster.

Example:
    ```python
    from my_collector_module import MyCustomCollector
    from my_icollecter_module import MyICollecter
    from my_ssh_session_module import SSHSessionAuth

    icollecter = MyICollecter()  # Instantiate your ICollecter implementation
    custom_collector = MyCustomCollector(icollecter, save_dir='/data')  # Instantiate your custom collector

    ssh_session = SSHSessionAuth(host='slurm-cluster.example.com', username='user', password='password')

    collected_data = custom_collector(ssh_session)  # Collect data from the Slurm cluster
    ```

Attributes:
    None

Methods:
    - __init__(self, icollecter: ICollecter, save_dir: str | Path | None = None) -> None: Initializes the AbstractCollecter instance.
    - _collect(self, session: SSHSessionAuth) -> str: Collects data from the Slurm cluster.
    - __repr__(self) -> str: Returns a string representation of the AbstractCollecter instance.
    - __call__(self, session: SSHSessionAuth) -> str: Calls the collector to collect data from the Slurm cluster.

"""

import os
from abc import ABC, abstractmethod
from pathlib import Path

from ..session.ssh_session import SSHSessionAuth
from .icollecter import ICollecter

__all__ = ["AbstractCollecter", "Collecter"]


class AbstractCollecter(ABC):
    """Abstract base class for collecting data from the Slurm cluster."""

    def __init__(
        self, icollecter: ICollecter, save_dir: str | Path | None = None
    ) -> None:
        """Initialize the AbstractCollecter instance.

        Args:
            icollecter (ICollecter): An instance of a class implementing the ICollecter interface.
            save_dir (str | Path | None, optional): The directory to save collected data. Defaults to cwd.
        """
        # Check if icollecter is an instance of ICollecter
        if not isinstance(icollecter, ICollecter):
            raise TypeError(
                f"icollecter must be an instance of ICollecter. Got {type(icollecter)} instead."
            )

        self._icollecter = icollecter

        # Check if save_dir is a string or a Path
        # If it is a string, convert it to a Path
        # If it is not a string or a Path, raise an error
        # If it is a string or a Path, check if the directory exists.

        if save_dir is not None:
            if isinstance(save_dir, str):
                save_dir = Path(save_dir)

            elif not isinstance(save_dir, Path):
                raise TypeError(
                    f"save_dir must be a string or a Path. Got {type(save_dir)} instead."
                )
            if not save_dir.exists():
                raise FileNotFoundError(f"save_dir {save_dir} does not exist.")

            self._save_dir = save_dir

        super().__init__()

    @abstractmethod
    def _collect(
        self,
        session: SSHSessionAuth,
        filename: str | None = None,
        **kwargs,
    ) -> str:
        """Collects data from the Slurm cluster.

        Args:
            session (SSHSessionAuth): The SSH session to the Slurm cluster.
            filename (str): The name of the file to save the collected data.
            kwargs (dict): Keyword arguments to pass to the icollecter.

        Returns:
            str: The collected data.
        """
        # Get the data from the slurm cluster
        data = self._icollecter(session, **kwargs)

        # Save the data to a text file with current timestamp
        if hasattr(self, "_save_dir"):
            if filename is None:
                raise ValueError(
                    "filename must be specified when save_dir is specified."
                )
            with open(
                os.path.join(
                    self._save_dir,
                    filename + ".txt" if not filename.endswith(".txt") else filename,
                ),
                "w",
            ) as f:
                f.write(data)
            # Close the file
            f.close()

        # Return the data
        return data

    def __repr__(self) -> str:
        """Return a string representation of the AbstractCollecter instance.

        Returns:
            str: String representation of the object.
        """
        if hasattr(self, "_save_dir"):
            return f"{self.__class__.__name__}(icollecter={self._icollecter}, save_dir={self._save_dir})"

        return f"{self.__class__.__name__}(icollecter={self._icollecter})"

    def __call__(
        self, session: SSHSessionAuth, filename: str | None = None, **kwargs
    ) -> str:
        """Call method for collecting data from the Slurm cluster.

        Args:
            session (SSHSessionAuth): The SSH session to the Slurm cluster.
            filename (str): The name of the file to save the collected data.
            kwargs (dict): Keyword arguments to pass to the icollecter.

        Returns:
            str: The collected data.
        """
        return self._collect(session, filename=filename, **kwargs)

    def swap(self, icollecter: ICollecter) -> None:
        """Swaps the icollecter of the AbstractCollecter instance.

        Args:
            icollecter (ICollecter): An instance of a class implementing the ICollecter interface.
        """
        # Check if icollecter is an instance of ICollecter
        if not isinstance(icollecter, ICollecter):
            raise TypeError(
                f"icollecter must be an instance of ICollecter. Got {type(icollecter)} instead."
            )
        self._icollecter = icollecter
        return


class Collecter(AbstractCollecter):
    """Collecter class for collecting data from the Slurm cluster."""

    def __init__(
        self, icollecter: ICollecter, save_dir: str | Path | None = None
    ) -> None:
        """Initialize the Collecter instance.

        Args:
            icollecter (ICollecter): An instance of a class implementing the ICollecter interface.
            save_dir (str | Path | None, optional): The directory to save collected data. Defaults to None.
        """
        super().__init__(icollecter, save_dir=save_dir)

    def _collect(
        self, session: SSHSessionAuth, filename: str | None = None, **kwargs
    ) -> str:
        """Collects data from the Slurm cluster.

        Args:
            session (SSHSessionAuth): The SSH session to the Slurm cluster.
            filename (str): The name of the file to save the collected data.
            kwargs (dict): Keyword arguments to pass to the icollecter.

        Returns:
            str: The collected data.
        """
        return super()._collect(session, filename=filename, **kwargs)
