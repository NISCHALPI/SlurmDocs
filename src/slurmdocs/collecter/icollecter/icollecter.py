"""ICollecter Module.

This module defines the 'ICollecter' abstract base class for collecting data from the Slurm cluster using SSH sessions.

Classes:
    - 'ICollecter': An abstract base class for collecting data from the Slurm cluster.

Usage:
    To implement custom data collection from the Slurm cluster, you can create a class that inherits from 'ICollecter' and implement the '_collect' method.

"""
from abc import ABC, abstractmethod

from ...session.ssh_session import SSHSessionAuth

__all__ = ["ICollecter"]


class ICollecter(ABC):
    """An abstract base class for collecting data from the Slurm cluster.

    This abstract class defines the interface for data collection from the Slurm cluster.

    Args:
        ABC (type): A metaclass for defining abstract base classes.

    Attributes:
        _feature (str): The name or identifier of the data collection feature.

    Methods:
        __init__(self, feature: str = None) -> None: Initializes the ICollecter instance.
        _collect(self, session: SSHSessionAuth, key: str) -> str: Collects data from the Slurm cluster using the provided SSH session.
        feature (property): Get the name or identifier of the data collection feature.
        feature (setter): Set the name or identifier of the data collection feature.
        __repr__(self) -> str: Return a string representation of the ICollecter instance.
        __call__(self, session: SSHSessionAuth, key: str) -> Any: Calls the collector to collect data from the Slurm cluster.

    """

    def __init__(self, timeout: float = 10.0, feature: str = None) -> None:
        """Initialize the ICollecter instance."""
        self._feature = feature if feature is not None else "NoneType"
        self._timeout = timeout
        pass

    @abstractmethod
    def _collect(self, session: SSHSessionAuth, **kwargs) -> str:
        """Collect data from the Slurm cluster using the provided SSH session.

        Args:
            session (SSHSessionAuth): The SSH session to the Slurm cluster.
            kwargs (dict): Keyword arguments to pass to the collect method.

        Returns:
            str: The collected data as a string.
        """
        pass

    @property
    def feature(self) -> str:
        """Get the name or identifier of the data collection feature.

        Returns:
            str: The feature name or identifier.
        """
        return self._feature

    @feature.setter
    def feature(self, feature: str) -> None:
        """Set the name or identifier of the data collection feature.

        Args:
            feature (str): The feature name or identifier.
        """
        self._feature = feature
        return

    def __repr__(self) -> str:
        """Return a string representation of the ICollecter instance.

        Returns:
            str: String representation of the object.
        """
        return f"{self.__class__.__name__}({self.feature})"

    def __call__(self, session: SSHSessionAuth, **kwargs) -> str:
        """Call method for collecting data from the Slurm cluster.

        Args:
            session (SSHSessionAuth): The SSH session to the Slurm cluster.
            kwargs (dict): Keyword arguments to pass to the collect method.

        Returns:
            Any: The collected data.
        """
        return self._collect(session, **kwargs)
