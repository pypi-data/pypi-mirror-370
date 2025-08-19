from typing import Any, Literal

import pandas as pd

from extralo.destination import Destination


class SQLDestination(Destination):
    """A class representing a SQL destination for loading data.

    Args:
        engine (sa.Engine): The SQLAlchemy engine to connect to the database.
        table (str): The name of the table to load the data into.
        schema (str): The name of the schema where the table resides.
        if_exists (str): The action to take if the table already exists.
    """

    def __init__(self, engine: Any, table: str, schema: str, if_exists: Literal["fail", "replace", "append"]) -> None:
        try:
            import sqlalchemy  # noqa: F401
        except ImportError as err:
            raise ImportError(
                "SQLAlchemy is required to use SQLDestination. Please install it with `pip install sqlalchemy`."
            ) from err
        self._engine = engine
        self._table = table
        self._if_exists = if_exists
        self._schema = schema

    def load(self, data: pd.DataFrame) -> None:
        """Loads the given pandas DataFrame into an SQL table.

        Args:
            data (DataFrame): The pandas DataFrame to be loaded.
        """
        data.to_sql(name=self._table, schema=self._schema, con=self._engine, if_exists=self._if_exists, index=False)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(table={self._table}, schema={self._schema}, if_exists={self._if_exists})"


class SQLAppendDestination(SQLDestination):
    """A destination class for appending data to an SQL table, overriding by group.

    Args:
        engine (sa.Engine): The SQLAlchemy engine object.
        table (str): The name of the table.
        schema (str): The name of the schema.
        group_column (str): The name of the column used for grouping.
        group_value (Any): The value of the group column.
    """

    def __init__(self, engine: Any, table: str, schema: str, group_column: str, group_value: Any) -> None:
        try:
            import sqlalchemy  # noqa: F401
        except ImportError as err:
            raise ImportError(
                "SQLAlchemy is required to use SQLAppendDestination. Please install it with `pip install sqlalchemy`."
            ) from err

        super().__init__(engine, table, schema, "append")
        self._group_column = group_column
        self._group_value = group_value

    def load(self, data: pd.DataFrame) -> None:
        """Load data into the SQL table after deleting rows with a specific group value.

        Args:
            data (DataFrame): The data to be loaded into the table.

        Raises:
            KeyError: If the specified group column is not found in the table.
        """
        import sqlalchemy as sa

        insp = sa.inspect(self._engine)
        if insp.has_table(self._table, self._schema):
            metadata_obj = sa.MetaData()
            table = sa.Table(self._table, metadata_obj, autoload_with=self._engine, schema=self._schema)
            if self._group_column not in table.c:
                raise KeyError(f"Column '{self._group_column}' not found in table '{self._table}'")
            stmt = sa.delete(table).where(table.c[self._group_column] == self._group_value)
            with self._engine.begin() as conn:
                conn.execute(stmt)

        super().load(data)
