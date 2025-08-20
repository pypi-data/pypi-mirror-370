from typing import Annotated, Union

from pydantic import Field

from .files.local import LocalCSVFile, LocalJsonFile
from .files.s3 import S3CSVFile

LocalFile = Annotated[
    Union[
        LocalCSVFile,
        LocalJsonFile,
    ],
    Field(discriminator="file_format"),
]

S3File = Annotated[
    Union[S3CSVFile,],
    Field(discriminator="file_format"),
]

Source = Annotated[
    Union[
        LocalFile,
        S3File,
    ],
    Field(discriminator="type"),
]
