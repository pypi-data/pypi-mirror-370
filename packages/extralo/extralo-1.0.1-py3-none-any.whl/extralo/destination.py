from abc import ABC, abstractmethod

from extralo.typing import DataFrame


class Destination(ABC):
    """Abstract base class for data sources."""

    @abstractmethod
    def load(self, data: DataFrame) -> None:
        """Load the given data into the destination.

        Args:
            data (DataFrame): The data to be loaded into the destination.

        Raises:
            NotImplementedError: This method is not implemented and should be overridden in a subclass.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return self.__class__.__name__

    def __str__(self) -> str:
        return self.__repr__()
