from abc import ABC
from typing import Any

import pandas as pd

from extralo.source import Source
from extralo.typing import DataFrame


class FileSource(Source, ABC):
    """Represents a file source.

    Args:
        file (str): The path to the file.
        **kwargs: Additional keyword arguments to be passed to the read function.
    """

    def __init__(self, file: str, **kwargs: Any) -> None:
        self._file = file
        self._kwargs = kwargs

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(file={self._file})"


class CSVSource(FileSource):
    """A class representing a CSV data source.

    This class inherits from the FileSource class and provides a method to extract data from a CSV file.
    """

    def __init__(self, file: str, **kwargs: Any) -> None:
        super().__init__(file, **kwargs)

    def extract(self) -> DataFrame:
        """Extracts data from a CSV file.

        Returns:
            DataFrame: The extracted data as a pandas DataFrame.
        """
        data: pd.DataFrame = pd.read_csv(self._file, **self._kwargs)
        return data


class XLSXSource(FileSource):
    """A class representing an XLSX data source.

    This class inherits from the FileSource class and provides a method to extract data from a XLSX file.
    """

    def __init__(self, file: str, **kwargs: Any) -> None:
        super().__init__(file, **kwargs)

    def extract(self) -> DataFrame:
        """Extracts data from an Excel file.

        Returns:
            DataFrame: The extracted data.
        """
        data: pd.DataFrame = pd.read_excel(self._file, **self._kwargs)
        return data


class SASSource(FileSource):
    """A class representing an SAS data source.

    This class inherits from the FileSource class and provides a method to extract data from a XLSX file.
    """

    def extract(self) -> Any:
        """Extracts data from an SAS file.

        Returns:
            DataFrame: The extracted data.
        """
        return pd.read_sas(self._file, **self._kwargs)
