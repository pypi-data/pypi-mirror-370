from typing import Any, Optional, Protocol

DataFrame = Any


class DataFrameModel(Protocol):  # noqa: D101
    def validate(  # noqa: D102
        self,
        check_obj: DataFrame,
        head: Optional[int] = None,
        tail: Optional[int] = None,
        sample: Optional[int] = None,
        random_state: Optional[int] = None,
        lazy: bool = False,
        inplace: bool = False,
    ) -> DataFrame: ...
