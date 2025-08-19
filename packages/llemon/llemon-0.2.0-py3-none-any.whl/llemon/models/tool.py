from __future__ import annotations

import asyncio
import importlib
import inspect
import json
import logging
import traceback
from concurrent.futures import Future, ThreadPoolExecutor, wait
from functools import cached_property
from typing import Any, Callable, ClassVar, NoReturn, get_type_hints

from pydantic import BaseModel, ConfigDict

from llemon.errors import Error, InProgressError
from llemon.tools.toolbox import Toolbox
from llemon.types import NS, ToolsArgument
from llemon.utils.logs import TOOL
from llemon.utils.trim import trim

log = logging.getLogger(__name__)
parameter_schemas: dict[Callable[..., Any], NS] = {}
undefined = object()


class Tool:

    def __init__(
        self,
        name: str,
        description: str,
        parameters: NS,
        function: Callable[..., Any] | None = None,
    ) -> None:
        if function is None:
            function = self._not_runnable
        self.name = name
        self.description = description
        self.parameters = parameters
        self.function = function

    def __str__(self) -> str:
        return f"tool {self.name!r}"

    def __repr__(self) -> str:
        return f"<{self}>"

    @classmethod
    def resolve(cls, tools: ToolsArgument) -> dict[str, Tool]:
        if tools is None:
            return {}
        if isinstance(tools, dict):
            return tools
        resolved: dict[str, Tool] = {}
        for tool in tools:
            if isinstance(tool, Toolbox):
                for name, description, function in tool.tools:
                    parameters = cls._parse_parameters(function)
                    resolved[name] = cls(name, description, parameters, function)
            else:
                resolved[tool.__name__] = cls.from_function(tool)
        return resolved

    @classmethod
    def from_function(cls, function: Callable[..., Any]) -> Tool:
        parameters = cls._parse_parameters(function)
        return cls(
            name=function.__name__,
            description=trim(function.__doc__ or ""),
            parameters=parameters,
            function=function,
        )

    @classmethod
    def load(cls, tool: NS) -> Tool:
        function = tool.get("function")
        if function:
            module, function = function.rsplit(".", 1)
            module = importlib.import_module(module)
            function = getattr(module, function)
        else:
            function = None
        return cls(
            name=tool["name"],
            description=tool["description"],
            parameters=tool["parameters"],
            function=function,
        )

    def dump(self) -> NS:
        data = dict(
            name=self.name,
            description=self.description,
            parameters=self.parameters,
        )
        if self.function is not self._not_runnable:
            data["function"] = f"{self.function.__module__}.{self.function.__name__}"
        return data

    @classmethod
    def _not_runnable(self, *args, **kwargs: Any) -> NoReturn:
        raise RuntimeError(f"{self} is not associated with a runnable function")

    @classmethod
    def _parse_parameters(self, function: Callable[..., Any]) -> NS:
        if function in parameter_schemas:
            return parameter_schemas[function]
        annotations = get_type_hints(function)
        annotations.pop("return", None)
        model_class: type[BaseModel] = type(
            function.__name__,
            (BaseModel,),
            {"__annotations__": annotations, "model_config": ConfigDict(extra="forbid")},
        )
        schema = model_class.model_json_schema()
        parameter_schemas[function] = schema
        return schema


class Call:

    executor: ClassVar[ThreadPoolExecutor | None] = None

    def __init__(
        self,
        id: str,
        tool: Tool,
        arguments: NS,
        return_value: Any = undefined,
        error: str | None = None,
    ) -> None:
        self.id = id
        self.tool = tool
        self.arguments = arguments
        self._return_value = return_value
        self._error = error

    def __str__(self) -> str:
        output = [f"call {self.id!r}: {self.signature}"]
        if self._return_value is not undefined:
            output.append(f" -> {self._return_value}")
        elif self._error is not None:
            output.append(f" -> {self._error!r}")
        return "".join(output)

    def __repr__(self) -> str:
        return f"<{self}>"

    @classmethod
    def load(cls, data: NS) -> Call:
        result = data["result"]
        return cls(
            id=data["id"],
            tool=Tool.load(data["tool"]),
            arguments=data["arguments"],
            return_value=result.get("return_value", undefined),
            error=result.get("error"),
        )

    @classmethod
    def get_executor(cls) -> ThreadPoolExecutor:
        if cls.executor is None:
            cls.executor = ThreadPoolExecutor()
        return cls.executor

    @classmethod
    def run_all(cls, calls: list[Call]) -> None:
        executor = cls.get_executor()
        futures: list[Future[Any]] = []
        for call in calls:
            future = executor.submit(call.run)
            futures.append(future)
        wait(futures)

    @classmethod
    async def async_run_all(cls, calls: list[Call]) -> None:
        tasks = [asyncio.create_task(call.async_run()) for call in calls]
        await asyncio.gather(*tasks, return_exceptions=True)

    @cached_property
    def signature(self) -> str:
        args = ", ".join(f"{key}={value!r}" for key, value in self.arguments.items())
        return f"{self.tool.name}({args})"

    @cached_property
    def arguments_json(self) -> str:
        return json.dumps(self.arguments)

    @cached_property
    def return_value(self) -> Any:
        if self._error:
            raise Error(self._error)
        if self._return_value is undefined:
            raise self._incomplete_call()
        return self._return_value

    @cached_property
    def error(self) -> str | None:
        if not self._error and self._return_value is undefined:
            raise self._incomplete_call()
        return self._error

    @cached_property
    def result(self) -> NS:
        if self._error:
            return {"error": self.error}
        elif self._return_value is undefined:
            raise self._incomplete_call()
        return {"return_value": self.return_value}

    @cached_property
    def result_json(self) -> str:
        result: NS = {}
        if self._error:
            result["error"] = self._error
        else:
            if isinstance(self.return_value, BaseModel):
                return_value = self.return_value.model_dump_json()
            try:
                return_value = json.dumps(self.return_value)
            except TypeError:
                return_value = str(self.return_value)
            result["return_value"] = return_value
        return json.dumps(result)

    def dump(self) -> NS:
        return {
            "id": self.id,
            "tool": self.tool.dump(),
            "arguments": self.arguments,
            "result": self.result,
        }

    def run(self) -> None:
        log.debug("running %s", self.signature)
        try:
            self._return_value = self.tool.function(**self.arguments)
            log.debug("%s returned %r", self.signature, self._return_value)
        except Exception as error:
            self._error = self._format_error(error)
            log.debug("%s raised %r", self.signature, self._error)

    async def async_run(self) -> None:
        log.debug(TOOL + "%s", self.signature)
        try:
            if inspect.iscoroutinefunction(self.tool.function):
                return_value = await self.tool.function(**self.arguments)
            else:
                return_value = await asyncio.to_thread(self.tool.function, **self.arguments)
            log.debug("%s returned %r", self.signature, return_value)
            self._return_value = return_value
        except Exception as error:
            self._error = self._format_error(error)
            log.debug("%s raised %r", self.signature, self._error)

    def _incomplete_call(self) -> InProgressError:
        return InProgressError(f"{self} didn't run yet")

    def _format_error(self, error: Exception) -> str:
        return "".join(traceback.format_exception(error.__class__, error, error.__traceback__))
