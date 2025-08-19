from abc import ABC, abstractmethod

from extralo.typing import DataFrame


class Transformer(ABC):
    """Abstract base class for transformers.

    This class defines the interface for transformers in the extralo package.
    Subclasses should implement the `transform` method.
    """

    @abstractmethod
    def transform(self, **kwargs: DataFrame) -> dict[str, DataFrame]:
        """Transforms the input data using the specified transformations.

        Parameters:
            **kwargs (DataFrame): Input dataframes to be transformed.

        Returns:
            dict[str, DataFrame]: A dictionary containing the transformed dataframes.

        Raises:
            NotImplementedError: This method needs to be implemented in a subclass.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return self.__class__.__name__

    def __str__(self) -> str:
        return self.__repr__()
