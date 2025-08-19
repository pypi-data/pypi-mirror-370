from __future__ import annotations

import datetime as dt
from functools import cached_property
from typing import ClassVar

from llemon.errors import InProgressError
from llemon.types import NS
from llemon.utils.now import now


class Request:

    classes: ClassVar[dict[str, type[Request]]] = {}

    def __init__(self, history: History | None = None) -> None:
        self.history = history or History()

    def __init_subclass__(cls) -> None:
        cls.classes[cls.__name__] = cls

    @classmethod
    def load(cls, data: NS) -> Request:
        request_class = cls.classes[data["type"]]
        args, attrs = request_class._restore(data)
        request = request_class(**args)
        for name, value in attrs.items():
            setattr(request, name, value)
        return request

    def dump(self) -> NS:
        return dict(
            type=self.__class__.__name__,
        )

    def check_supported(self) -> None:
        pass

    def format(self) -> str:
        raise NotImplementedError()

    @classmethod
    def _restore(cls, data: NS) -> tuple[NS, NS]:
        return {}, {}


class Response:

    classes: ClassVar[dict[str, type[Response]]] = {}

    def __init__(self, request: Request) -> None:
        self.request = request
        self.started = now()
        self.ended: dt.datetime | None = None

    def __init_subclass__(cls) -> None:
        cls.classes[cls.__name__] = cls

    @classmethod
    def load(cls, data: NS) -> Response:
        response_class: type[Response] = cls.classes[data["type"]]
        args, attrs = response_class._restore(data)
        response = response_class(**args)
        for name, value in attrs.items():
            setattr(response, name, value)
        return response

    @cached_property
    def duration(self) -> float:
        if not self.ended:
            raise self._incomplete_request()
        return (self.ended - self.started).total_seconds()

    def dump(self) -> NS:
        if not self.ended:
            raise self._incomplete_request()
        return dict(
            type=self.__class__.__name__,
            request=self.request.dump(),
            started=self.started.isoformat(),
            ended=self.ended.isoformat(),
        )

    def complete(self) -> None:
        self.ended = now()

    def format(self) -> str:
        raise NotImplementedError()

    @classmethod
    def _restore(cls, data: NS) -> tuple[NS, NS]:
        args = dict(
            request=Request.load(data["request"]),
        )
        attrs = dict(
            started=dt.datetime.fromisoformat(data["started"]),
            ended=dt.datetime.fromisoformat(data["ended"]),
        )
        return args, attrs

    def _incomplete_request(self) -> InProgressError:
        return InProgressError(f"{self.request} hasn't completed yet")


from llemon.models.history import History
