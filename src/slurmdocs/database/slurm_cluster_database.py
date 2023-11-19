"""Slurm Cluster Database.

This module provides a class for managing a Slurm Cluster Database. The database
stores information related to Slurm cluster nodes and their CPU details. It allows
you to create, update, query, and delete data within the database.

Classes:
    - SlurmClusterDatabase: A class for managing the Slurm Cluster Database.

"""

import os
import shutil
import warnings
from pathlib import Path

import pandas as pd

from ..parse import IlscpuParser, IscontrolParser, Parser
from .base_database import BaseDatabase

__all__ = ["SlurmClusterDatabase"]


class SlurmClusterDatabase(BaseDatabase):
    """Class for Slurm Cluster Database.

    This class provides methods to manage a Slurm Cluster Database. You can create,
    update, query, and delete data within the database. The database stores information
    related to Slurm cluster nodes and their CPU details.

    Attributes:
        _defaut_path (Path): The default path for the database.

    Methods:
        __init__(self, db_name: str, db_path: str | Path | None = None) -> None:
            Initializes the SlurmClusterDatabase instance.

        is_empty(self) -> bool:
            Checks if the database is empty.

        create(self) -> None:
            Creates subdirectories for the database.

        delete(self) -> None:
            Deletes the database and its subdirectories.

        remove(self, data: dict) -> None:
            Removes a specific data entry from the database.

        check_integrity(self) -> bool:
            Checks the integrity of the database.

        print(self) -> str:
            Prints the directory tree structure of the database.

        insert(self, data: dict) -> None:
            Inserts data into the database.

        update(self, data: dict) -> None:
            Updates data in the database.

        query(self, query: dict) -> pd.Series | pd.DataFrame:
            Queries data from the database based on a specified query.

        is_cpu_file_available(self, filename: str | Path) -> bool:
            Checks if a CPU data file is available in the database.

        is_node_file_available(self) -> bool:
            Checks if the node data file is available in the database.

        __getitem__(self, key: dict) -> pd.Series | pd.DataFrame:
            Implements the [] operator for querying data from the database.

        coverage(self) -> float:
            Calculates the coverage of the database based on available node and CPU data.
    """

    # Default path
    _defaut_path = Path.home() / ".slurmdocs"

    _cpu_db_name = "cpu"
    _node_db_name = "node"

    def __init__(self, db_name: str, db_path: str | Path | None = None) -> None:
        """Initialize the SlurmClusterDatabase instance.

        Args:
            db_name (str): The name of the database.
            db_path (str | Path | None, optional): The path to the database directory.
                If None, the default path will be used. Defaults to None.
        """
        # Default db path
        if db_path is None:
            self.db_path = self._defaut_path
        elif isinstance(db_path, str):
            self.db_path = Path(db_path)
        else:
            self.db_path = db_path

        # Attach to DB path
        self.db_path = self.db_path.joinpath(db_name)

        # If path does not exist, create it
        if not self.db_path.exists():
            self.db_path.mkdir(parents=True)

        # Init Parsers
        self.iparsers = {"cpu": IlscpuParser(), "node": IscontrolParser()}
        self.parser = Parser(
            iparser=self.iparsers["cpu"],
        )

        super().__init__(db_path=self.db_path)

    def is_empty(self) -> bool:
        """Check if the database is empty.

        Returns:
            bool: True if the database is empty, False otherwise.
        """
        # Check if cpu and node subdirectories exist or not
        if (
            not (self.db_path / self._cpu_db_name).exists()
            or not (self.db_path / self._node_db_name).exists()
        ):
            return True

        # Check if any files exist in cpu and node subdirectories. If not, database is empty
        if (
            len(os.listdir(self.db_path / self._cpu_db_name)) == 0
            and len(os.listdir(self.db_path / self._node_db_name)) == 0
        ):
            return True

        return False

    @staticmethod
    def cleanpath(path: Path = Path.home() / '.slurmdocs') -> None:
        """Remove empty directories from the default database path."""
        for dirs in path.iterdir():
            if dirs.is_dir():
                if len(os.listdir(dirs)) == 0:
                    os.rmdir(dirs)
                    print(f"Removed empty directory {dirs}")
        return

    def create(self) -> None:
        """Create subdirectories for the database."""
        # Create subdirectories
        if not self.db_path.exists():
            self.db_path.mkdir(parents=True)

        # make cpu and node subdirectories
        if not (self.db_path / self._cpu_db_name).exists():
            (self.db_path / self._cpu_db_name).mkdir(parents=True)
        if not (self.db_path / self._node_db_name).exists():
            (self.db_path / self._node_db_name).mkdir(parents=True)

    def _delete(self, path: str | Path) -> None:
        """Delete a directory and its contents.

        Args:
            path (str | Path): The path to the directory to be deleted.
        """
        # Check if path is a string
        if isinstance(path, str):
            path = Path(path)

        # If directory
        if path.is_dir():
            # Use shutil to delete directory
            shutil.rmtree(path)
        # If file
        elif path.is_file():
            # Use os to delete file
            os.remove(path)

    def delete(self) -> None:
        """Delete the database and its subdirectories."""
        # Delete subdirectories
        self._delete(self.db_path / self._cpu_db_name)
        self._delete(self.db_path / self._node_db_name)

    def remove(self, query: dict) -> None:
        """Remove a specific data entry from the database.

        Args:
            query (dict): A dictionary containing information about the data to be removed.
        """
        # Get key and filepath
        _, filepath = self._key_filepath(query)

        # Delete file
        self._delete(filepath)

    def check_integrity(self, supress: bool = False) -> bool:
        """Check the integrity of the database.

        Returns:
            bool: True if the database is intact, False otherwise.
        """
        # Check if subdirectories are empty or not
        if len(os.listdir(self.db_path / self._cpu_db_name)) == 0:
            if not supress:
                warnings.warn(f"CPU database {self.db_path} is empty.")
            return False

        if len(os.listdir(self.db_path / self._node_db_name)) != 1:
            if not supress:
                warnings.warn(f"Node database {self.db_path} is empty.")
            return False

        return True

    def _print_directory_tree(
        self, root_path: str, indent: str = "", last: bool = True
    ) -> None:
        """Print the directory tree structure.

        Args:
            root_path (str): The root directory path.
            indent (str, optional): The indentation string. Defaults to "".
            last (bool, optional): True if the current directory is the last in its level.
        """
        print(indent + ("└─ " if last else "├─ ") + os.path.basename(root_path))
        if os.path.isdir(root_path):
            entries = os.listdir(root_path)
            entries.sort()
            for i, entry in enumerate(entries):
                entry_path = os.path.join(root_path, entry)
                is_last = i == len(entries) - 1
                self._print_directory_tree(
                    entry_path, indent + ("   " if last else "│  "), last=is_last
                )

    def print(self) -> str:
        """Print the directory tree structure of the database.

        Returns:
            str: The directory tree structure.
        """
        return self._print_directory_tree(self.db_path)

    def _check_key(self, query: dict) -> str:
        """Check if the data dictionary contains a valid key.

        Args:
            query (dict): The data dictionary.

        Raises:
            KeyError: If the data dictionary does not contain a valid key.

        Returns:
            str: The valid key ('cpu' or 'node').
        """
        # Check if key contains cpu or node
        if "key" not in query:
            raise KeyError(f"Key {query} does not contain key.")

        if query["key"] not in ["cpu", "node"]:
            raise KeyError(f"Key {query} does not contain cpu or node.")

        if query["key"] == "cpu":
            return "cpu"

        return "node"

    def _key_filepath(self, query: dict) -> tuple[Path, str]:
        """Get the key and filepath from the query dictionary.

        Args:
            query (dict): The data dictionary.

        Raises:
            KeyError: If the data dictionary does not contain a valid key or filename.

        Returns:
            tuple[Path, str]: A tuple containing the key and filepath.
        """
        # Check the key
        key = self._check_key(query)

        # Check get filename
        if "filename" not in query:
            raise KeyError(f"Key {query} does not contain filename.")

        return key, self.db_path / key / query["filename"]

    def _filepath_data(self, query: dict) -> tuple[Path, str]:
        """Get the data filepath from the data dictionary.

        Args:
            query (dict): The data dictionary.

        Raises:
            KeyError: If the data dictionary does not contain a valid key, filename, or data.

        Returns:
            tuple[Path, str]: A tuple containing the filepath and data.
        """
        # Check the key
        key, filepath = self._key_filepath(query)

        if "data" not in query:
            raise KeyError(f"Key {query} does not contain data.")

        return filepath, query["data"]

    def insert(self, query: dict) -> None:
        """Insert data into the database.

        Args:
            query (dict): A dictionary containing information to be inserted into the database. It should contain the following keys:
                - key: The key of the data ('cpu' or 'node').
                - filename: The filename of the data.
                - data: The data to be inserted.
        """
        # Get filepath and data
        filepath, data = self._filepath_data(query)

        # Write data to file if exists otherwise overwrite
        with open(filepath, "w") as f:
            f.write(data)

        return

    def update(self, query: dict) -> None:
        """Update data in the database.

        Args:
            query (dict): A dictionary containing information to be updated in the database.
        """
        # Get filepath and data
        filepath, data = self._filepath_data(query)

        # If file does not exist, insert data
        if not filepath.exists():
            raise FileNotFoundError(f"File {filepath} does not exist.")

        # Write data to file
        self.insert({"key": query["key"], "filename": query["filename"], "data": data})

    def query(self, query: dict) -> pd.Series | pd.DataFrame:
        """Query data from the database based on a specified query.

        Args:
            query (dict): A dictionary containing a query to retrieve data.

        Raises:
            KeyError: If the query dictionary does not contain a valid key or filename.

        Returns:
            pd.Series | pd.DataFrame: The queried data as a Pandas Series or DataFrame.
        """
        # Empty Guards
        if self.is_empty():
            raise FileNotFoundError(f"Database {self.db_path} is empty.")

        # Get key and filepath
        key, filepath = self._key_filepath(query)

        # Change parser based on key
        if key == "cpu":
            self.parser.swap(self.iparsers["cpu"])
        elif key == "node":
            self.parser.swap(self.iparsers["node"])

        return self.parser(filepath=filepath)

    def is_cpu_file_available(self, filename: str | Path) -> bool:
        """Check if a CPU data file is available in the database.

        Args:
            filename (str | Path): The filename of the CPU data.

        Returns:
            bool: True if the CPU data file is available, False otherwise.
        """
        if isinstance(filename, str):
            filename = Path(filename)

        return (self.db_path / "cpu" / filename).exists()

    def is_node_file_available(self) -> bool:
        """Check if the node data file is available in the database.

        Returns:
            bool: True if the node data file is available, False otherwise.
        """
        if self.is_empty():
            return False

        if os.listdir(self.db_path / self._node_db_name).__len__() != 1:
            return False

        return True

    def get_cpu_file(self, filename: str | Path) -> pd.Series:
        """Get the filepath of the CPU data file.

        Args:
            filename (str | Path): The filename of the CPU data.

        Returns:
            pd.Series: The queried CPU data as a Pandas Series.
        """
        return self.query({"key": "cpu", "filename": filename})

    def get_node_file(self) -> pd.DataFrame:
        """Get the filepath of the node data file.

        Returns:
            pd.DataFrame: The queried node data as a Pandas DataFrame.
        """
        return self.query(
            {
                "key": "node",
                "filename": os.listdir(self.db_path / self._node_db_name)[0],
            }
        )

    def read_as_text(self, query: dict) -> str:
        """Read the queried data as text.

        Args:
            query (dict): A dictionary containing a query to retrieve data.

        Returns:
            str: The queried data as text.
        """
        # Get key and filepath
        key, filepath = self._key_filepath(query)

        # Read data from file
        with open(filepath) as f:
            return f.read()

    def __getitem__(self, key: dict) -> pd.Series | pd.DataFrame:
        """Implement the [] operator for querying data from the database.

        Args:
            key (dict): A dictionary containing a query to retrieve data.

        Returns:
            pd.Series | pd.DataFrame: The queried data as a Pandas Series or DataFrame.
        """
        return self.query(key)

    def coverage(self) -> float:
        """Calculate the coverage of the database based on available node and CPU data.

        Returns:
            float: The coverage of the database as a percentage.
        """
        if not self.is_node_file_available():
            raise FileNotFoundError(
                f"Node file not found in {self.db_path}. Need Node file to calculate coverage."
            )

        # Get node data
        node_df = self.query(
            {
                "key": "node",
                "filename": os.listdir(self.db_path / self._node_db_name)[0],
            }
        )

        # Get all the NodeName
        node_names = node_df["NodeName"]

        # Check cpu files named nodename.txt are available or not
        cpu_files = [
            self.is_cpu_file_available(node_name + ".txt") for node_name in node_names
        ]

        # Calculate coverage
        return sum(cpu_files) * 100 / len(cpu_files)

    def __len__(self) -> int:
        """Return the number of files in the database.

        Returns:
            int: The number of files in the database.
        """
        return len(os.listdir(self.db_path / self._cpu_db_name)) + len(
            os.listdir(self.db_path / self._node_db_name)
        )

    def __iter__(self) -> pd.Series:
        """_summary_.

        Returns:
            pd.Series: _description_
        """
        # Empty Guards
        if self.is_empty():
            raise FileNotFoundError(f"Database {self.db_path} is empty.")

        # Iterator over the cpu files
        for cpu_file in os.listdir(self.db_path / self._cpu_db_name):
            yield self.query({"key": "cpu", "filename": cpu_file})
