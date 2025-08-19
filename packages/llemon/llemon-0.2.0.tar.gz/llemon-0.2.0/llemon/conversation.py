from __future__ import annotations

import warnings
from types import TracebackType
from typing import TYPE_CHECKING, Iterator, cast, overload

from pydantic import BaseModel

from llemon.models.generate import GenerateRequest, GenerateResponse
from llemon.models.generate_data import GenerateDataRequest, GenerateDataResponse
from llemon.models.generate_stream import GenerateStreamRequest, GenerateStreamResponse
from llemon.models.history import History
from llemon.models.request import Request, Response
from llemon.models.tool import Tool
from llemon.types import (
    NS,
    FilesArgument,
    FormattingArgument,
    LLMRequestCallback,
    ToolsArgument,
)
from llemon.utils.formatting import Formatting
from llemon.utils.schema import schema_to_model

if TYPE_CHECKING:
    from llemon.apis.llm.llm import LLM


class Conversation:

    def __init__(
        self,
        model: LLMModel,
        instructions: str | None = None,
        context: NS | None = None,
        history: History | None = None,
        tools: ToolsArgument = None,
        formatting: FormattingArgument = None,
        llm_request_callbacks: list[LLMRequestCallback] | None = None,
    ) -> None:
        if llm_request_callbacks is None:
            llm_request_callbacks = []
        self.model = model
        self.instructions = instructions
        self.context = context if context is not None else {}
        self.history = history or History()
        self.tools = Tool.resolve(tools)
        self.formatting = Formatting.resolve(formatting)
        self.llm_request_callbacks = llm_request_callbacks
        self._state: NS = {}
        self._finished = False

    def __bool__(self) -> bool:
        return bool(self.history)

    def __len__(self) -> int:
        return len(self.history)

    def __iter__(self) -> Iterator[tuple[Request, Response]]:
        yield from self.history

    @overload
    def __getitem__(self, index: int) -> tuple[Request, Response]: ...

    @overload
    def __getitem__(self, index: slice) -> Conversation: ...

    def __getitem__(self, index: int | slice) -> tuple[Request, Response] | Conversation:
        if isinstance(index, slice):
            return self.replace(history=self.history[index])
        return self.history[index]

    async def __aenter__(self) -> Conversation:
        return self

    async def __aexit__(
        self,
        exception: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.finish()

    def __del__(self) -> None:
        if not self._finished:
            warnings.warn(f"{self} not finished", ResourceWarning)

    @classmethod
    def load(cls, data: NS) -> Conversation:
        conversation = data["conversation"]
        conversation["model"] = data["models"][conversation["model"]]
        data["history"] = conversation.pop("history")
        history = History.load(data)
        tools = [Tool.load(data["tools"][name]) for name in conversation.get("tools", [])]
        return cls(
            model=LLMModel.load(conversation["model"]),
            instructions=conversation.get("instructions"),
            context=conversation.get("context"),
            history=history,
            tools={tool.name: tool for tool in tools},
            formatting=Formatting.resolve(conversation.get("formatting")),
        )

    @property
    def llm(self) -> LLM:
        return self.model.llm

    def replace(
        self,
        model: LLMModel | None = None,
        instructions: str | None = None,
        context: NS | None = None,
        history: History | None = None,
        tools: ToolsArgument = None,
        formatting: FormattingArgument = None,
        llm_request_callbacks: list[LLMRequestCallback] | None = None,
    ) -> Conversation:
        return type(self)(
            model=model or self.model,
            instructions=instructions or self.instructions,
            context=context or self.context,
            history=history or self.history,
            tools=tools or self.tools,
            formatting=formatting or self.formatting,
            llm_request_callbacks=llm_request_callbacks or self.llm_request_callbacks,
        )

    async def finish(self) -> None:
        if self._finished:
            return
        await self.llm.teardown(self._state)
        self._finished = True

    def dump(self) -> NS:
        data = self.history.dump()
        data["models"][self.model.name] = self.model.dump()
        for tool in self.tools.values():
            data["tools"][tool.name] = tool.dump()
        conversation = dict(
            model=self.model.name,
            instructions=self.instructions,
            context=self.context or None,
            history=data.pop("history"),
            tools=list(self.tools),
            formatting=self.formatting.bracket if self.formatting else None,
        )
        data["conversation"] = {key: value for key, value in conversation.items() if value is not None}
        return data

    async def generate(
        self,
        message: str | None = None,
        context: NS | None = None,
        *,
        save: bool = True,
        files: FilesArgument = None,
        tools: ToolsArgument = None,
        use_tool: bool | str | None = None,
        formatting: FormattingArgument = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        seed: int | None = None,
        frequency_penalty: float | None = None,
        presence_penalty: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        stop: list[str] | None = None,
        prediction: str | None = None,
        return_incomplete_message: bool | None = None,
    ) -> GenerateResponse:
        request = GenerateRequest(
            model=self.model,
            instructions=self.instructions,
            user_input=message,
            context=self.context | (context or {}),
            formatting=formatting or self.formatting,
            history=self.history,
            files=files,
            tools=self.tools | Tool.resolve(tools),
            use_tool=use_tool,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            top_p=top_p,
            top_k=top_k,
            stop=stop,
            prediction=prediction,
            return_incomplete_message=return_incomplete_message,
        )
        async with self.model._prepare(request, self._state, self.llm_request_callbacks, teardown=False):
            response = await self.llm.generate(request)
        if save:
            self.history.add(request, response)
        return response

    async def generate_stream(
        self,
        message: str | None = None,
        context: NS | None = None,
        *,
        save: bool = True,
        files: FilesArgument = None,
        tools: ToolsArgument = None,
        use_tool: bool | str | None = None,
        formatting: FormattingArgument = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        seed: int | None = None,
        frequency_penalty: float | None = None,
        presence_penalty: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        stop: list[str] | None = None,
        prediction: str | None = None,
        return_incomplete_message: bool | None = None,
    ) -> GenerateStreamResponse:
        request = GenerateStreamRequest(
            model=self.model,
            instructions=self.instructions,
            user_input=message,
            context=self.context | (context or {}),
            formatting=formatting or self.formatting,
            history=self.history,
            files=files,
            tools=self.tools | Tool.resolve(tools),
            use_tool=use_tool,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            top_p=top_p,
            top_k=top_k,
            stop=stop,
            prediction=prediction,
            return_incomplete_message=return_incomplete_message,
        )
        async with self.model._prepare(request, self._state, self.llm_request_callbacks, teardown=False):
            response = await self.llm.generate_stream(request)
        if save:
            self.history.add(request, response)
        return response

    @overload
    async def generate_data(
        self,
        schema: NS,
        message: str | None = None,
        context: NS | None = None,
        *,
        save: bool = True,
        files: FilesArgument = None,
        tools: ToolsArgument = None,
        use_tool: bool | str | None = None,
        formatting: FormattingArgument = None,
        temperature: float | None = None,
        seed: int | None = None,
        frequency_penalty: float | None = None,
        presence_penalty: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        prediction: NS | None = None,
    ) -> GenerateDataResponse[BaseModel]: ...

    @overload
    async def generate_data[T: BaseModel](
        self,
        schema: type[T],
        message: str | None = None,
        context: NS | None = None,
        *,
        save: bool = True,
        files: FilesArgument = None,
        tools: ToolsArgument = None,
        use_tool: bool | str | None = None,
        formatting: FormattingArgument = None,
        temperature: float | None = None,
        seed: int | None = None,
        frequency_penalty: float | None = None,
        presence_penalty: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        prediction: T | None = None,
    ) -> GenerateDataResponse[T]: ...

    async def generate_data[T: BaseModel](
        self,
        schema: type[T] | NS,
        message: str | None = None,
        context: NS | None = None,
        *,
        save: bool = True,
        files: FilesArgument = None,
        tools: ToolsArgument = None,
        use_tool: bool | str | None = None,
        formatting: FormattingArgument = None,
        temperature: float | None = None,
        seed: int | None = None,
        frequency_penalty: float | None = None,
        presence_penalty: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        prediction: T | NS | None = None,
    ) -> GenerateDataResponse[T]:
        if isinstance(schema, dict):
            model_class = cast(type[T], schema_to_model(schema))
        else:
            model_class = schema
        request = GenerateDataRequest(
            schema=model_class,
            model=self.model,
            instructions=self.instructions,
            user_input=message,
            context=self.context | (context or {}),
            formatting=formatting or self.formatting,
            history=self.history,
            files=files,
            tools=self.tools | Tool.resolve(tools),
            use_tool=use_tool,
            temperature=temperature,
            seed=seed,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            top_p=top_p,
            top_k=top_k,
            prediction=prediction,
        )
        async with self.model._prepare(request, self._state, self.llm_request_callbacks, teardown=False):
            response = await self.llm.generate_data(request)
        if save:
            self.history.add(request, response)
        return response


from llemon.apis.llm.llm_model import LLMModel
