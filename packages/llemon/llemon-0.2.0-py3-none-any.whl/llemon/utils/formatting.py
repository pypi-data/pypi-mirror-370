from __future__ import annotations

from typing import Any, ClassVar

import jinja2

from llemon.types import FormattingArgument
from llemon.utils.concat import concat


class Formatting:

    format_by_default: ClassVar[bool] = True
    brackets: ClassVar[dict[str, str]] = {
        "(": ")",
        "[": "]",
        "{": "}",
        "<": ">",
    }
    default_bracket: ClassVar[str] = "{"
    formattings: ClassVar[dict[str, Formatting]] = {}

    def __init__(self, bracket: str) -> None:
        self.bracket = bracket
        self._end = self.brackets[bracket]
        self._env = jinja2.Environment(
            variable_start_string=self.bracket * 2,
            variable_end_string=self._end * 2,
            block_start_string=f"{self.bracket}%",
            block_end_string=f"%{self._end}",
            comment_start_string=f"{self.bracket}#",
            comment_end_string=f"#{self._end}",
        )

    def __str__(self) -> str:
        return f"formatting {self.bracket}...{self._end}"

    def __repr__(self) -> str:
        return f"<{self}>"

    @classmethod
    def resolve(cls, formatting: FormattingArgument) -> Formatting | None:
        if formatting is None:
            if cls.format_by_default:
                formatting = cls.default_bracket
            else:
                return None
        if formatting is False:
            return None
        if formatting is True:
            formatting = cls.default_bracket
        if isinstance(formatting, str):
            return cls.from_bracket(formatting)
        return formatting

    @classmethod
    def from_bracket(cls, bracket: str) -> Formatting:
        if bracket not in cls.brackets:
            raise ValueError(f"Invalid bracket {bracket!r} (expected {concat(cls.brackets)})")
        if bracket not in cls.formattings:
            cls.formattings[bracket] = cls(bracket)
        return cls.formattings[bracket]

    def format(self, text: str, context_dict: dict[str, Any] | None = None, /, **context_kwargs: Any) -> str:
        context = (context_dict or {}) | context_kwargs
        template = self._env.from_string(text)
        return template.render(context)
