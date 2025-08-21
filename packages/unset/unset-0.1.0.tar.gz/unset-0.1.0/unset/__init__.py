from typing import Final, Any, TypeVar

from pydantic_core import core_schema

T = TypeVar('T')


class UnsetType:
    _instance = None
    __slots__ = ()

    def __new__(cls):
        if getattr(cls, "_instance") is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return 'Unset'

    def __copy__(self: T) -> T:
        return self

    def __reduce__(self) -> str:
        return 'Unset'

    def __deepcopy__(self: T, _: Any) -> T:
        return self

    def __bool__(self):
        return False

    def __call__(self, value: Any) -> bool:
        return value is self

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.is_instance_schema(UnsetType)


Unset: Final = UnsetType()
