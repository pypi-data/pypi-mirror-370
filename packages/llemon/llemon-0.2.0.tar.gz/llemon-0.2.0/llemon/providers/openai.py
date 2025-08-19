from __future__ import annotations

import json
import logging
from typing import AsyncIterator, Literal, overload

import openai
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionContentPartParam,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCallParam,
    ChatCompletionNamedToolChoiceParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
    ParsedChoice,
)
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_chunk import Choice as StreamChoice
from openai.types.chat.chat_completion_content_part_image_param import (
    ImageURL as ImageURLParam,
)
from openai.types.chat.chat_completion_content_part_param import (
    ChatCompletionContentPartImageParam,
    ChatCompletionContentPartTextParam,
)
from openai.types.chat.chat_completion_content_part_param import (
    File as ChatcompletionContentPartFileParam,
)
from openai.types.chat.chat_completion_content_part_param import FileFile as FileParam
from openai.types.chat.chat_completion_message_tool_call_param import (
    Function as FunctionParam,
)
from openai.types.shared_params import FunctionDefinition, ResponseFormatJSONObject
from pydantic import BaseModel

from llemon.apis.llm.llm import LLM
from llemon.apis.llm.llm_model_property import LLMModelProperty
from llemon.errors import Error
from llemon.models.file import File
from llemon.models.generate import GenerateRequest, GenerateResponse
from llemon.models.generate_data import GenerateDataRequest, GenerateDataResponse
from llemon.models.generate_stream import GenerateStreamRequest, GenerateStreamResponse
from llemon.models.tool import Call
from llemon.types import NS, ToolCalls, ToolDelta, ToolStream
from llemon.utils.logs import ASSISTANT, SYSTEM, USER
from llemon.utils.parallelize import async_parallelize

FILE_IDS = "openai.file_ids"
FILE_HASHES = "openai.file_hashes"

log = logging.getLogger(__name__)


