from typing import List, Union, Optional, Tuple, Dict, Any
from ..types._inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton


class InlineKeyboardBuilder:
    def __init__(self):
        self._keyboard: List[List[InlineKeyboardButton]] = []

    def add(
        self,
        text: str,
        callback_data: Optional[str] = None,
        url: Optional[str] = None,
        web_app: Optional[str] = None,
        copy_text: Optional[str] = None,
        switch_inline_query: Optional[str] = None,
    ) -> "InlineKeyboardBuilder":
        if not any([callback_data, url, web_app, copy_text, switch_inline_query]):
            raise ValueError("At least one button action must be specified")

        button = InlineKeyboardButton(
            text=text,
            callback_data=callback_data,
            web_app=web_app,
            url=url,
            copy_text=copy_text,
            switch_inline_query=switch_inline_query,
        )

        if not self._keyboard:
            self._keyboard.append([])
        self._keyboard[-1].append(button)
        return self

    def row(
        self, *buttons: InlineKeyboardButton, size: Union[int, Tuple[int, ...]] = None
    ) -> "InlineKeyboardBuilder":
        if not buttons:
            return self

        if size is None:
            self._keyboard.append(list(buttons))
        elif isinstance(size, int):
            for i in range(0, len(buttons), size):
                self._keyboard.append(list(buttons[i : i + size]))
        else:
            buttons = list(buttons)
            for s in size:
                if s > 0 and buttons:
                    self._keyboard.append(buttons[:s])
                    buttons = buttons[s:]
            if buttons:
                self._keyboard.append(buttons)
        return self

    def adjust(self, *sizes: Union[int, Tuple[int, ...]]) -> "InlineKeyboardBuilder":
        buttons = [btn for row in self._keyboard for btn in row]
        self._keyboard = []

        if not sizes:
            if buttons:
                self._keyboard = [buttons]
            return self

        for size in sizes:
            if isinstance(size, int):
                if size > 0 and buttons:
                    self._keyboard.append(buttons[:size])
                    buttons = buttons[size:]
            else:
                for s in size:
                    if s > 0 and buttons:
                        self._keyboard.append(buttons[:s])
                        buttons = buttons[s:]

        if buttons:
            self._keyboard.append(buttons)
        return self

    def as_markup(self) -> InlineKeyboardMarkup:
        clean_keyboard = [row for row in self._keyboard if row]
        return InlineKeyboardMarkup(inline_keyboard=clean_keyboard)

    def export(self) -> List[List[Dict[str, Any]]]:
        return [
            [
                {
                    "text": btn.text,
                    "callback_data": btn.callback_data,
                    "url": btn.url,
                    "web_app": {"url": btn.web_app} if btn.web_app else None,
                    "switch_inline_query": btn.switch_inline_query,
                }
                for btn in row
                if any(
                    [btn.callback_data, btn.url, btn.web_app, btn.switch_inline_query]
                )
            ]
            for row in self._keyboard
            if row
        ]

    def __len__(self) -> int:
        return sum(len(row) for row in self._keyboard)

    @property
    def keyboard(self) -> List[List[InlineKeyboardButton]]:
        return [row for row in self._keyboard if row]
