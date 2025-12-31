from dataclasses import dataclass, fields
from typing import Type, TypeVar, Any, Union, get_origin, get_args, ClassVar
from ..filters import Filter
from ..types._callback_query import CallbackQuery

T = TypeVar("T", bound="CallbackData")


@dataclass
class CallbackData:
    _prefix: ClassVar[str] = ""
    _sep: ClassVar[str] = ":"

    def __init_subclass__(cls, prefix: str, sep: str = ":", **kwargs):
        cls._prefix = prefix
        cls._sep = sep
        super().__init_subclass__(**kwargs)

    def pack(self) -> str:
        parts = [self._prefix]
        for f in fields(self):
            value = getattr(self, f.name)
            parts.append(str(value) if value is not None else "")
        return self._sep.join(parts)

    @classmethod
    def unpack(cls: Type[T], data: str) -> T:
        if not data.startswith(f"{cls._prefix}{cls._sep}"):
            raise ValueError("Invalid callback_data format")

        parts = data.split(cls._sep)
        cls_fields = fields(cls)

        if len(parts) - 1 > len(cls_fields):
            raise ValueError("Too many fields in callback data")

        kwargs = {}
        for i, f in enumerate(cls_fields, start=1):
            if i >= len(parts):
                value = None
            else:
                value = parts[i] if parts[i] != "" else None

            if value is not None:
                # Type conversion
                target_type = f.type
                # Handle Optional
                origin = get_origin(target_type)
                args = get_args(target_type)
                if origin is Union:
                    non_none_args = [arg for arg in args if arg is not type(None)]
                    if len(non_none_args) == 1:
                        target_type = non_none_args[0]

                try:
                    if target_type is int:
                        value = int(value)
                    elif target_type is float:
                        value = float(value)
                    elif target_type is bool:
                        value = str(value).lower() in ("true", "1", "yes")
                except ValueError as e:
                    raise ValueError(f"Invalid value for field {f.name}: {value}") from e

                kwargs[f.name] = value

        return cls(**kwargs)

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

        for field_name, expected in self.conditions.items():
            actual = getattr(data, field_name)

            if expected is ...:
                if actual is None:
                    return False
            elif expected is None:
                if actual is not None:
                    return False
            elif isinstance(expected, list):
                if actual not in expected:
                    return False
            elif actual != expected:
                return False

        return data
