from dataclasses import fields, is_dataclass, MISSING
from typing import (
    Optional,
    TYPE_CHECKING,
    Any,
    Type,
    TypeVar,
    get_origin,
    get_args,
    Dict,
    Union,
    ForwardRef,
    Callable,
    Tuple,
    List,
)
import sys

if TYPE_CHECKING:
    from ..client import Bot

T = TypeVar("T", bound="BotModel")


class BotModel:
    """Base model that supports bot injection for Telegram types."""

    bot: Optional["Bot"] = None
    _parsers_cache: Dict[Type, List[Tuple[str, str, Callable[[Any], Any]]]] = {}

    def __post_init__(self):
        self._inject_bot_to_children()

    def _inject_bot_to_children(self) -> "BotModel":
        """Recursively inject bot instance to all child BotModel instances."""
        if self.bot is None:
            return self
        if not is_dataclass(self):
            return self
        for f in fields(self):
            if f.name == "bot":
                continue
            value = getattr(self, f.name, None)
            if value is None:
                continue
            self._inject_bot_recursive(value)
        return self

    def _inject_bot_recursive(self, value: Any):
        if isinstance(value, BotModel):
            if value.bot is None:
                value.bot = self.bot
                value._inject_bot_to_children()
        elif isinstance(value, list):
            for item in value:
                self._inject_bot_recursive(item)

    def set_bot(self, bot: "Bot") -> "BotModel":
        """Manually set bot instance and propagate to children."""
        self.bot = bot
        self._inject_bot_to_children()
        return self

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        if not isinstance(data, dict):
            return data

        parsers = cls._get_field_parsers()
        init_kwargs = {}

        for key, name, parser in parsers:
            if key in data:
                value = data[key]
                if value is not None:
                    init_kwargs[name] = parser(value)
                else:
                    init_kwargs[name] = None

        return cls(**init_kwargs)

    @classmethod
    def _get_field_parsers(cls) -> List[Tuple[str, str, Callable[[Any], Any]]]:
        if cls in cls._parsers_cache:
            return cls._parsers_cache[cls]

        parsers = []
        aliases = getattr(cls, "_aliases", {})

        for f in fields(cls):
            if f.name == "bot":
                continue
            key = aliases.get(f.name, f.name)
            parser = cls._make_parser(f.type)
            parsers.append((key, f.name, parser))

        cls._parsers_cache[cls] = parsers
        return parsers

    @classmethod
    def _make_parser(cls, type_hint: Any) -> Callable[[Any], Any]:
        type_hint = cls._resolve_type(type_hint)

        if type_hint is None:
            return lambda v: v

        origin = get_origin(type_hint)
        args = get_args(type_hint)

        if origin is list:
            item_parser = cls._make_parser(args[0])
            return lambda v: [item_parser(i) for i in v] if v is not None else None

        if origin is Union:
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1:
                return cls._make_parser(non_none_args[0])
            classes = [arg for arg in non_none_args if is_dataclass(arg) and issubclass(arg, BotModel)]
            type_map = {}
            for cls_ in classes:
                for f in fields(cls_):
                    if f.name == "type" and f.default is not MISSING:
                        type_map[f.default] = cls_
                        break

            if type_map:

                def union_parser_discriminator(value):
                    if isinstance(value, dict):
                        t = value.get("type")
                        if t in type_map:
                            return type_map[t].from_dict(value)
                    return value

                return union_parser_discriminator
            return lambda v: v

        if is_dataclass(type_hint) and issubclass(type_hint, BotModel):
            return type_hint.from_dict

        return lambda v: v

    @classmethod
    def _resolve_type(cls, type_hint: Any) -> Any:
        if isinstance(type_hint, ForwardRef):
            type_hint = type_hint.__forward_arg__

        if isinstance(type_hint, str):
            module = sys.modules.get(cls.__module__)
            if module and hasattr(module, type_hint):
                return getattr(module, type_hint)

            if type_hint == cls.__name__:
                return cls

            for sub in BotModel.__subclasses__():
                if sub.__name__ == type_hint:
                    return sub

        return type_hint

    @classmethod
    def _parse_value(cls, value: Any, type_hint: Any) -> Any:
        parser = cls._make_parser(type_hint)
        return parser(value)

    def model_dump(self, exclude_none=False) -> Dict[str, Any]:
        """Simulate pydantic's model_dump"""
        result = {}
        aliases = getattr(self, "_aliases", {})
        for f in fields(self):
            if f.name == "bot":
                continue
            value = getattr(self, f.name)
            if exclude_none and value is None:
                continue
            key = aliases.get(f.name, f.name)
            if isinstance(value, BotModel):
                result[key] = value.model_dump(exclude_none=exclude_none)
            elif isinstance(value, list):
                result[key] = [
                    item.model_dump(exclude_none=exclude_none) if isinstance(item, BotModel) else item for item in value
                ]
            else:
                result[key] = value
        return result

    def dict(self, exclude_none=False) -> Dict[str, Any]:
        """Alias for model_dump for backward compatibility."""
        return self.model_dump(exclude_none=exclude_none)
