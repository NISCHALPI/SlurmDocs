"""Parses Slurm's 'scontrol show node' output.

This class, 'Iscontrol', is designed to parse information from the output of the 'scontrol show node' command in Slurm, converting it into a pandas DataFrame for easier manipulation and analysis.

Attributes:
    None

Methods:
    - __init__(self, preprocess: bool = True) -> None: Initializes the Iscontrol object.
    - _per_node_filter(self, node: str) -> dict: Parses a single node's information from the command output.
    - _parse_scontrol(self, string: str) -> pd.DataFrame: Parses the entire 'scontrol show node' output.
    - _gpu_filter(gpu: str | None) -> str | None: Filters and extracts GPU information from the 'Gres' field.
    - _partitionize(self, dataframe: pd.DataFrame) -> pd.DataFrame: Converts the 'Partitions' field into separate columns.
    - _preprocess_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame: Preprocesses the DataFrame by dropping redundant columns and filtering GPU information.

Usage:
    1. Create an 'Iscontrol' object, optionally specifying whether to preprocess the DataFrame.
    2. Use the '_parse' method to parse 'scontrol show node' output from a file and obtain the parsed data as a pandas DataFrame.

Example:
    ```python
    from my_parsing_module import Iscontrol

    scontrol_parser = Iscontrol(preprocess=True)  # Instantiate the Slurm scontrol parser with preprocessing
    parsed_data = scontrol_parser._parse(Path('scontrol_output.txt'))  # Parse Slurm scontrol data from a file
    ```

Returns:
    pd.DataFrame: Parsed data stored as a pandas DataFrame.
"""

import re
from pathlib import Path

import pandas as pd

from .base_iparse import IParse

__all__ = ["IscontrolParser"]


