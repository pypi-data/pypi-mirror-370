from __future__ import annotations

from functools import cached_property
from typing import Any, ClassVar, cast, override

from pydantic import BaseModel

from llemon.errors import UnsupportedFeatureError
from llemon.models.generate import GenerateRequest, GenerateResponse
from llemon.types import NS
from llemon.utils.schema import schema_to_model


class GenerateDataRequest[T: BaseModel](GenerateRequest):

    JSON_INSTRUCTION: ClassVar[str] = "Answer ONLY in JSON that adheres EXACTLY to the following JSON schema: {schema}"

    @override
    def __init__(self, *, schema: type[T], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.schema = schema

    def dump(self) -> NS:
        data = super().dump()
        data.update(
            schema=self.schema.model_json_schema(),
        )
        return data

    def append_json_instruction(self) -> None:
        self.append_instruction(self.JSON_INSTRUCTION.format(schema=self.schema.model_json_schema()))

    def check_supported(self) -> None:
        super().check_supported()
        if not self.model.config.supports_json:
            raise UnsupportedFeatureError(f"{self.model} doesn't support structured output")

    @classmethod
    def _restore(cls, data: NS) -> tuple[NS, NS]:
        args, attrs = super()._restore(data)
        args.update(
            schema=schema_to_model(data["schema"]),
        )
        return args, attrs


class GenerateDataResponse[T: BaseModel](GenerateResponse):

    request: GenerateDataRequest[T]

    def __init__(self, request: GenerateDataRequest[T]) -> None:
        super().__init__(request)
        self._data: T | None = None

    @cached_property
    def data(self) -> T:
        if not self.ended:
            raise self._incomplete_request()
        return cast(T, self._data)

    def complete_data(self, data: T) -> None:
        self._data = data
        super().complete_text(self._data.model_dump_json())

    def dump(self) -> NS:
        data = super().dump()
        data.update(
            data=self.data.model_dump(),
        )
        return data

    @classmethod
    def _restore(self, data: NS) -> tuple[NS, NS]:
        args, attrs = super()._restore(data)
        request: GenerateDataRequest[BaseModel] = args["request"]
        attrs.update(
            _data=request.schema.model_validate(data["data"]),
        )
        return args, attrs
