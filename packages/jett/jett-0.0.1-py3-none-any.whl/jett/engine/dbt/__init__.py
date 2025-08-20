from typing import Any, Literal

from ... import Result
from ...__types import DictData
from ...models import Context, MetricEngine, MetricTransform
from ..__abc import BaseEngine


class Dbt(BaseEngine):
    type: Literal["dbt"]

    def execute(
        self,
        context: Context,
        engine: DictData,
        metric: MetricEngine,
    ) -> Any: ...

    def set_engine_context(self, context: Context, **kwargs) -> DictData: ...

    def set_result(self, df: Any, context: Context) -> Result: ...

    def apply(
        self,
        df: Any,
        context: Context,
        engine: DictData,
        metric: MetricTransform,
        **kwargs,
    ) -> Any: ...