class OpenAI(LLM):

    gpt5 = LLMModelProperty("gpt-5")
    gpt5_mini = LLMModelProperty("gpt-5-mini")
    gpt5_nano = LLMModelProperty("gpt-5-nano")
    gpt41 = LLMModelProperty("gpt-4.1")
    gpt41_mini = LLMModelProperty("gpt-4.1-mini")
    gpt41_nano = LLMModelProperty("gpt-4.1-nano")
    gpt4o = LLMModelProperty("gpt-4o")
    gpt4o_mini = LLMModelProperty("gpt-4o-mini")
    gpt4 = LLMModelProperty("gpt-4")
    gpt4_turbo = LLMModelProperty("gpt-4-turbo")
    gpt35_turbo = LLMModelProperty("gpt-3.5-turbo")

    def __init__(self, api_key: str) -> None:
        self.client = openai.AsyncOpenAI(api_key=api_key)

    async def setup(self, request: GenerateRequest, state: NS) -> None:
        await super().setup(request, state)
        if request.files:
            log.debug("uploading files")
        for file in request.files:
            await self._upload_file(file, state)

    async def teardown(self, state: NS) -> None:
        await async_parallelize([(self._delete_file, (file_id,), {}) for file_id in state.pop(FILE_IDS, set())])
        state.pop(FILE_HASHES, None)
        await super().teardown(state)

    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        response = GenerateResponse(request)
        messages = await self._messages(request)
        return await self._generate(request, response, messages)

    async def generate_stream(self, request: GenerateStreamRequest) -> GenerateStreamResponse:
        response = GenerateStreamResponse(request)
        messages = await self._messages(request)
        return await self._generate_stream(request, response, messages)

    async def generate_data[T: BaseModel](self, request: GenerateDataRequest[T]) -> GenerateDataResponse[T]:
        response = GenerateDataResponse(request)
        messages = await self._messages(request)
        if not request.model.config.supports_structured_output:
            return await self._generate_json(request, response, messages)
        return await self._generate_data(request, response, messages)

    async def _upload_file(self, file: File, state: NS) -> None:
        if not file.data and file.is_image:
            log.debug("%s is an image URL; skipping", file)
            return
        await file.fetch()
        assert file.data is not None
        hash: File | None = state.get(FILE_HASHES, {}).get(file.md5)
        if hash:
            log.debug("%s is already uploaded as %s; reusing", file, hash.id)
            file.id = hash.id
            return
        file_object = await self.client.files.create(
            file=(file.name, file.data, file.mimetype),
            purpose="assistants",
        )
        log.debug("uploaded %s as %s", file.name, file_object.id)
        file.id = file_object.id
        state.setdefault(FILE_IDS, set()).add(file_object.id)
        state.setdefault(FILE_HASHES, {})[file.md5] = file

    async def _delete_file(self, file_id: str) -> None:
        log.debug("deleting %s", file_id)
        await self.client.files.delete(file_id)

    async def _messages(self, request: GenerateRequest) -> list[ChatCompletionMessageParam]:
        messages: list[ChatCompletionMessageParam] = []
        if request.instructions:
            instructions = request.get_instructions()
            log.debug(SYSTEM + "%s", instructions)
            messages.append(self._system(instructions))
        if request.history:
            request.history._log()
            for request_, response_ in request.history.interactions:
                if not isinstance(request_, GenerateRequest) or not isinstance(response_, GenerateResponse):
                    continue
                messages.append(await self._user(request_.get_user_input(), request_.files))
                if response_.calls:
                    messages.append(self._tool_call(response_.calls))
                    messages.extend(self._tool_results(response_.calls))
                messages.append(self._assistant(response_.text))
        user_input = request.get_user_input()
        log.debug(USER + "%s", user_input)
        messages.append(await self._user(user_input, request.files))
        return messages

    def _system(self, prompt: str) -> ChatCompletionSystemMessageParam:
        return ChatCompletionSystemMessageParam(role="system", content=prompt)

    async def _user(self, text: str, files: list[File]) -> ChatCompletionUserMessageParam:
        content: str | list[ChatCompletionContentPartParam]
        if files:
            content = []
            if text:
                content.append(
                    ChatCompletionContentPartTextParam(
                        type="text",
                        text=text,
                    )
                )
            for file in files:
                if file.is_image:
                    content.append(
                        ChatCompletionContentPartImageParam(
                            type="image_url",
                            image_url=ImageURLParam(url=file.url),
                        )
                    )
                else:
                    assert file.id is not None
                    content.append(
                        ChatcompletionContentPartFileParam(
                            type="file",
                            file=FileParam(file_id=file.id),
                        )
                    )
        else:
            content = text
        return ChatCompletionUserMessageParam(role="user", content=content)

    def _assistant(self, content: str) -> ChatCompletionAssistantMessageParam:
        return ChatCompletionAssistantMessageParam(role="assistant", content=content)

    def _tool_call(self, calls: list[Call]) -> ChatCompletionAssistantMessageParam:
        return ChatCompletionAssistantMessageParam(
            role="assistant",
            tool_calls=[
                ChatCompletionMessageToolCallParam(
                    type="function",
                    id=call.id,
                    function=FunctionParam(name=call.tool.name, arguments=call.arguments_json),
                )
                for call in calls
            ],
        )

    def _tool_results(self, calls: list[Call]) -> list[ChatCompletionToolMessageParam]:
        return [
            ChatCompletionToolMessageParam(
                role="tool",
                tool_call_id=call.id,
                content=call.result_json,
            )
            for call in calls
        ]

    async def _generate(
        self,
        request: GenerateRequest,
        response: GenerateResponse,
        messages: list[ChatCompletionMessageParam],
        json: bool = False,
    ) -> GenerateResponse:
        try:
            response_format = ResponseFormatJSONObject(type="json_object") if json else openai.NOT_GIVEN
            openai_response = await self.client.chat.completions.create(
                model=request.model.name,
                messages=messages,
                tools=self._tools(request),
                tool_choice=self._tool_choice(request),
                temperature=_optional(request.temperature),
                max_tokens=_optional(request.max_tokens),
                seed=_optional(request.seed),
                frequency_penalty=_optional(request.frequency_penalty),
                presence_penalty=_optional(request.presence_penalty),
                top_p=_optional(request.top_p),
                stop=_optional(request.stop),
                response_format=response_format,
            )
        except openai.APIError as error:
            raise Error(error)
        result = self._parse_choices("text", openai_response.choices, request.get_return_incomplete_message())
        if isinstance(result, list):
            await self._run_tools(request, response, messages, result)
            return await self._generate(request, response, messages, json=json)
        log.debug(ASSISTANT + "%s", result)
        response.complete_text(result)
        return response

    async def _generate_stream(
        self,
        request: GenerateStreamRequest,
        response: GenerateStreamResponse,
        messages: list[ChatCompletionMessageParam],
    ) -> GenerateStreamResponse:
        try:
            openai_response = await self.client.chat.completions.create(
                model=request.model.name,
                messages=messages,
                tools=self._tools(request),
                tool_choice=self._tool_choice(request),
                temperature=_optional(request.temperature),
                max_tokens=_optional(request.max_tokens),
                seed=_optional(request.seed),
                frequency_penalty=_optional(request.frequency_penalty),
                presence_penalty=_optional(request.presence_penalty),
                top_p=_optional(request.top_p),
                stop=_optional(request.stop),
                stream=True,
            )
        except openai.APIError as error:
            raise Error(error)

        async def stream() -> AsyncIterator[str]:
            tool_stream: ToolStream = {}
            async for chunk in openai_response:
                result = self._parse_choices("stream", chunk.choices, request.get_return_incomplete_message())
                if isinstance(result, tuple):
                    index, id, name, arguments = result
                    if index not in tool_stream:
                        tool_stream[index] = (id, name, [])
                    else:
                        tool_stream[index][2].append(arguments)
                elif result:
                    yield result
            if tool_stream:
                tools = [(id, name, json.loads("".join(args))) for (id, name, args) in tool_stream.values()]
                await self._run_tools(request, response, messages, tools)
                await self._generate_stream(request, response, messages)
                assert response.stream is not None
                async for delta in response.stream:
                    yield delta
            else:
                log.debug(ASSISTANT + "%s", response.text)

        response.stream = stream()
        return response

    async def _generate_data[T: BaseModel](
        self,
        request: GenerateDataRequest[T],
        response: GenerateDataResponse[T],
        messages: list[ChatCompletionMessageParam],
    ) -> GenerateDataResponse[T]:
        try:
            openai_response = await self.client.beta.chat.completions.parse(
                model=request.model.name,
                messages=messages,
                tools=self._tools(request),
                tool_choice=self._tool_choice(request),
                temperature=_optional(request.temperature),
                max_tokens=_optional(request.max_tokens),
                seed=_optional(request.seed),
                frequency_penalty=_optional(request.frequency_penalty),
                presence_penalty=_optional(request.presence_penalty),
                top_p=_optional(request.top_p),
                stop=_optional(request.stop),
                response_format=request.schema,
            )
        except openai.APIError as error:
            raise Error(error)
        result = self._parse_choices("data", openai_response.choices, return_incomplete_message=False)
        if isinstance(result, list):
            await self._run_tools(request, response, messages, result)
            return await self._generate_data(request, response, messages)
        log.debug(ASSISTANT + "%s", result)
        response.complete_data(result)
        return response

    async def _generate_json[T: BaseModel](
        self,
        request: GenerateDataRequest[T],
        response: GenerateDataResponse[T],
        messages: list[ChatCompletionMessageParam],
    ) -> GenerateDataResponse[T]:
        log.debug("%s doesn't support structured output; using JSON instead", request.model)
        request.append_json_instruction()
        messages = await self._messages(request)
        generate_response = GenerateResponse(request)
        await self._generate(request, generate_response, messages, json=True)
        data = request.schema.model_validate_json(generate_response.text)
        response.complete_data(data)
        response.calls = generate_response.calls
        return response

    def _tools(self, request: GenerateRequest) -> list[ChatCompletionToolParam] | openai.NotGiven:
        if not request.tools:
            return openai.NOT_GIVEN
        tools: list[ChatCompletionToolParam] = []
        for tool in request.tools.values():
            tools.append(
                ChatCompletionToolParam(
                    type="function",
                    function=FunctionDefinition(
                        name=tool.name,
                        description=tool.description,
                        parameters=tool.parameters,
                        strict=True,
                    ),
                )
            )
        return tools

    def _tool_choice(
        self,
        request: GenerateRequest,
    ) -> openai.NotGiven | Literal["none"] | Literal["required"] | ChatCompletionNamedToolChoiceParam:
        if request.use_tool is None:
            return openai.NOT_GIVEN
        if request.use_tool is False:
            return "none"
        if request.use_tool is True:
            return "required"
        return ChatCompletionNamedToolChoiceParam(
            type="function",
            function={"name": request.use_tool},
        )

    @overload
    def _parse_choices(
        self,
        kind: Literal["text"],
        choices: list[Choice],
        return_incomplete_message: bool,
    ) -> str | ToolCalls: ...

    @overload
    def _parse_choices[T: BaseModel](
        self,
        kind: Literal["data"],
        choices: list[ParsedChoice[T]],
        return_incomplete_message: bool,
    ) -> T | ToolCalls: ...

    @overload
    def _parse_choices(
        self,
        kind: Literal["stream"],
        choices: list[StreamChoice],
        return_incomplete_message: bool,
    ) -> str | ToolDelta: ...

    def _parse_choices[T: BaseModel](
        self,
        kind: Literal["text", "data", "stream"],
        choices: list[Choice] | list[ParsedChoice[T]] | list[StreamChoice],
        return_incomplete_message: bool,
    ) -> str | T | ToolCalls | ToolDelta:
        if not choices:
            raise Error(f"no response from {self}")
        choice = choices[0]
        match choice.finish_reason:
            case "stop":
                if isinstance(choice, Choice):
                    refusal = choice.message.refusal
                else:
                    refusal = choice.delta.refusal
                if refusal:
                    raise Error(f"response from {self} was blocked: {refusal}")
            case "length":
                if not return_incomplete_message:
                    raise Error(f"response from {self} exceeded the maximum length")
            case "tool_calls" | "function_call":
                pass
            case "content_filter":
                raise Error(f"response from {self} was blocked")
        if isinstance(choice, Choice):
            if choice.message.tool_calls:
                tool_calls: ToolCalls = []
                for tool in choice.message.tool_calls:
                    tool_calls.append((tool.id, tool.function.name, json.loads(tool.function.arguments)))
                return tool_calls
            if isinstance(choice, ParsedChoice):
                if not choice.message.parsed:
                    raise Error(f"no data in response from {self}")
                return choice.message.parsed
            if not choice.message.content:
                raise Error(f"no content in response from {self}")
            return choice.message.content
        if choice.delta.tool_calls:
            for tool_call in choice.delta.tool_calls:
                if not tool_call.function:
                    continue
                return (
                    tool_call.index,
                    tool_call.id or "",
                    tool_call.function.name or "",
                    tool_call.function.arguments or "",
                )
        return choice.delta.content or ""

    async def _run_tools(
        self,
        request: GenerateRequest,
        response: GenerateResponse,
        messages: list[ChatCompletionMessageParam],
        tools: ToolCalls,
    ) -> None:
        calls = [Call(id, request.tools[name], args) for id, name, args in tools]
        await Call.async_run_all(calls)
        messages.append(self._tool_call(calls))
        messages.extend(self._tool_results(calls))
        response.calls.extend(calls)


def _optional[T](value: T | None) -> T | openai.NotGiven:
    return value if value is not None else openai.NOT_GIVEN
