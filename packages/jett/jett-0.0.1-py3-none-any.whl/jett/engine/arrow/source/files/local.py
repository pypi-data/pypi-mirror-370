from typing import Any, Literal

from jett import Shape
from jett.__types import DictData
from jett.models import MetricSource

from ....__abc import BaseSource


class LocalJsonFile(BaseSource):
    type: Literal["local"]
    file_format: Literal["json"]
    path: str

    def load(
        self,
        engine: DictData,
        metric: MetricSource,
        **kwargs,
    ) -> tuple[Any, Shape]: ...

    def inlet(self) -> tuple[str, str]: ...
