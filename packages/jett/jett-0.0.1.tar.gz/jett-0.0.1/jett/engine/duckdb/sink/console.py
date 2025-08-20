import logging
from typing import Any, Literal

import duckdb

from ....__types import DictData
from ....models import Shape
from ...__abc import BaseSink

logger = logging.getLogger("jett")


class Console(BaseSink):
    """Console DuckDB Sink model."""

    type: Literal["console"]
    limit: int = 10
    max_width: int | None = None

    def save(
        self,
        df: duckdb.DuckDBPyRelation,
        *,
        engine: DictData,
        **kwargs,
    ) -> Any:
        """Save the result data to the Console."""
        logger.info("🎯 Sink - Start sync with console")
        df.show(max_rows=self.limit, max_width=self.max_width)
        return df, Shape.from_tuple(df.shape)

    def outlet(self) -> tuple[str, str]:
        return "console", self.dest()

    def dest(self) -> str:
        return "console"
