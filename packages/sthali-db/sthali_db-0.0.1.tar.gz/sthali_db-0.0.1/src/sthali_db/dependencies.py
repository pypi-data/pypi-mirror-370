"""This module provides the dependencies for sthali-db usage.

Classes:
    PaginateParameters: Represents the parameters for retrieving items.

Functions:
    filter_parameters: Not implemented. Raises NotImplementedError.
"""

import typing

import pydantic


async def filter_parameters() -> typing.NoReturn:
    """Not implemented."""
    raise NotImplementedError


class PaginateParameters(pydantic.BaseModel):
    """Represents the parameters for retrieving items.

    Attributes:
        skip (pydantic.NonNegativeInt): The number of items to skip. Defaults to 0.
        limit (pydantic.NonNegativeInt): The maximum number of items to return. Defaults to 100.
    """

    skip: typing.Annotated[
        pydantic.NonNegativeInt,
        pydantic.Field(default=0, description="The number of items to skip"),
    ]
    limit: typing.Annotated[
        pydantic.NonNegativeInt,
        pydantic.Field(default=100, description="The maximum number of items to return"),
    ]
