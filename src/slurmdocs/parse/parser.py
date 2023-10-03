"""Defines an abstract parser and a concrete parser implementation for parsing data from files.

This module provides two classes: `AbstractParser` and `Parser`, which are designed for parsing data from files using a specified parsing interface (`IParse`).

Classes:
    - `AbstractParser`: An abstract base class for parsing data from files.
    - `Parser`: A concrete implementation of the `AbstractParser` class.

Usage:
    1. Create a custom parsing class that implements the `IParse` interface.
    2. Instantiate a `Parser` object with the custom parsing class as an argument.
    3. Use the `Parser` object to parse data from files.

Example:
    ```python
    from my_parsing_module import MyCustomParser
    from my_parser import Parser

    custom_parser = MyCustomParser()  # Instantiate your custom parser
    parser = Parser(custom_parser)    # Instantiate the Parser with your custom parser

    # Parse data from a file
    parsed_data = parser("data.txt")
    ```

Attributes:
    - `AbstractParser`: The abstract base class for all parsers. It provides common functionality for parsing data from files.
    - `Parser`: A concrete implementation of the `AbstractParser` class that can be used with a specific parsing interface.

Note:
    Ensure that your custom parsing class implements the `IParse` interface to work seamlessly with the `Parser` class.
"""
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from .iparse import IParse  # TODO: add IParse

__all__ = ["AbstractParser", "Parser"]


class AbstractParser(ABC):
    """Abstract base class for parsing data from files using a specified parsing interface (IParse)."""

    def __init__(
        self,
        iparser: IParse,
    ) -> None:
        """Initialize an AbstractParser instance.

        Args:
            iparser (IParse): An instance of a class that implements the IParse interface.

        Raises:
            TypeError: If iparser is not an instance of IParse.
        """
        # Set the IParse interface
        self.iparser = iparser
        return

    def _check_file_integrity(self, filepath: str | Path) -> None:
        """Check the integrity of a file path.

        Args:
            filepath (str | Path): The path to the file to check.

        Raises:
            TypeError: If filepath is not a str or Path.
            FileNotFoundError: If the file does not exist.
            FileNotFoundError: If the path is not a file.
            PermissionError: If the file is not readable.

        """
        # Verify filepath
        if not isinstance(filepath, str | Path):
            raise TypeError(f"filepath must be str or Path, not {type(filepath)}")

        if isinstance(filepath, str):
            filepath = Path(filepath)
        else:
            filepath = filepath

        # If not exists, raise error
        if not filepath.exists():
            raise FileNotFoundError(f"{filepath} does not exist")

        # If not a file, raise error
        if not filepath.is_file():
            raise FileNotFoundError(f"{filepath} is not a file")

        return

    # TO DO : def _dispatch(self) -> None:

    @abstractmethod
    def _parse(self, filepath: str | Path) -> pd.Series:
        """Parse data from a file using the provided IParse interface.

        Args:
            filepath (str | Path): Path to the file to parse.

        Returns:
            tp.Tuple[pd.Series, pd.DataFrame]: Tuple of parsed data (metadata, data).
        """
        # Verify filepath
        self._check_file_integrity(filepath)

        # Parse data
        return self.iparser(filepath)

    @property
    def iparser(self) -> IParse:
        """Get the IParse interface used by the AbstractParser.

        Returns:
            IParse: The IParse interface used by the AbstractParser.
        """
        return self._iparser

    @iparser.setter
    def iparser(self, iparser: IParse) -> None:
        """Set the IParse interface used by the AbstractParser.

        Args:
            iparser (IParse): The IParse interface used by the AbstractParser.
        """
        if not isinstance(iparser, IParse):
            raise TypeError(f"iparser must be IParse, not {type(iparser)}")

        self._iparser = iparser

        return

    def swap(self, iparser: IParse) -> None:
        """Swap the IParse interface used by the AbstractParser.

        Args:
            iparser (IParse): The IParse interface used by the AbstractParser.
        """
        self.iparser = iparser

        return

    def __call__(self, filepath: str | Path) -> pd.Series:
        """Call method for parsing data from a file.

        Args:
            filepath (str | Path): Path to the file to parse.

        Returns:
            Any: The parsed data.

        """
        return self._parse(filepath)

    def __repr__(self) -> str:
        """Return a string representation of the AbstractParser instance.

        Returns:
            str: String representation of the object.

        """
        return f"{self.__class__.__name__}(iparser={self.iparser})"


class Parser(AbstractParser):
    """Concrete implementation of the AbstractParser class."""

    def __init__(self, iparser: IParse) -> None:
        """Initialize a Parser instance.

        Args:
            iparser (IParse): An instance of a class that implements the IParse interface.
        """
        super().__init__(iparser)
        return

    def _parse(self, filepath: str | Path) -> pd.Series:
        """Parse data from a file using the provided IParse interface.

        Args:
            filepath (str | Path): Path to the file to parse.

        Returns:
            pd.Series: Parsed data.
        """
        return super()._parse(filepath)
