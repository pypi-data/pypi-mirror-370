"""This module provides {...}.

Classes:
    Models: Types class provides a mechanism to manage a custom enumeration of types.

"""

import enum
import typing


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
