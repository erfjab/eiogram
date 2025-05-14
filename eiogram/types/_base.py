from dataclasses import fields, MISSING
from typing import Any, Dict, Type, TypeVar, get_origin, get_args, Union

T = TypeVar("T", bound="Validated")


class Validated:
    def __post_init__(self):
        for f in fields(self):
            value = getattr(self, f.name)
            if value is None and f.default is not MISSING:
                continue
            expected_type = f.type
            try:
                self._validate_type(value, expected_type)
            except Exception as e:
                raise TypeError(
                    f"Invalid type for field '{f.name}': expected {expected_type}, got {type(value)}"
                ) from e

    @staticmethod
    def _validate_type(value: Any, expected_type: Any) -> None:
        if expected_type is Any:
            return

        origin = get_origin(expected_type)
        if origin is Union:
            for arg in get_args(expected_type):
                try:
                    if arg == "bot":
                        return
                    Validated._validate_type(value, arg)
                    return
                except TypeError:
                    continue
            raise TypeError(f"{value} does not match any of {get_args(expected_type)}")

        if origin is not None:
            # e.g. Optional[int] → origin = Union
            return

        if not isinstance(value, expected_type):
            raise TypeError()

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Convert API response to object with proper bot handling"""
        processed_data = data.copy()  # Use a copy to avoid modifying original data

        # Handle special field renaming
        if "callback_query" in processed_data and hasattr(cls, "callback"):
            processed_data["callback"] = processed_data["callback_query"]

        # Handle special field renaming
        if "from" in processed_data and hasattr(cls, "from_user"):
            processed_data["from_user"] = processed_data["from"]

        # Get all field names from the class
        field_names = {f.name for f in fields(cls)}

        # Filter out fields that don't exist in the class
        filtered_data = {k: v for k, v in processed_data.items() if k in field_names}

        # Convert nested objects
        for field in fields(cls):
            if field.name in filtered_data:
                value = filtered_data[field.name]
                if value is not None:
                    filtered_data[field.name] = cls._convert_value(field.type, value)

        # Check required fields
        required_fields = [
            f.name
            for f in fields(cls)
            if f.default is MISSING and f.default_factory is MISSING
        ]
        missing = [f for f in required_fields if f not in filtered_data]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        return cls(**filtered_data)

    @classmethod
    def _convert_value(cls, field_type, value):
        """Convert nested objects"""
        if hasattr(field_type, "from_dict"):
            return field_type.from_dict(value)

        origin = get_origin(field_type)
        if origin is Union:
            args = [a for a in get_args(field_type) if a is not type(None)]
            if args and hasattr(args[0], "from_dict"):
                return args[0].from_dict(value)

        return value
