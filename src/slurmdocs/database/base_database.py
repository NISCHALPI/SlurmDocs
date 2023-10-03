"""Database Module for SlurmDocs.

This module provides the foundation for database functionality within the SlurmDocs application. It defines an abstract
base class (ABC) called BaseDatabase, which serves as a blueprint for all database implementations within SlurmDocs.

BaseDatabase defines a common interface and structure for database-related operations, including database creation,
deletion, integrity checking, data insertion, updating, querying, and more.

Subclasses of BaseDatabase should implement these methods to create specific database implementations, such as file-based,
SQL, or NoSQL databases.

Classes:
    BaseDatabase (ABC): The abstract base class for all database implementations in SlurmDocs.

Example:
    To create a custom database implementation for SlurmDocs, you should subclass BaseDatabase and provide
    implementations for its abstract methods.

    ```python
    from abc import ABC, abstractmethod
    from pathlib import Path

    class MyDatabase(BaseDatabase):
        def __init__(self, db_path: str | Path) -> None:
            super().__init__(db_path)

        # Implement abstract methods here...
    ```

Note:
    This module is part of the SlurmDocs application and should be used in conjunction with other components
    to build a complete documentation management system.

For more information on how to use and extend the database module, refer to the documentation or README provided
with the SlurmDocs project.

Author:
    Your Name nischalbhattaraipi@gmail.com
"""


from abc import ABC, abstractmethod
from pathlib import Path


class BaseDatabase(ABC):
    """Database module for SlurmDocs.

    This class serves as the base for all database implementations within SlurmDocs. It provides common functionality
    and defines the structure for database-related operations.

    Args:
        db_path (str or Path): The path to the database directory.

    Attributes:
        db_path (Path): The validated path to the database directory.

    Methods:
        __init__(self, db_path: str | Path) -> None:
            Constructor for the BaseDatabase class. Initializes the database path and validates it.

        _validate_db_path(db_path: str | Path) -> None:
            Validate the provided database path.

        create() -> None:
            Create the database. This method should create the necessary directory structure.

        delete() -> None:
            Delete the database.

        check_integrity() -> bool:
            Check the integrity of the database. This method checks if the database is in a valid state.

        is_empty() -> bool:
            Check if the database is empty.

        print() -> str:
            Print the database.

        insert(data: dict) -> None:
            Insert data into the database.

        update(data: dict) -> None:
            Update data in the database.

        query(query: str) -> list:
            Query data from the database based on a query string.

        __repr__() -> str:
            Return the representation of the database.

        __str__() -> str:
            Return the string representation of the database.
    """

    def __init__(self, db_path: str | Path) -> None:
        """Constructor for the BaseDatabase class.

        Initializes the database path and validates it.

        Args:
            db_path (str or Path): The path to the database directory.
        """
        self._validate_db_path(db_path)
        self.db_path = Path(db_path)

    def _validate_db_path(self, db_path: str | Path) -> None:
        """Validate the provided database path.

        Args:
            db_path (str or Path): The path to the database directory.
        """
        if isinstance(db_path, str):
            db_path = Path(db_path)

        if not db_path.exists():
            raise FileNotFoundError(f"Database path {db_path} does not exist.")
        if not db_path.is_dir():
            raise NotADirectoryError(f"Database path {db_path} is not a directory.")

    @abstractmethod
    def create(self) -> None:
        """Create the database.

        This method should create the necessary directory structure.
        """
        pass

    @abstractmethod
    def delete(self) -> None:
        """Delete the database."""
        pass

    @abstractmethod
    def check_integrity(self) -> bool:
        """Check the integrity of the database.

        This method checks if the database is in a valid state.

        Returns:
            bool: True if the database is in a valid state, False otherwise.
        """
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        """Check if the database is empty.

        This method checks if the database is empty.

        Returns:
            bool: True if the database is empty, False otherwise.
        """
        pass

    @abstractmethod
    def print(self) -> None:
        """Print the database."""
        pass

    @abstractmethod
    def insert(self, data: dict) -> None:
        """Insert data into the database.

        Args:
            data (dict): The data to be inserted into the database.
        """
        pass

    @abstractmethod
    def update(self, data: dict) -> None:
        """Update data in the database.

        Args:
            data (dict): The data to be updated in the database.
        """
        pass

    @abstractmethod
    def query(self, query: str) -> list:
        """Query data from the database based on a query string.

        Args:
            query (str): The query string.

        Returns:
            list: A list of results that match the query.
        """
        pass

    def __repr__(self) -> str:
        """Return the representation of the database.

        Returns:
            str: A string representation of the database.
        """
        return f"{self.__class__.__name__}(db_path={self.db_path})"

    def __str__(self) -> str:
        """Return the string representation of the database.

        Returns:
            str: A string representation of the database.
        """
        return self.__repr__()
