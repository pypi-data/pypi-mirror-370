from typing import Annotated, Union

from pydantic import Field

from .console import Console
from .restapi import RestAPI

Metric = Annotated[
    Union[
        Console,
        RestAPI,
    ],
    Field(
        discriminator="type",
        description="A metric model registry",
    ),
]
ListMetric = list[Metric]
