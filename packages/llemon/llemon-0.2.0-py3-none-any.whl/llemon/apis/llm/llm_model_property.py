from llemon.apis.llm.llm import LLM
from llemon.apis.llm.llm_model import LLMModel


class LLMModelProperty:

    def __init__(self, name: str) -> None:
        self.name = name

    def __get__(self, llm: LLM, provider: type[LLM]) -> LLMModel:
        return provider.get(self.name)
