from __future__ import annotations

import inspect
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, cast, overload

from pydantic import BaseModel

from llemon.apis.llm.llm_model_config import LLMModelConfig
from llemon.models.history import History
from llemon.types import (
    NS,
    FilesArgument,
    FormattingArgument,
    LLMRequestCallback,
    ToolsArgument,
)
from llemon.utils.schema import schema_to_model

log = logging.getLogger(__name__)


class LLMModel:

    def __init__(self, llm: LLM, name: str, config: LLMModelConfig) -> None:
        self.llm = llm
        self.name = name
        self.config = config
        self.request_callbacks: list[LLMRequestCallback] = []

    def __str__(self) -> str:
        return f"{self.llm} {self.name!r}"

    def __repr__(self) -> str:
        return f"<{self}>"

    @classmethod
    def load(cls, data: NS) -> LLMModel:
        llm_class = LLM.classes[data["provider"]]
        return llm_class.get(data["name"], **(data.get("config") or {}))

    def on_request(self, callback: LLMRequestCallback) -> LLMRequestCallback:
        self.request_callbacks.append(callback)
        return callback

    def conversation(
        self,
        instructions: str | None = None,
        context: NS | None = None,
        tools: ToolsArgument = None,
        history: History | None = None,
        formatting: FormattingArgument = True,
    ) -> Conversation:
        return Conversation(self, instructions, context=context, tools=tools, history=history, formatting=formatting)

    async def generate(
        self,
        message1: str | None = None,
        message2: str | None = None,
        /,
        *,
        history: History | None = None,
        files: FilesArgument = None,
        tools: ToolsArgument = None,
        use_tool: bool | str | None = None,
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
        instructions, user_input = self._resolve_messages(message1, message2)
        request = GenerateRequest(
            model=self,
            user_input=user_input,
            instructions=instructions,
            history=history,
            files=files,
            tools=tools,
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
        async with self._prepare(request):
            return await self.llm.generate(request)

    async def generate_stream(
        self,
        message1: str | None = None,
        message2: str | None = None,
        /,
        *,
        history: History | None = None,
        files: FilesArgument = None,
        tools: ToolsArgument = None,
        use_tool: bool | str | None = None,
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
        instructions, user_input = self._resolve_messages(message1, message2)
        request = GenerateStreamRequest(
            model=self,
            user_input=user_input,
            instructions=instructions,
            history=history,
            files=files,
            tools=tools,
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
        async with self._prepare(request):
            return await self.llm.generate_stream(request)

    @overload
    async def generate_data(
        self,
        schema: NS,
        message1: str | None = None,
        message2: str | None = None,
        /,
        *,
        history: History | None = None,
        files: FilesArgument = None,
        tools: ToolsArgument = None,
        use_tool: bool | str | None = None,
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
        message1: str | None = None,
        message2: str | None = None,
        /,
        *,
        history: History | None = None,
        files: FilesArgument = None,
        tools: ToolsArgument = None,
        use_tool: bool | str | None = None,
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
        message1: str | None = None,
        message2: str | None = None,
        /,
        *,
        history: History | None = None,
        files: FilesArgument = None,
        tools: ToolsArgument = None,
        use_tool: bool | str | None = None,
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
        instructions, user_input = self._resolve_messages(message1, message2)
        request = GenerateDataRequest(
            schema=model_class,
            model=self,
            user_input=user_input,
            instructions=instructions,
            history=history,
            files=files,
            temperature=temperature,
            seed=seed,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            top_p=top_p,
            top_k=top_k,
            tools=tools,
            use_tool=use_tool,
            prediction=prediction,
        )
        async with self._prepare(request):
            return await self.llm.generate_data(request)

    def dump(self) -> NS:
        data: NS = dict(
            provider=self.llm.__class__.__name__,
            name=self.name,
        )
        config = self.config.dump(self.name)
        if config:
            data["config"] = config
        return data

    def _resolve_messages(self, message1: str | None, message2: str | None) -> tuple[str | None, str | None]:
        if message2 is None:
            return None, message1
        return message1, message2

    @asynccontextmanager
    async def _prepare(
        self,
        request: GenerateRequest,
        state: NS | None = None,
        llm_request_callbacks: list[LLMRequestCallback] | None = None,
        teardown: bool = True,
    ) -> AsyncIterator[None]:
        if state is None:
            state = {}
        if llm_request_callbacks is None:
            llm_request_callbacks = []
        for callback in [*self.request_callbacks, *llm_request_callbacks]:
            log.debug("running callback %s", callback.__name__)
            if inspect.iscoroutinefunction(callback):
                await callback(request)
            else:
                callback(request)
        await self.llm.setup(request, state)
        request.check_supported()
        try:
            yield
        finally:
            if teardown:
                await self.llm.teardown(state)


from llemon.apis.llm.llm import LLM
from llemon.conversation import Conversation
from llemon.models.generate import GenerateRequest, GenerateResponse
from llemon.models.generate_data import GenerateDataRequest, GenerateDataResponse
from llemon.models.generate_stream import GenerateStreamRequest, GenerateStreamResponse
