from __future__ import annotations

import json
import logging
from functools import cached_property
from typing import ClassVar, cast

from pydantic import BaseModel

from llemon.errors import UnsupportedFeatureError
from llemon.models.file import File
from llemon.models.history import History
from llemon.models.request import Request, Response
from llemon.models.tool import Call, Tool
from llemon.types import NS, FilesArgument, FormattingArgument, ToolsArgument
from llemon.utils.formatting import Formatting
from llemon.utils.logs import ASSISTANT, FILE, TOOL, USER
from llemon.utils.trim import trim

log = logging.getLogger(__name__)


class GenerateRequest(Request):

    no_content: ClassVar[str] = "."
    return_incomplete_messages: ClassVar[bool] = False

    def __init__(
        self,
        *,
        model: LLMModel,
        history: History | None = None,
        instructions: str | None = None,
        user_input: str | None = None,
        context: NS | None = None,
        formatting: FormattingArgument | None = None,
        files: FilesArgument = None,
        tools: ToolsArgument | None = None,
        use_tool: bool | str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        seed: int | None = None,
        frequency_penalty: float | None = None,
        presence_penalty: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        stop: list[str] | None = None,
        prediction: str | NS | BaseModel | None = None,
        return_incomplete_message: bool | None = None,
    ) -> None:
        super().__init__(history=history)
        if instructions is not None:
            instructions = trim(instructions)
        if user_input is not None:
            user_input = trim(user_input)
        if context is None:
            context = {}
        self.model = model
        self.instructions = instructions
        self.user_input = user_input
        self.context = context
        self.formatting = Formatting.resolve(formatting)
        self.files = File.resolve(files)
        self.tools = Tool.resolve(tools)
        self.use_tool = use_tool
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.seed = seed
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.top_p = top_p
        self.top_k = top_k
        self.stop = stop
        self.prediction = self._resolve_prediction(prediction)
        self.return_incomplete_message = return_incomplete_message

    def get_instructions(self, format: bool = True) -> str:
        if not self.instructions:
            return ""
        if format and self.formatting:
            return self.formatting.format(self.instructions, self.context)
        return self.instructions

    def get_user_input(self, format: bool = True) -> str:
        if not self.user_input:
            if self.files:
                return ""
            return self.no_content
        if format and self.formatting:
            return self.formatting.format(self.user_input, self.context)
        return self.user_input

    def get_return_incomplete_message(self) -> bool:
        if self.return_incomplete_message is None:
            return self.return_incomplete_messages
        return self.return_incomplete_message

    def append_instruction(self, instruction: str) -> None:
        instruction = trim(instruction)
        if not self.instructions:
            self.instructions = instruction
        else:
            self.instructions += "\n" + instruction

    def check_supported(self) -> None:
        if self.tools and not self.model.config.supports_tools:
            raise UnsupportedFeatureError(f"{self.model} doesn't support tools")
        for file in self.files:
            if not self.model.config.accepts_files:
                raise UnsupportedFeatureError(f"{self.model} doesn't support files")
            if file.mimetype not in self.model.config.accepts_files:
                raise UnsupportedFeatureError(f"{self.model} doesn't support {file.mimetype} files ({file})")

    def format(self) -> str:
        output: list[str] = []
        output.append(f"{USER}{self.get_user_input()}")
        for file in self.files:
            output.append(f"{FILE}{file.name}")
        return "\n".join(output)

    def dump(self) -> NS:
        data = super().dump()
        data.update(
            model=self.model.dump(),
            instructions=self.instructions,
            user_input=self.user_input,
            context=self.context or None,
            formatting=self.formatting.bracket if self.formatting else None,
            files=[file.dump() for file in self.files],
            tools=[tool.dump() for tool in self.tools.values()],
            use_tool=self.use_tool,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            seed=self.seed,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            top_p=self.top_p,
            top_k=self.top_k,
            stop=self.stop,
            prediction=self.prediction,
            return_incomplete_message=self.return_incomplete_message,
        )
        data = {key: value for key, value in data.items() if value is not None}
        return data

    @classmethod
    def _restore(self, data: NS) -> tuple[NS, NS]:
        args, attrs = super()._restore(data)
        tools = [Tool.load(tool) for tool in data.get("tools", [])]
        args.update(
            model=LLMModel.load(data["model"]),
            instructions=data.get("instructions"),
            user_input=data.get("user_input"),
            context=data.get("context"),
            formatting=Formatting.resolve(data.get("formatting")),
            files=[File.load(file) for file in data.get("files", [])],
            tools={tool.name: tool for tool in tools},
            use_tool=data.get("use_tool"),
            temperature=data.get("temperature"),
            max_tokens=data.get("max_tokens"),
            seed=data.get("seed"),
            frequency_penalty=data.get("frequency_penalty"),
            presence_penalty=data.get("presence_penalty"),
            top_p=data.get("top_p"),
            top_k=data.get("top_k"),
            stop=data.get("stop"),
            prediction=data.get("prediction"),
            return_incomplete_message=data.get("return_incomplete_message"),
        )
        return args, attrs

    def _resolve_prediction(self, prediction: str | NS | BaseModel | None) -> str | None:
        if prediction is None:
            return None
        if isinstance(prediction, BaseModel):
            return prediction.model_dump_json()
        try:
            return json.dumps(prediction)
        except TypeError:
            return str(prediction)


class GenerateResponse(Response):

    request: GenerateRequest

    def __init__(self, request: GenerateRequest) -> None:
        super().__init__(request)
        self.calls: list[Call] = []
        self._text: str | None = None

    @cached_property
    def text(self) -> str:
        if not self.ended:
            raise self._incomplete_request()
        return cast(str, self._text)

    def dump(self) -> NS:
        data = super().dump()
        data.update(
            calls=[call.dump() for call in self.calls],
            text=self.text,
        )
        return data

    def complete_text(self, text: str) -> None:
        self._text = text.strip()
        super().complete()

    def format(self) -> str:
        output: list[str] = []
        for call in self.calls:
            result = call.result["error"] if "error" in call.result else call.result["return_value"]
            output.append(f"{TOOL}{call.signature} -> {result}")
        output.append(f"{ASSISTANT}{self.text}")
        return "\n".join(output)

    @classmethod
    def _restore(self, data: NS) -> tuple[NS, NS]:
        args, attrs = super()._restore(data)
        attrs.update(
            calls=[Call.load(call) for call in data["calls"]],
            _text=data["text"],
        )
        return args, attrs


from llemon.apis.llm.llm_model import LLMModel
