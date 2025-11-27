from typing import Optional, TYPE_CHECKING, Any
from pydantic import BaseModel, model_validator

if TYPE_CHECKING:
    from ..client import Bot


class BotModel(BaseModel):
    """Base model that supports bot injection for Telegram types."""

    if TYPE_CHECKING:
        bot: Optional["Bot"] = None
    else:
        bot: Optional[Any] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True

    @model_validator(mode="after")
    def _inject_bot_to_children(self) -> "BotModel":
        """Recursively inject bot instance to all child BotModel instances."""
        if self.bot is None:
            return self

        for field_name in self.model_fields:
            if field_name == "bot":
                continue

            value = getattr(self, field_name, None)
            if value is None:
                continue

            if isinstance(value, BotModel):
                if value.bot is None:
                    value.bot = self.bot
                    # Trigger child's validator to propagate further
                    value._inject_bot_to_children()
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, BotModel) and item.bot is None:
                        item.bot = self.bot
                        item._inject_bot_to_children()

        return self

    def set_bot(self, bot: "Bot") -> "BotModel":
        """Manually set bot instance and propagate to children."""
        self.bot = bot
        self._inject_bot_to_children()
        return self
