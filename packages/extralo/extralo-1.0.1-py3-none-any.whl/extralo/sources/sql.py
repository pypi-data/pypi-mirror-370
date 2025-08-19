from typing import Any, Optional

import pandas as pd

from extralo.source import Source
from extralo.typing import DataFrame


class SQLSource(Source):
    """A class representing a SQL data source.

    Requires sqlparse and sqlalchemy to be installed. The SQL query is executed using the provided database engine.
    The query can have multiple statements, separated by semicolons. The last one must return some data.

    Args:
        engine (object): The database engine object.
        query (str): The SQL query to execute.
        params (dict, optional): The parameters to be passed to the SQL query. Defaults to None.
    """

    def __init__(self, engine: Any, query: str, params: Optional[dict[str, Any]] = None) -> None:
        try:
            import sqlalchemy as sa  # noqa: F401
            import sqlalchemy.exc as sa_exc  # noqa: F401
        except ImportError as err:
            raise ImportError(
                "SQLAlchemy is required to use SQLSource. Please install it with `pip install sqlalchemy`."
            ) from err
        try:
            import sqlparse as sp  # noqa: F401
        except ImportError as err:
            raise ImportError(
                "sqlparser is required to use SQLSource. Please install it with `pip install sqlparser`."
            ) from err
        self._engine = engine
        self._query = query
        self._params = params or {}

    def extract(self) -> DataFrame:
        """Extracts data from the database using the provided SQL query.

        Returns:
            DataFrame: The extracted data as a pandas DataFrame.
        """
        import sqlalchemy as sa
        import sqlalchemy.exc as sa_exc
        import sqlparse as sp

        query = sp.split(self._query)
        with self._engine.begin() as connection:
            for statement in query[:-1]:
                connection.execute(
                    sa.text(statement), parameters=self._params, execution_options={"no_parameters": True}
                )
            try:
                data = pd.read_sql(sa.text(query[-1]), connection, params=self._params)
            except sa_exc.ProgrammingError:
                data = pd.read_sql(sa.text(query[-1]), connection)

        return data

    def __repr__(self) -> str:
        return f"SQLSource(engine={self._engine})"
