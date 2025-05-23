from typing import Type, TypeVar, Any, Union, get_origin, get_args, ClassVar
from pydantic import BaseModel, ValidationError, field_validator, ConfigDict
from ..filters import Filter
from ..types._callback_query import CallbackQuery

T = TypeVar("T", bound="CallbackData")


class CallbackData(BaseModel):
    _prefix: ClassVar[str] = ""
    _sep: ClassVar[str] = ":"

    model_config = ConfigDict(
        extra="forbid", validate_assignment=True, ignored_types=(type(ClassVar),)
    )

    def __init_subclass__(cls, prefix: str, sep: str = ":", **kwargs):
        cls._prefix = prefix
        cls._sep = sep
        super().__init_subclass__(**kwargs)

    def pack(self) -> str:
        parts = [self._prefix]
        for field_name, field in self.model_fields.items():
            value = getattr(self, field_name)
            parts.append(str(value) if value is not None else "")
        return self._sep.join(parts)

    @classmethod
    def unpack(cls: Type[T], data: str) -> T:
        if not data.startswith(f"{cls._prefix}{cls._sep}"):
            raise ValueError("Invalid callback_data format")

        parts = data.split(cls._sep)
        field_names = list(cls.model_fields.keys())

        if len(parts) - 1 > len(field_names):
            raise ValueError("Too many fields in callback data")

        kwargs = {}
        for i, field_name in enumerate(field_names, start=1):
            if i >= len(parts):
                value = None
            else:
                value = parts[i] if parts[i] != "" else None

            if value is not None:
                kwargs[field_name] = value

        try:
            return cls(**kwargs)
        except ValidationError as e:
            raise ValueError(f"Invalid callback data: {e}") from e

    @field_validator("*", mode="before")
    @classmethod
    def convert_types(cls, value: Any, info):
        if value is None:
            return None

        field = info.field_name
        field_info = cls.model_fields[field]
        target_type = field_info.annotation

        if get_origin(target_type) is Union:
            possible_types = [t for t in get_args(target_type) if t is not type(None)]
            if not possible_types:
                return None
            target_type = possible_types[0]

        if target_type is str:
            return str(value)
        elif target_type is int:
            return int(value)
        elif target_type is float:
            return float(value)
        elif target_type is bool:
            return str(value).lower() in ("true", "1", "yes")
        return value

    @classmethod
    def filter(cls: Type[T], **conditions: Any) -> "CallbackDataFilter[T]":
        return CallbackDataFilter(cls, **conditions)


class CallbackDataFilter(Filter):
    def __init__(self, callback_data_class: Type[CallbackData], **conditions):
        self.callback_data_class = callback_data_class
        self.conditions = conditions
        super().__init__(self._filter_func)

    def _filter_func(self, callback: CallbackQuery) -> Union[bool, Any]:
        if not isinstance(callback, CallbackQuery) or not callback.data:
            return False

        try:
            data = self.callback_data_class.unpack(callback.data)
        except ValueError:
            return False

        for field_name, expected_value in self.conditions.items():
            if field_name not in self.callback_data_class.model_fields:
                return False

            actual_value = getattr(data, field_name)

            if callable(expected_value):
                if not expected_value(actual_value):
                    return False
            elif actual_value != expected_value:
                return False

        return data
