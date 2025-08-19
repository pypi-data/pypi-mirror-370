import os.path
from abc import ABC
from typing import Any

import pandas as pd

from extralo.destination import Destination


class FileDestination(Destination, ABC):
    """Represents a destination that writes data to a file.

    Args:
        file (str): The path to the file.
        **kwargs: Additional keyword arguments to be passed to the load function.
    """

    def __init__(self, file: str, **kwargs: Any) -> None:
        self._file = file
        self._kwargs = kwargs

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(file={self._file})"


class CSVDestination(FileDestination):
    """A destination class for saving data to a CSV file."""

    def load(self, data: pd.DataFrame) -> None:
        """Save the given pandas DataFrame to a CSV file.

        If the file already exists, it will be overwritten.

        Args:
            data (DataFrame): The DataFrame to be saved.
        """
        data.to_csv(self._file, **self._kwargs)


class XLSXDestination(FileDestination):
    """A destination class for saving data to a XLSX file."""

    def load(self, data: pd.DataFrame) -> None:
        """Save the given pandas DataFrame to a XLSX file.

        If the file already exists, it will be overwritten.

        Args:
            data (DataFrame): The DataFrame to be saved.
        """
        data.to_excel(self._file, **self._kwargs)


class XLSXAppendDestination(FileDestination):
    """A destination class for appending data to a XLSX file.

    This class cannot be used with the parallel ETL.
    """

    def __init__(self, file: str, mode: str, if_sheet_exists: str = None, **kwargs: Any) -> None:
        super().__init__(file, **kwargs)
        self._mode = mode
        self._if_sheet_exists = if_sheet_exists

    def load(self, data: pd.DataFrame) -> None:
        """Append the given pandas DataFrame to a XLSX file.

        Args:
            data (DataFrame): The DataFrame to be saved.
        """
        with pd.ExcelWriter(self._file, mode=self._mode, if_sheet_exists=self._if_sheet_exists) as writer:
            data.to_excel(writer, **self._kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(file={self._file}, mode={self._mode})"


class CSVAppendDestination(FileDestination):
    """A destination class for appending data to a CSV file."""

    def load(self, data: pd.DataFrame) -> None:
        """Append the given pandas DataFrame to a CSV file.

        If the file already exists, it will be appended, and will be assumed that the headers
        are in the same order.

        Args:
            data (DataFrame): The DataFrame to be saved.
        """
        if os.path.isfile(self._file):
            data.to_csv(self._file, mode="a", header=False, **self._kwargs)
            return
        data.to_csv(self._file, mode="w", header=True, **self._kwargs)
