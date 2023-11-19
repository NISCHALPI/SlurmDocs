"""Implements a stats interface for slurmdocs.

This module defines an abstract base class `AbstractStats` that provides a framework for computing statistics on Pandas Series objects. It also includes a concrete implementation of this class called `Stats`.

Classes:
    - AbstractStats: An abstract base class that defines the interface for computing statistics on Pandas Series objects.
    - Stats: A concrete implementation of `AbstractStats` specifically designed for slurmdocs.

Usage:
    To use this module, first create an instance of the `Stats` class, passing an `Istat` object to its constructor. You can then call this instance as a function with a Pandas Series to compute statistics.

Example:
    ```python
    istats = Istat()  # Create an Istat object with the desired configuration
    stats = Stats(istats)  # Create a Stats object with the Istat object

    data_series = pd.Series([1, 2, 3, 4, 5])
    result_series = stats(data_series)  # Compute statistics on the data_series
    ```

Attributes:
    - `AbstractStats`: An abstract base class for computing statistics on Pandas Series objects. It enforces the implementation of the `_compute` method.
    - `Stats`: A concrete implementation of `AbstractStats` specifically designed for slurmdocs. It overrides the `_compute` method to provide custom statistics computation.

Methods:
    - `AbstractStats.__init__(self, istats: Istat) -> None`: Initializes an instance of `AbstractStats` with the provided `Istat` object.
    - `AbstractStats._compute(self, series: pd.Series) -> pd.Series`: Abstract method to compute statistics from a Pandas Series. Subclasses must implement this method.
    - `AbstractStats.__call__(self, series: pd.Series) -> pd.Series`: Allows calling an instance of `AbstractStats` as a function to compute statistics on a Pandas Series.
    - `AbstractStats.__repr__(self) -> str`: Returns a string representation of the `AbstractStats` instance.

    - `Stats._compute(self, series: pd.Series) -> pd.Series`: Overrides the `_compute` method in `AbstractStats` to provide custom statistics computation for slurmdocs data.

Raises:
    - `TypeError`: Raised in the constructor if the `istats` argument is not an instance of the `Istat` class.

Note:
    This module is intended for computing statistics on slurmdocs data using the provided `Istat` configuration. Subclasses can be created to implement custom statistics computation based on specific requirements.

"""

from abc import ABC, abstractmethod

import pandas as pd

from .istat import Istat

__all__ = ["AbstractStats", "Statistics"]


class AbstractStats(ABC):
    """Abstract class for stats interface."""

    def __init__(self, istats: Istat) -> None:
        """Initialize an instance of AbstractStats.

        Args:
            istats (Istat): An instance of the Istat class used for configuring statistics computation.

        Raises:
            TypeError: If istats is not an instance of the Istat class.
        """
        self.istats = istats

    @abstractmethod
    def _compute(self, series: pd.Series) -> pd.Series:
        """Compute statistics from a Pandas Series.

        Args:
            series (pd.Series): A Pandas Series containing the data for which statistics need to be computed.

        Returns:
            pd.Series: A Pandas Series containing the computed statistics.
        """
        return self._istats(series)

    def __call__(self, series: pd.Series) -> pd.Series:
        """Compute statistics from a Pandas Series using this instance.

        Args:
            series (pd.Series): A Pandas Series containing the data for which statistics need to be computed.

        Returns:
            pd.Series: A Pandas Series containing the computed statistics.
        """
        return self._compute(series)

    def __repr__(self) -> str:
        """Return a string representation of the AbstractStats instance.

        Returns:
            str: A string representation of the AbstractStats instance, including the associated Istat configuration.
        """
        return f"{self.__class__.__name__}({self._istats})"

    @property
    def istats(self) -> Istat:
        """Return the Istat configuration associated with this instance.

        Returns:
            Istat: The Istat configuration associated with this instance.
        """
        return self._istats

    @istats.setter
    def istats(self, istats: Istat) -> None:
        """Set the Istat configuration associated with this instance.

        Args:
            istats (Istat): The Istat configuration to associate with this instance.
        """
        if not isinstance(istats, Istat):
            raise TypeError(f"istats must be an instance of Istat, not {type(istats)}")

        self._istats = istats

    def swap(self, istats: Istat) -> None:
        """Swap the Istat interface associated with this instance.

        Args:
            istats (Istat): The Istat configuration to associate with this instance.
        """
        self.istats = istats


class Statistics(AbstractStats):
    """Stats class for slurmdocs."""

    def _compute(self, series: pd.Series) -> pd.Series:
        """Compute custom statistics for slurmdocs data.

        This method overrides the abstract _compute method in AbstractStats to provide custom statistics computation for slurmdocs data.

        Args:
            series (pd.Series): A Pandas Series containing slurmdocs data.

        Returns:
            pd.Series: A Pandas Series containing the computed statistics for slurmdocs data.
        """
        # Custom statistics computation for slurmdocs data goes here
        return super()._compute(series)
