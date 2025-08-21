"""This module provides a high-level interface for interacting with different database clients.

Classes:
    DB: Represents a database client adapter.

Dataclasses:
    DBSpecification: Represents the specification for a database connection.
"""

import pathlib
import typing

import pydantic
import sthali_core

if typing.TYPE_CHECKING:
    from .clients import Base


parent_path = pathlib.Path(__file__).parent
enum_clients_config = sthali_core.enum_clients.Clients(parent_path)
ClientEnum = enum_clients_config.enum


@pydantic.dataclasses.dataclass
class DBSpecification:
    """Represents the specification for a database connection.

    Attributes:
        path (str): Path to the database.
            This field specifies the path to the database file or server.
        client (str): One of available database clients.
            This field specifies the database client to be used for the connection.
            The available options are "Default", "Postgres", "Redis", "SQLite", and "TinyDB".
            Defaults to "Default".
    """

    path: typing.Annotated[str, pydantic.Field(description="Path to the database")]
    client: typing.Annotated[ClientEnum, pydantic.Field(description="One of available database clients")]


class DB:
    """Represents a database client adapter.

    Args:
        db_spec (DBSpecification): The specification for the database connection.
        table (str): The name of the table to interact with.
    """

    def __init__(self, db_spec: DBSpecification, table: str) -> None:
        """Initialize the DB instance.

        Args:
            db_spec (DBSpecification): The specification for the database connection.
            table (str): The name of the table to interact with.
        """
        client_name = str(db_spec.client.value)
        client_module = enum_clients_config.clients_map[client_name]
        client_class: type[Base] = getattr(client_module, f"{client_name.title()}Client")
        client = client_class(db_spec.path, table)

        self.insert_one = client.insert_one
        self.select_one = client.select_one
        self.update_one = client.update_one
        self.delete_one = client.delete_one
        self.select_many = client.select_many
