import inspect
from typing import (
    Type,
    TypeVar,
    Any,
    Dict,
    Union,
    get_type_hints,
    get_origin,
    get_args,
)
from dataclasses import dataclass, fields
from ._filters import Filter
from ..types._callback import Callback

T = TypeVar("T", bound="CallbackData")


class CallbackData:
    _prefix: str
    _sep: str = ":"

    def __init_subclass__(cls, prefix: str, sep: str = ":", **kwargs):
        cls._prefix = prefix
        cls._sep = sep
        super().__init_subclass__(**kwargs)

    def pack(self) -> str:
        parts = [self._prefix]
        for field in fields(self):
            value = getattr(self, field.name)
            parts.append(str(value) if value is not None else "")
        return self._sep.join(parts)

    @classmethod
    def unpack(cls: Type[T], data: str) -> T:
        if not data.startswith(f"{cls._prefix}{cls._sep}"):
            raise ValueError("Invalid callback_data format")

        parts = data.split(cls._sep)
        field_types = get_type_hints(cls)
        field_list = list(fields(cls))

        kwargs = {}
        for i, field in enumerate(field_list, start=1):
            if i >= len(parts):
                value = None
            else:
                value = parts[i] if parts[i] != "" else None

            if value is not None:
                field_type = field_types[field.name]
                kwargs[field.name] = cls._convert_value(value, field_type)
            elif field.default is inspect.Parameter.empty:
                raise ValueError(f"Missing required field: {field.name}")

        return cls(**kwargs)

    @staticmethod
    def _convert_value(value: str, target_type: Any) -> Any:
        if get_origin(target_type) is Union:
            possible_types = get_args(target_type)
            for t in possible_types:
                try:
                    return CallbackData._convert_single_value(value, t)
                except (ValueError, TypeError):
                    continue
            raise ValueError(f"Could not convert {value} to any of {possible_types}")
        return CallbackData._convert_single_value(value, target_type)

    @staticmethod
    def _convert_single_value(value: str, target_type: Any) -> Any:
        if target_type is str:
            return value
        elif target_type is int:
            return int(value)
        elif target_type is float:
            return float(value)
        elif target_type is bool:
            return value.lower() == "true"
        else:
            raise ValueError(f"Unsupported type: {target_type}")

    @classmethod
    def filter(cls: Type[T], **conditions: Any) -> "CallbackDataFilter[T]":
        return CallbackDataFilter(cls, **conditions)

    @classmethod
    def has(cls, **fields: bool) -> "CallbackDataFilter[T]":
        conditions = {}
        for field_name, should_exist in fields.items():
            conditions[field_name] = (
                (lambda val: val is not None)
                if should_exist
                else (lambda val: val is None)
            )
        return cls.filter(**conditions)


@dataclass
class CallbackDataFilter(Filter):
    callback_data_class: Type[CallbackData]
    conditions: Dict[str, Any]

    def __init__(self, callback_data_class: Type[CallbackData], **conditions):
        self.callback_data_class = callback_data_class
        self.conditions = conditions
        super().__init__(self._filter_func)

    def _filter_func(self, callback: Callback) -> Union[bool, Any]:
        if not isinstance(callback, Callback) or not callback.data:
            return False

        try:
            data = self.callback_data_class.unpack(callback.data)
        except ValueError:
            return False

        for field_name, expected_value in self.conditions.items():
            if not hasattr(data, field_name):
                return False

            actual_value = getattr(data, field_name)

            if callable(expected_value):
                if not expected_value(actual_value):
                    return False
            elif actual_value != expected_value:
                return False

        return data
