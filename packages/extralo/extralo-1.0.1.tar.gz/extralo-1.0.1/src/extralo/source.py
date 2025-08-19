from abc import ABC, abstractmethod

from extralo.typing import DataFrame


class Source(ABC):
    """Abstract base class for data sources."""

    @abstractmethod
    def extract(self) -> DataFrame:
        """Extracts data from a source and returns it as a DataFrame.

        Returns:
            DataFrame: The extracted data.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return self.__class__.__name__

    def __str__(self) -> str:
        return self.__repr__()
