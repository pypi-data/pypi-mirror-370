from typing import Any, Literal, Optional, Union

from extralo.destination import Destination
from extralo.typing import DataFrame


class DeltaLakeDestination(Destination):
    """A destination class for saving data to a Delta Lake table.

    Args:
        table_uri (str): The path to the Delta Lake table.
        **kwargs: Additional keyword arguments to be passed to the save function.
    """

    def __init__(
        self,
        table_uri: str,
        mode: Literal["error", "append", "overwrite", "ignore"],
        partition_by: Optional[Union[list[str], str]] = None,
        schema: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        try:
            import deltalake  # noqa: F401
        except ImportError as err:
            raise ImportError(
                "DeltaLake is required to use DeltaLakeDestination. Please install it with `pip install deltalake`."
            ) from err
        self._table_uri = table_uri
        self._mode = mode
        self._partition_by = partition_by
        self._kwargs = kwargs
        self._schema = schema

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(table={self._table_uri}, mode={self._mode})"

    def load(self, data: DataFrame) -> None:
        """Loads the given DataFrame into the Delta Lake table.

        Args:
            data (DataFrame): The DataFrame to be loaded.
        """
        import deltalake as dl

        if self._schema:
            import pyarrow as pa

            data = pa.Table.from_pandas(data).cast(self._schema)

        dl.write_deltalake(
            table_or_uri=self._table_uri, data=data, mode=self._mode, partition_by=self._partition_by, **self._kwargs
        )


class SparkDeltaLakeDestination(Destination):
    """A class to handle data loading into a Delta Lake table using Apache Spark.

    Args:
        spark (SparkSession): The Spark session to use for data operations.
        table (str): The name of the Delta Lake table.
        mode (Literal["error", "append", "overwrite", "ignore"]): The mode for writing data.
        partition_by (Optional[Union[list[str], str]]): Columns to partition the data by.
        replace_where (Optional[str]): SQL condition to replace data that matches the condition.
        **kwargs: Additional keyword arguments to be passed to the save function.
    """

    def __init__(
        self,
        spark,
        table: str,
        mode: Literal["error", "append", "overwrite", "ignore"],
        partition_by: Optional[Union[list[str], str]] = None,
        replace_where: Optional[str] = None,
        schema=None,
        **kwargs: Any,
    ):
        self._spark = spark
        self._table = table
        self._mode = mode
        self._partition_by = partition_by
        self._replace_where = replace_where or "true"
        self._kwargs = kwargs
        self._schema = schema

    def load(self, data: DataFrame):
        """Loads the provided data into the Delta Lake table.

        Args:
            data (DataFrame): The data to be loaded into the Delta Lake table.
        """
        df = self._spark.createDataFrame(data, schema=self._schema)
        df.write.saveAsTable(
            self._table,
            replaceWhere=self._replace_where,
            mode=self._mode,
            partitionBy=self._partition_by,
            format="delta",
            **self._kwargs,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(table={self._table}, mode={self._mode})"
