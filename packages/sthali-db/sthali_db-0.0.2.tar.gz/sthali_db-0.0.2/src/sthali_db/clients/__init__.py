"""This module provides a high-level interface for interacting with different database clients.

Constants:
    ResourceTable(str): The name of the table in the database.
    ResourceId(uuid.UUID): The unique identifier of the resource.
    ResourceObj(dict[str, typing.Any]): The resource object.
    Partial(bool | None): Perform a partial update.

Classes:
    Base(path: str, table: ResourceTable): Base client class for interacting with a database.
"""

import typing
import uuid

import fastapi
import pydantic

from .. import dependencies

ResourceTable = typing.Annotated[str, pydantic.Field(description="The name of the table in the database")]
ResourceId = typing.Annotated[
    uuid.UUID, pydantic.Field(default_factory=uuid.uuid4, description="The unique identifier of the resource"),
]
ResourceObj = typing.Annotated[
    dict[str, typing.Any], pydantic.Field(default_factory=dict, description="The resource object"),
]
Partial = typing.Annotated[bool | None, pydantic.Field(description="Perform a partial update")]


class Base:
    """Base client class for interacting with a database.

    Provides the basic interface for performing CRUD operations on a database. Derived classes should implement the
    specific methods for each operation.

    Attributes:
        exception (fastapi.HTTPException): The exception module to be used for raising HTTP exceptions.
        status (fastapi.status): The status module to be used for HTTP status codes.

    Args:
        path (str): The path to the database.
        table (ResourceTable): The name of the table in the database.

    Methods:
        insert_one(resource_id: ResourceId, resource_obj: ResourceObj): Inserts a resource object in the database.
            Returns ResourceObj.
        select_one(resource_id: ResourceId): Retrieves a resource from the database based on the given ID. Returns
            ResourceObj.
        update_one(resource_id: ResourceId, resource_obj: ResourceObj, partial: Partial = None): Updates a resource in
            the database based on the given ID. Returns ResourceObj.
        delete_one(resource_id: ResourceId): Deletes a resource from the database based on the given resource ID.
            Returns None.
        select_many(paginate_parameters: dependencies.PaginateParameters): Retrieves multiple resources from the
            database based on the given pagination parameters. Returns list[ResourceObj].
    """

    exception = fastapi.HTTPException
    status = fastapi.status

    def __init__(self, path: str, table: ResourceTable) -> None:
        """Initialize the Base class.

        Args:
            path (str): The path to the database.
            table (ResourceTable): The name of the table in the database.
        """
        self.path = path
        self.table = table

    async def insert_one(self, resource_id: ResourceId, resource_obj: ResourceObj) -> ResourceObj:
        """Inserts a resource object in the database.

        Args:
            resource_id (ResourceId): The ID of the resource to be inserted.
            resource_obj (ResourceObj): The resource object to be inserted.

        Returns:
            ResourceObj: The resource object containing the ID.

        Raises:
            self.exception: If the resource already exists in the database.
        """
        raise NotImplementedError

    async def select_one(self, resource_id: ResourceId) -> ResourceObj:
        """Retrieves a resource from the database based on the given ID.

        Args:
            resource_id (ResourceId): The ID of the resource to be retrieved.

        Returns:
            ResourceObj: The retrieved resource object.

        Raises:
            self.exception: If the resource is not found in the database.
        """
        raise NotImplementedError

    async def update_one(
        self,
        resource_id: ResourceId,
        resource_obj: ResourceObj,
        partial: Partial = None,
    ) -> ResourceObj:
        """Updates a resource in the database based on the given ID.

        Args:
            resource_id (ResourceId): The ID of the resource to be updated.
            resource_obj (ResourceObj): The resource object to be updated.
            partial (Partial): Whether to perform a partial update or replace the entire resource object.
                Defaults to None.

        Returns:
            ResourceObj: The resource object containing the ID.

        Raises:
            self.exception: If the resource is not found in the database.
        """
        raise NotImplementedError

    async def delete_one(self, resource_id: ResourceId) -> None:
        """Deletes a resource from the database based on the given resource ID.

        Args:
            resource_id (ResourceId): The ID of the resource to be deleted.

        Returns:
            None

        Raises:
            self.exception: If the resource is not found in the database.
        """
        raise NotImplementedError

    async def select_many(self, paginate_parameters: dependencies.PaginateParameters) -> list[ResourceObj]:
        """Retrieves multiple resources from the database based on the given pagination parameters.

        Args:
            paginate_parameters (PaginateParameters): The pagination parameters.

        Returns:
            list[ResourceObj]: A list of objects representing the retrieved resources.
        """
        raise NotImplementedError
