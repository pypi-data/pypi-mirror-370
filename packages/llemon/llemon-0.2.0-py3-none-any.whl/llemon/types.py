from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from llemon.models.file import File
    from llemon.models.generate import GenerateRequest
    from llemon.models.request import Request, Response
    from llemon.models.tool import Call, Tool
    from llemon.tools.toolbox import Toolbox
    from llemon.utils.formatting import Formatting

type NS = dict[str, Any]
type FilesArgument = list[str | pathlib.Path | tuple[str, bytes] | File] | None
type ToolsArgument = list[Callable[..., Any] | Toolbox] | dict[str, Tool] | None
type CallArgument = NS | Call
type FormattingArgument = bool | str | Formatting | None
type Interaction = tuple[Request, Response]
type LLMRequestCallback = Callable[[GenerateRequest], Any]
type ToolCalls = list[tuple[str, str, NS]]
type ToolStream = dict[int, tuple[str, str, list[str]]]
type ToolDelta = tuple[int, str, str, str]