class IscontrolParser(IParse):
    """Parses Slurm's 'scontrol show node' output.

    This class, 'Iscontrol', is designed to parse information from the output of the 'scontrol show node' command in Slurm, converting it into a pandas DataFrame for easier manipulation and analysis.

    Attributes:
    None

    Methods:
    - __init__(self, preprocess: bool = True) -> None: Initializes the Iscontrol object.
    - _per_node_filter(self, node: str) -> dict: Parses a single node's information from the command output.
    - _parse_scontrol(self, string: str) -> pd.DataFrame: Parses the entire 'scontrol show node' output.
    - _gpu_filter(gpu: str | None) -> str | None: Filters and extracts GPU information from the 'Gres' field.
    - _partitionize(self, dataframe: pd.DataFrame) -> pd.DataFrame: Converts the 'Partitions' field into separate columns.
    - _preprocess_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame: Preprocesses the DataFrame by dropping redundant columns and filtering GPU information.
    - _parse(self, filename: Path) -> pd.DataFrame: Parses 'scontrol show node' output from a file.

    Usage:
    1. Create an 'Iscontrol' object, optionally specifying whether to preprocess the DataFrame.
    2. Use the '_parse' method to parse 'scontrol show node' output from a file and obtain the parsed data as a pandas DataFrame.

    Example:
    ```python
    from my_parsing_module import Iscontrol

    scontrol_parser = Iscontrol(preprocess=True)  # Instantiate the Slurm scontrol parser with preprocessing
    parsed_data = scontrol_parser._parse(Path('scontrol_output.txt'))  # Parse Slurm scontrol data from a file
    ```

    Returns:
    pd.DataFrame: Parsed data stored as a pandas DataFrame.
    """

    def __init__(self, preprocess: bool = True) -> None:
        """Initialize the Iscontrol object.

        Args:
        preprocess (bool, optional): Whether to preprocess the DataFrame by dropping redundant columns and filtering GPU information. Defaults to True.
        """
        # Choose whether to preprocess the dataframe or not
        self.preprocess = preprocess
        super().__init__("lscpu")

    def _per_node_filter(self, node: str) -> dict:
        """Per node filter to convert the output of scontrol show node to a dictionary.

        Args:
        node (str): A string containing information about a single node.

        Returns:
        dict: A dictionary containing parsed node information.
        """
        node = (
            node.replace("\n", "")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace(" ", "@")
            .replace("(null)", "")
            .replace("N/A", "")
            .replace("n/a", "")
            .replace("n/s", "")
        )

        node = node.split("@")
        ret_dic = {}
        for item in node:
            if item.count("=") >= 1:
                key, value = item.split("=", maxsplit=1)
                if value == "" or value == " ":
                    value = None

                # Convert to int if possible
                try:
                    value = int(value)
                except:  # noqa: E722
                    pass

                ret_dic[key] = value

        return ret_dic

    def _parse_scontrol(self, string: str) -> pd.DataFrame:
        """Parse the output of 'scontrol show node' and convert it into a DataFrame.

        Args:
        string (str): The output of 'scontrol show node' as a string.

        Returns:
        pd.DataFrame: Parsed data stored as a pandas DataFrame.
        """
        # Split the string into nodes
        nodes = string.split("\n\n")

        # Remove empty lines
        nodes = list(filter(lambda x: len(x) > 0, nodes))

        # Convert each node to a dictionary
        nodes = list(map(self._per_node_filter, nodes))

        # Convert the list of dictionaries to a dataframe
        return pd.DataFrame(nodes)

    @staticmethod
    def _gpu_filter(gpu: str | None) -> str | None:
        """Filter and extract GPU information from the 'Gres' field.

        Args:
        gpu (str | None): A string containing GPU information or None if no GPU information is present.

        Returns:
        str | None: Extracted GPU information as a string or None if no GPU information is present.
        """
        if gpu is None:
            return None

        # Define a regular expression pattern to match GPU entries
        gpu_pattern = r"gpu:([a-zA-Z0-9-]+:\d+)"

        # Find all GPU matches in the text
        gpu_matches = re.findall(gpu_pattern, gpu)

        # Join the matches into a single string by comma
        return ",".join(gpu_matches)

    def _partitionize(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Convert the 'Partitions' field into separate columns in the DataFrame.

        Args:
        dataframe (pd.DataFrame): The DataFrame containing node information.

        Returns:
        pd.DataFrame: The DataFrame with separate columns for partitions.
        """
        # Seprate partioions inot different columns
        unique_partitions = dataframe["Partitions"].str.split(",").explode().unique()

        partition_dataframe = pd.DataFrame(
            index=dataframe.index, columns=unique_partitions, dtype=bool
        )  # noqa: ARG005

        # Use XOR to fill the dataframe with False
        partition_dataframe = partition_dataframe ^ partition_dataframe

        for index, row in dataframe.iterrows():
            for partition in row["Partitions"].split(","):
                partition_dataframe.loc[index, partition] = True

        # Add a partition identifier to columns name
        partition_dataframe.columns = [
            col + "_PRT" for col in partition_dataframe.columns
        ]

        # Concatenate the partition dataframe with the original dataframe
        dataframe = pd.concat([dataframe, partition_dataframe], axis=1)
        # Drop the redundant columns
        dataframe.drop("Partitions", axis=1, inplace=True)
        return dataframe

    def _preprocess_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Preprocess the DataFrame by dropping redundant columns and filtering GPU information.

        Args:
        dataframe (pd.DataFrame): The DataFrame containing node information.

        Returns:
        pd.DataFrame: The preprocessed DataFrame.
        """
        # Drop the redundant columns of temporary state
        redundant_columns = [
            "Arch",  # Architecture of the node. Almost Always x86_6
            "Version",  # Version of the slurm software running on the node
            "OS",  # Operating system of the node
            "ActiveFeatures",  # Features of the node
            "AllocTRES",  # TRES allocated to the node
            "CfgTRES",  # TRES configured on the node
            "Comment",  # Comment on the node
            "TmpDisk",  # Temporary disk space on the node
            "Weight",  # Weight of the node
            "BootTime",  # Boot time of the node
            "SlurmdStartTime",  # Start time of the slurmd daemon on the node
            "CapWatts",  # Power consumption of the node
            "CurrentWatts",  # Current power consumption of the node
            "AveWatts",  # Average power consumption of the node
            "ExtSensorsJoules",  # Energy consumption of the node
            "ExtSensorsWatts",  # Power consumption of the node
            "MCS_label",  # Label of the node
            "Owner",  # Owner of the node
            "State",  # State of the node
            "ExtSensorsTemp",  # Temperature of the node
            "CPULoad",  # CPU load of the node
            "CPUAlloc",  # CPU allocation of the node
            "FreeMem",  # Free memory of the node
            "AllocMem",  # Allocated memory of the node
            "MemSpecLimit",  # Memory specification limit of the node
        ]

        # GPU model filter
        dataframe["Gres"] = dataframe["Gres"].apply(self._gpu_filter)

        return dataframe.drop(columns=redundant_columns)

    def _parse(self, filename: Path) -> pd.Series:
        """Parse 'scontrol show node' output from a file and return the parsed data as a DataFrame.

        Args:
        filename (Path): The path to the file containing 'scontrol show node' output.

        Returns:
        pd.DataFrame: Parsed data stored as a pandas DataFrame.
        """
        with open(filename) as f:
            string = f.read()

        # Parse the data
        df = self._parse_scontrol(string=string)

        # Partitionize the dataframe
        df = self._partitionize(dataframe=df)

        # Preprocess the dataframe
        if self.preprocess:
            return self._preprocess_dataframe(df)

        return df
