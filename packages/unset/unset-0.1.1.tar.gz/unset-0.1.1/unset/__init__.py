import os
from typing import Final, Any, TypeVar

from pydantic_core import core_schema

UNSET_JSON_SERIALIZE_AS_NONE: bool = os.getenv("UNSET_JSON_SERIALIZE_AS_NONE", "1").lower() in ("1", "true")

T = TypeVar('T')


class UnsetType:
    _instance = None
    __slots__ = ()

    def __new__(cls):
        if getattr(cls, "_instance") is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __str__(self) -> str:
        return '<Unset>'

    def __repr__(self) -> str:
        return str(self)

    def __reduce__(self) -> str:
        return 'Unset'

    def __copy__(self: T) -> T:
        return self

    def __deepcopy__(self: T, _: Any) -> T:
        return self

    def __bool__(self):
        return False

    def __call__(self, value: Any) -> bool:
        return value is self

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.is_instance_schema(
            UnsetType,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda v: None if UNSET_JSON_SERIALIZE_AS_NONE else str(v),
                when_used='json',
            ),
        )


Unset: Final = UnsetType()
