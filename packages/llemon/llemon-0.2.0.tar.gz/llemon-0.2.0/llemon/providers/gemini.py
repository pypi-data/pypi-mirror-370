from __future__ import annotations

import json
import logging
from typing import AsyncIterator

from google import genai
from google.genai.types import (
    AutomaticFunctionCallingConfig,
    Content,
    FinishReason,
    FunctionDeclaration,
    GenerateContentConfig,
    GenerateContentResponse,
    HttpOptions,
    ModelContent,
    Part,
    Tool,
    ToolListUnion,
    UserContent,
)
from pydantic import BaseModel

from llemon.apis.llm.llm import LLM
from llemon.apis.llm.llm_model_property import LLMModelProperty
from llemon.errors import Error, InitializationError
from llemon.models.file import File
from llemon.models.generate import GenerateRequest, GenerateResponse
from llemon.models.generate_data import GenerateDataRequest, GenerateDataResponse
from llemon.models.generate_stream import GenerateStreamRequest, GenerateStreamResponse
from llemon.models.tool import Call
from llemon.types import NS, ToolCalls
from llemon.utils.logs import ASSISTANT, SYSTEM, USER

log = logging.getLogger(__name__)


class Gemini(LLM):

    pro25 = LLMModelProperty("gemini-2.5-pro")
    flash25 = LLMModelProperty("gemini-2.5-flash")
    lite25 = LLMModelProperty("gemini-2.5-flash-lite")
    flash2 = LLMModelProperty("gemini-2.0-flash")
    lite2 = LLMModelProperty("gemini-2.0-flash-lite")

    def __init__(
        self,
        api_key: str | None = None,
        project: str | None = None,
        location: str | None = None,
        version: str | None = None,
    ) -> None:
        if sum([bool(api_key), bool(project) or bool(location)]) != 1:
            raise InitializationError("either API key or project and location must be provided")
        options: NS = {}
        if version:
            options["http_options"] = HttpOptions(api_version=version)
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = genai.Client(project=project, location=location, vertexai=True)

    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        response = GenerateResponse(request)
        contents = await self._contents(request)
        return await self._generate(request, response, self._config(request), contents)

    async def generate_stream(self, request: GenerateStreamRequest) -> GenerateStreamResponse:
        response = GenerateStreamResponse(request)
        contents = await self._contents(request)
        return await self._generate_stream(request, response, self._config(request), contents)

    async def generate_data[T: BaseModel](self, request: GenerateDataRequest[T]) -> GenerateDataResponse[T]:
        response = GenerateDataResponse(request)
        contents = await self._contents(request)
        return await self._generate_data(request, response, self._config(request), contents)

    def _config(self, request: GenerateRequest) -> GenerateContentConfig:
        config = GenerateContentConfig(
            temperature=request.temperature,
            max_output_tokens=request.max_tokens,
            seed=request.seed,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty,
            top_p=request.top_p,
            top_k=request.top_k,
            stop_sequences=request.stop,
            tools=self._tools(request),
            automatic_function_calling=AutomaticFunctionCallingConfig(
                disable=True,
            ),
        )
        if request.instructions:
            instructions = request.get_instructions()
            log.debug(SYSTEM + "%s", instructions)
            config.system_instruction = self._system(instructions)
        if isinstance(request, GenerateDataRequest):
            config.response_mime_type = "application/json"
            config.response_schema = request.schema
        return config

    async def _contents(self, request: GenerateRequest) -> list[Content]:
        contents: list[Content] = []
        if request.history:
            request.history._log()
            for request_, response_ in request.history.interactions:
                if not isinstance(request_, GenerateRequest) or not isinstance(response_, GenerateResponse):
                    continue
                contents.append(await self._user(request_.get_user_input(), request_.files))
                if response_.calls:
                    contents.append(self._tool_call(response_.calls))
                    contents.append(self._tool_results(response_.calls))
                contents.append(self._assistant(response_.text))
        user_input = request.get_user_input()
        log.debug(USER + "%s", user_input)
        contents.append(await self._user(user_input, request.files))
        return contents

    def _system(self, instructions: str) -> Content:
        return Content(parts=[Part.from_text(text=instructions)])

    async def _user(self, text: str, files: list[File]) -> UserContent:
        parts: list[Part] = []
        if files:
            if text:
                parts.append(Part.from_text(text=text))
            for file in files:
                await file.fetch()
                assert file.data is not None
                part = Part.from_bytes(data=file.data, mime_type=file.mimetype)
                parts.append(part)
        else:
            parts.append(Part.from_text(text=text))
        return UserContent(parts=parts)

    def _assistant(self, content: str) -> ModelContent:
        return ModelContent(parts=[Part.from_text(text=content)])

    def _tool_call(self, calls: list[Call]) -> ModelContent:
        parts: list[Part] = []
        for call in calls:
            part = Part.from_function_call(
                name=call.tool.name,
                args=call.arguments,
            )
            parts.append(part)
        return ModelContent(parts=parts)

    def _tool_results(self, calls: list[Call]) -> Content:
        parts: list[Part] = []
        for call in calls:
            parts.append(
                Part.from_function_response(
                    name=call.tool.name,
                    response={"result": call.result},
                )
            )
        return Content(role="tool", parts=parts)

    def _tools(self, request: GenerateRequest) -> ToolListUnion | None:
        if not request.tools or request.use_tool is False:
            return None
        tools: ToolListUnion = []
        for tool in request.tools.values():
            tools.append(
                Tool(
                    function_declarations=[
                        FunctionDeclaration(
                            name=tool.name,
                            description=tool.description,
                            parameters_json_schema=tool.parameters,
                        )
                    ]
                )
            )
        return tools

    async def _generate(
        self,
        request: GenerateRequest,
        response: GenerateResponse,
        config: GenerateContentConfig,
        contents: list[Content],
    ) -> GenerateResponse:
        try:
            gemini_response = await self.client.aio.models.generate_content(
                model=request.model.name,
                contents=contents,
                config=config,
            )
        except Exception as error:
            raise Error(error)
        result = self._parse_response(gemini_response, request.get_return_incomplete_message())
        if isinstance(result, list):
            await self._run_tools(request, response, contents, result)
            return await self._generate(request, response, config, contents)
        log.debug(ASSISTANT + "%s", result)
        response.complete_text(result)
        return response

    async def _generate_stream(
        self,
        request: GenerateStreamRequest,
        response: GenerateStreamResponse,
        config: GenerateContentConfig,
        contents: list[Content],
    ) -> GenerateStreamResponse:
        try:
            anthropic_response = await self.client.aio.models.generate_content_stream(
                model=request.model.name,
                contents=contents,
                config=config,
            )
        except Exception as error:
            raise Error(error)

        async def stream() -> AsyncIterator[str]:
            tool_calls: ToolCalls = []
            async for chunk in anthropic_response:
                result = self._parse_response(chunk, request.get_return_incomplete_message())
                if isinstance(result, list):
                    tool_calls.extend(result)
                elif result:
                    yield result
            if tool_calls:
                await self._run_tools(request, response, contents, tool_calls)
                await self._generate_stream(request, response, config, contents)
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
        config: GenerateContentConfig,
        contents: list[Content],
    ) -> GenerateDataResponse[T]:
        try:
            gemini_response = await self.client.aio.models.generate_content(
                model=request.model.name,
                contents=contents,
                config=config,
            )
        except Exception as error:
            raise Error(error)
        result = self._parse_response(gemini_response, return_incomplete_message=False)
        if isinstance(result, list):
            await self._run_tools(request, response, contents, result)
            return await self._generate_data(request, response, config, contents)
        data = request.schema.model_validate(json.loads(result))
        log.debug(ASSISTANT + "%s", data)
        response.complete_data(data)
        return response

    def _parse_response(
        self,
        response: GenerateContentResponse,
        return_incomplete_message: bool,
    ) -> str | ToolCalls:
        if not response.candidates:
            raise Error(f"{self} returned no candidates")
        candidate = response.candidates[0]
        match candidate.finish_reason:
            case FinishReason.STOP:
                pass
            case FinishReason.MAX_TOKENS:
                if not return_incomplete_message:
                    raise Error(f"{self} reached the maximum number of tokens")
            case _:
                if response.prompt_feedback and response.prompt_feedback.block_reason_message:
                    raise Error(f"{self} was blocked: {response.prompt_feedback.block_reason_message}")
                raise Error(f"{self} was aborted: {candidate.finish_message}")
        if response.function_calls:
            tool_calls: ToolCalls = []
            for function_call in response.function_calls:
                tool_calls.append((function_call.id or "", function_call.name or "", function_call.args or {}))
            return tool_calls
        if not candidate.content:
            raise Error(f"{self} returned no content")
        if not candidate.content.parts:
            raise Error(f"{self} returned no parts")
        part = candidate.content.parts[0]
        if not part.text:
            raise Error(f"{self} returned no text")
        return part.text

    async def _run_tools(
        self,
        request: GenerateRequest,
        response: GenerateResponse,
        contents: list[Content],
        tool_calls: ToolCalls,
    ) -> None:
        calls = [Call(id, request.tools[name], args) for id, name, args in tool_calls]
        await Call.async_run_all(calls)
        contents.append(self._tool_call(calls))
        contents.append(self._tool_results(calls))
        response.calls.extend(calls)
