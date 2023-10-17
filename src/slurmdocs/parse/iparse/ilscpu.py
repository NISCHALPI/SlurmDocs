"""Parses LSCPU output from a specified file.

This class implements the IParse interface to parse data from the 'lscpu' command output file.

Attributes:
    None

Methods:
    - _parse_lscpu(filename: Path) -> pd.Series: Parse LSCPU output from the specified file.

Usage:
    1. Instantiate an 'Ilscpu' object.
    2. Use the '_parse' method to parse LSCPU output from a file and obtain the parsed data as a pandas Series.

Example:
    ```python
    from my_parsing_module import Ilscpu

    lscpu_parser = Ilscpu()  # Instantiate the LSCPU parser
    parsed_data = lscpu_parser._parse(Path('lscpu_output.txt'))  # Parse LSCPU data from a file
    ```

Returns:
    pd.Series: Parsed data stored as a pandas Series.
"""

from pathlib import Path

import pandas as pd

from .base_iparse import IParse

__all__ = ["IlscpuParser"]


class IlscpuParser(IParse):
    """Parses LSCPU output.

    This class implements the IParse interface for parsing data from 'lscpu' command output files.

    Attributes:
        None

    Methods:
        - __init__(self) -> None: Initializes the Ilscpu object.
        - _parse_lscpu(self, filename: Path) -> pd.Series: Parse LSCPU output from the specified file.
        - _parse(self, filename: Path) -> pd.Series: Parse LSCPU output from the specified file.
    """

    def __init__(self) -> None:
        """Initialize the Ilscpu object."""
        super().__init__("lscpu")

    def _parse_lscpu(self, string: str) -> pd.Series:
        """Parse LSCPU output from the specified file.

        Args:
            string (Path): lscp output as a string.

        Returns:
            pd.Series: Parsed data stored as a pandas Series.
        """
        data = {}

        for line in string:
            # Skip empty lines
            if line == "\n":
                continue

            # Strip whitespace
            line = line.strip()

            key, value = line.split(":", maxsplit=1)
            key = key.strip()
            value = value.strip()

            # Convert to int if possible
            try:
                value = int(value)
            except ValueError:
                pass

            data[key] = value

        return pd.Series(data)

    def _parse(self, filename: Path) -> pd.Series:
        """Parse LSCPU output from the specified file.

        Args:
            filename (Path): The path to the file containing LSCPU output.

        Returns:
            pd.Series: Parsed data stored as a pandas Series.
        """
        with open(filename) as f:
            string = f.readlines()

        return self._parse_lscpu(string=string)
