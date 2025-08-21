# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Conversion of protobuf int enums to Python enums."""

import enum
from typing import Literal, TypeVar, overload

EnumT = TypeVar("EnumT", bound=enum.Enum)
"""A type variable that is bound to an enum."""


@overload
def enum_from_proto(
    value: int, enum_type: type[EnumT], *, allow_invalid: Literal[False]
) -> EnumT: ...


@overload
def enum_from_proto(
    value: int, enum_type: type[EnumT], *, allow_invalid: Literal[True] = True
) -> EnumT | int: ...


def enum_from_proto(
    value: int, enum_type: type[EnumT], *, allow_invalid: bool = True
) -> EnumT | int:
    """Convert a protobuf int enum value to a python enum.

    Example:
        ```python
        import enum

        from proto import proto_pb2  # Just an example. pylint: disable=import-error

        @enum.unique
        class SomeEnum(enum.Enum):
            # These values should match the protobuf enum values.
            UNSPECIFIED = 0
            SOME_VALUE = 1

        enum_value = enum_from_proto(proto_pb2.SomeEnum.SOME_ENUM_SOME_VALUE, SomeEnum)
        # -> SomeEnum.SOME_VALUE

        enum_value = enum_from_proto(42, SomeEnum)
        # -> 42

        enum_value = enum_from_proto(
            proto_pb2.SomeEnum.SOME_ENUM_UNKNOWN_VALUE, SomeEnum, allow_invalid=False
        )
        # -> ValueError
        ```

    Args:
        value: The protobuf int enum value.
        enum_type: The python enum type to convert to.
        allow_invalid: If `True`, return the value as an `int` if the value is not
            a valid member of the enum (this allows for forward-compatibility with new
            enum values defined in the protocol but not added to the Python enum yet).
            If `False`, raise a `ValueError` if the value is not a valid member of the
            enum.

    Returns:
        The resulting python enum value if the protobuf value is known, otherwise
            the input value converted to a plain `int`.

    Raises:
        ValueError: If `allow_invalid` is `False` and the value is not a valid member
            of the enum.
    """
    try:
        return enum_type(value)
    except ValueError:
        if allow_invalid:
            return value
        raise
