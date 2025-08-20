from typing import Annotated, Union

from pydantic import Field

from .dbt import Dbt
from .duckdb import DuckDB
from .polars import Polars
from .spark import Spark

Engine = Annotated[
    Union[
        Polars,
        DuckDB,
        Spark,
        Dbt,
    ],
    Field(
        discriminator="type",
        description="The main engine registry models for operator model.",
    ),
]
