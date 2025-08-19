from __future__ import annotations

import logging
from typing import Iterator, Self, overload

from llemon.types import NS, Interaction

log = logging.getLogger(__name__)


class History:

    def __init__(self, interactions: list[Interaction] | None = None) -> None:
        if interactions is None:
            interactions = []
        self.interactions = interactions

    def __str__(self) -> str:
        return self.format()

    def __repr__(self) -> str:
        return f"<history: {self.format().replace('\n', ' | ')}>"

    def __bool__(self) -> bool:
        return bool(self.interactions)

    def __len__(self) -> int:
        return len(self.interactions)

    def __iter__(self) -> Iterator[Interaction]:
        yield from self.interactions

    @overload
    def __getitem__(self, index: int) -> Interaction: ...

    @overload
    def __getitem__(self, index: slice) -> Self: ...

    def __getitem__(self, index: int | slice) -> Interaction | Self:
        if isinstance(index, slice):
            return type(self)(self.interactions[index])
        return self.interactions[index]

    @classmethod
    def load(cls, data: NS) -> History:
        history = cls()
        models: dict[str, NS] = data.get("models", {})
        tools: dict[str, NS] = data.get("tools", {})
        files: dict[str, NS] = data.get("files", {})
        for interaction in data["history"]:
            request_data = interaction["request"]
            if "model" in request_data:
                request_data["model"] = models[request_data["model"]]
            if "files" in request_data:
                request_data["files"] = [files[name] for name in request_data["files"]]
            if "tools" in request_data:
                request_data["tools"] = [tools[name] for name in request_data["tools"]]
            response_data = interaction["response"]
            for call in response_data.get("calls", []):
                call["tool"] = tools[call["tool"]]
            response_data["request"] = request_data
            response = Response.load(response_data)
            response.request.history = history
            history.add(response.request, response)
        return history

    def dump(self) -> NS:
        history: list[NS] = []
        models: dict[str, NS] = {}
        tools: dict[str, NS] = {}
        files: dict[str, NS] = {}
        for request, response in self.interactions:
            response_data = response.dump()
            for call in response_data.get("calls", []):
                tool_name = call["tool"]["name"]
                tools[tool_name] = call["tool"]
                call["tool"] = tool_name
            request_data = response_data.pop("request")
            if "model" in request_data:
                model_name = request_data["model"]["name"]
                models[model_name] = request_data["model"]
                request_data["model"] = model_name
            if "files" in request_data:
                files.update({file["name"]: file for file in request_data["files"]})
                request_data["files"] = [file["name"] for file in request_data["files"]]
            if "tools" in request_data:
                tools.update({tool["name"]: tool for tool in request_data["tools"]})
                request_data["tools"] = [tool["name"] for tool in request_data["tools"]]
            history.append({"request": request_data, "response": response_data})
        return dict(
            history=history,
            models=models,
            tools=tools,
            files=files,
        )

    def add(self, request: Request, response: Response) -> None:
        self.interactions.append((request, response))

    def format(self) -> str:
        interactions: list[str] = []
        for request, response in self.interactions:
            interactions.append(request.format())
            interactions.append(response.format())
        return "\n".join(interactions)

    def _log(self) -> None:
        extra = {"markup": True, "highlighter": None}
        log.debug("[bold underline]history[/]", extra=extra)
        for request, response in self.interactions:
            timestamp = f"{response.started:%H:%M:%S}-{response.ended:%H:%M:%S} ({response.duration:.2f}s)"
            log.debug(f"[bold yellow]{request.__class__.__name__}[/] ({timestamp})", extra=extra)
            log.debug(request.format(), extra=extra)
            log.debug(response.format(), extra=extra)


from llemon.models.request import Request, Response
