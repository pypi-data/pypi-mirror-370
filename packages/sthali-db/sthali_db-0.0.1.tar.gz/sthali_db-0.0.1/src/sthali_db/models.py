"""This module provides classes for creating dynamic models based on field specifications.

Classes:
    Models(name: str, fields: list[FieldSpecification]): Represents a collection of models.

Dataclasses:
    FieldSpecification: Represents a field with its metadata.
"""

import collections.abc
import enum
import typing
import uuid

import pydantic


@pydantic.dataclasses.dataclass
class FieldSpecification:
    """Represents a field with its metadata.

    Attributes:
        name (str): Name of the field.
        type (typing.Any): Type annotation of the field.
        default (Default | None): Default value/factory of the field. Defaults to None.
        description (str | None): Description of the field. Defaults to None.
        optional (bool | None): Indicates if the field accepts None. Defaults to None.
        title (str | None): Title of the field. Defaults to None.
    """

    @pydantic.dataclasses.dataclass
    class Default:
        """Represents a default value for an attribute.

        Attributes:
            factory (collections.abc.Callable[..., typing.Any] | None): The function used to create the default value
                forthe attribute. Defaults to None.
            value (typing.Any | None): The default value for the attribute. Defaults to None.
        """

        factory: typing.Annotated[
            collections.abc.Callable[..., typing.Any] | None,
            pydantic.Field(
                default=None, description="The function used to create the default value for the attribute",
            ),
        ]
        value: typing.Annotated[
            typing.Any | None,
            pydantic.Field(default=None, description="The default value for the attribute"),
        ]

    name: typing.Annotated[str, pydantic.Field(description="Name of the field")]
    type: typing.Annotated[typing.Any, pydantic.Field(description="Type annotation of the field")]
    default: typing.Annotated[
        Default | None,
        pydantic.Field(default=None, description="Default value/factory of the field"),
    ]
    description: typing.Annotated[str | None, pydantic.Field(default=None, description="Description of the field")]
    optional: typing.Annotated[
        bool | None,
        pydantic.Field(default=None, description="Indicates if the field accepts None"),
    ]
    title: typing.Annotated[str | None, pydantic.Field(default=None, description="Title of the field")]

    @property
    def _metadata(self) -> dict[str, typing.Any]:
        result: dict[str, typing.Any] = {
            "description": self.description or f"Field {self.name}",
            "title": self.title or self.name,
        }
        if self.default:
            if self.default.factory:
                result["default_factory"] = self.default.factory
            else:
                result["default"] = self.default.value
        return result

    @property
    def type_annotated(self) -> typing.Annotated[typing.Any, pydantic.Field]:
        """Returns the type annotation of the field.

        Returns:
            typing.Annotated[typing.Any, Field]: The type annotation of the field.
        """
        field_type = (self.type, typing.Union[self.type, None])[bool(self.optional)]
        return typing.Annotated[field_type, pydantic.Field(**self._metadata)]


class Models:
    """Represents a collection of models.

    This class is responsible for creating and managing models dynamically based on the provided fields.
    It provides methods to create different types of models such as create, response, and update models.

    Attributes:
        name (str): The name of the collection of models.
        create_model (type[Base]): The dynamically created model for creating new instances.
        response_model (type[BaseWithId]): The dynamically created model for response payloads.
        update_model (type[Base]): The dynamically created model for updating existing instances.
    """

    class Base(pydantic.BaseModel):
        """Represents a base class for models."""

    class BaseWithId(Base):
        """Represents a base class for models with a resource identifier."""

        id: typing.Annotated[uuid.UUID, pydantic.Field(description="Resource identifier")]

    def __init__(self, name: str, fields: list[FieldSpecification]) -> None:
        """Initialize the Models class.

        Args:
            name (str): The name of the collection of models.
            fields (list[FieldSpecification]): The list of fields specification for the models.
        """
        self.name = name
        self.create_model = self._factory(self.Base, f"Create{name.title()}", fields)
        self.response_model = self._factory(self.BaseWithId, f"Response{name.title()}", fields)
        self.update_model = self._factory(self.Base, f"Update{name.title()}", fields)

    @staticmethod
    def _factory(
        base: type[pydantic.main.ModelT],
        name: str,
        fields: list[FieldSpecification],
    ) -> type[pydantic.main.ModelT]:
        fields_constructor = {field.name: field.type_annotated for field in fields}
        return pydantic.create_model(name, __base__=base, **fields_constructor)


class Types:
    """Types class provides a mechanism to manage a custom enumeration of types.

    Attributes:
        types_enum (TypeEnum): An enumeration of various types and values.

    Methods:
        get(name: str) -> typing.Any:
            Retrieve an attribute from the `types_enum` based on the given name.
        set(name: str, value: typing.Any = None, operation: typing.Literal["add", "del"] = "add") -> None:
            Modifies the `types_enum` attribute by adding or deleting an enumeration member.
    """
    class TypeEnum(enum.Enum):
        """Original TypeEnum enumerate class."""

        any = typing.Any
        none = None
        bool = bool
        true = True
        false = False
        str = str
        int = int
        float = float
        list = list
        dict = dict

    types_enum = TypeEnum

    def get(self, name: str) -> typing.Any:
        """Retrieve an attribute from the `types_enum` based on the given name.

        Args:
            name (str): The name of the attribute to retrieve.

        Returns:
            typing.Any: The value of the attribute with the given name.
        """
        return getattr(self.types_enum, name).value

    def set(self, name: str, value: typing.Any = None) -> None:
        """Modifies the `types_enum` attribute by adding an enumeration member.

        Args:
            name (str): The name of the enumeration member to add
            value (typing.Any, optional): The value of the enumeration member to add. Defaults to None.

        Returns:
            None
        """
        old_types_enum: list[tuple[str, typing.Any]] = [
            (i, getattr(self.types_enum, i)) for i in self.types_enum.__members__
        ]
        new_types_enum = [*old_types_enum, (name, value)]
        self.types_enum = enum.Enum("TypeEnum", new_types_enum)

    def pop(self, name: str) -> None:
        """Modifies the `types_enum` attribute by deleting an enumeration member.

        Args:
            name (str): The name of the enumeration member to delete.

        Returns:
            None
        """
        old_types_enum: list[tuple[str, typing.Any]] = [
            (i, getattr(self.types_enum, i)) for i in self.types_enum.__members__
        ]
        new_types_enum = [i for i in old_types_enum if i[0] != name]
        self.types_enum = enum.Enum("TypeEnum", new_types_enum)
