"""Stats Interface for Pandas Series.

This module defines the `Istat` class, an abstract interface for computing statistics on Pandas Series objects. Subclasses can implement the `_compute` method to specify custom statistics computation logic.

Classes:
    - Istat: An abstract base class for statistics computation on Pandas Series.

Usage:
    To create custom statistics computation classes based on this interface, subclass `Istat` and implement the `_compute` method. Example:

    ```python
    class MyCustomStats(Istat):
        def _compute(self, series: pd.Series) -> pd.Series:
            # Implement custom statistics computation here
            pass
    ```

Note:
    This module provides a framework for statistics computation, allowing users to define their own statistical calculations tailored to their specific needs.
"""
from abc import ABC, abstractmethod

import pandas as pd

__all__ = ["Istat"]


class Istat(ABC):
    """Stats interface for slurmdocs.

    This class defines an abstract interface for computing statistics on Pandas Series objects. It serves as a base for implementing specific statistics computation strategies. Users can subclass this interface and provide their custom `_compute` method to compute statistics tailored to their needs.

    Attributes:
        _features (str): A string representing the type of features used for statistics computation. Defaults to "NoneType" if not specified during initialization.

    Methods:
        __init__(self, features: str = "NoneType") -> None:
            Initialize an instance of Istat.

        __repr__(self) -> str:
            Return a string representation of the Istat instance, including its features type.

        _compute(self, series: pd.Series) -> pd.Series:
            Abstract method to compute statistics from a Pandas Series. Subclasses must implement this method.

        __call__(self, series: pd.Series) -> pd.Series:
            Compute statistics from a Pandas Series using this instance.

    Args:
        features (str, optional): A string describing the type of features used for statistics computation. Defaults to "NoneType."

    Example:
        To create a custom statistics computation class based on this interface:

        ```python
        class MyCustomStats(Istat):
            def _compute(self, series: pd.Series) -> pd.Series:
                # Implement custom statistics computation here
                pass
        ```

    Note:
        This class is designed to provide a framework for computing statistics on Pandas Series objects. Subclasses should implement the `_compute` method to specify the desired statistics computation logic.
    """

    def __init__(self, features: str = "NoneType") -> None:
        """Initialize an instance of Istat.

        Args:
            features (str, optional): A string describing the type of features used for statistics computation. Defaults to "NoneType."
        """
        self._features = features if features else "NoneType"
        super().__init__()

    def __repr__(self) -> str:
        """Return a string representation of the Istat instance, including its features type.

        Returns:
            str: A string representation of the object.
        """
        return f"Istat({self._features})" if self._features else "Istat()"

    @abstractmethod
    def _compute(self, series: pd.Series) -> pd.Series:
        """Compute statistics from a Pandas Series.

        Args:
            series (pd.Series): A Pandas Series containing the data for which statistics need to be computed.

        Returns:
            pd.Series: A Pandas Series containing the computed statistics.
        """
        pass

    def __call__(self, series: pd.Series) -> pd.Series:
        """Compute statistics from a Pandas Series using this instance.

        Args:
            series (pd.Series): A Pandas Series containing the data for which statistics need to be computed.

        Returns:
            pd.Series: A Pandas Series containing the computed statistics.
        """
        return self._compute(series)
