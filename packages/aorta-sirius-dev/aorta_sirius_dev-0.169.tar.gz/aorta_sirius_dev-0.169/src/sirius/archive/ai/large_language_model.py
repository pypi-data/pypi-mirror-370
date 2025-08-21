from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Callable, Dict, Any

from openai._types import NOT_GIVEN, NotGiven

from sirius.archive.ai.long_term_memory import LongTermMemory
from sirius.common import DataClass
from sirius.exceptions import OperationNotSupportedException


class LargeLanguageModel(Enum):
    GPT4o = "gpt-4o"
    GPT4oMini = "gpt-4o-mini"


open_ai_large_language_model_list: List["LargeLanguageModel"] = [
    LargeLanguageModel.GPT4o,
    LargeLanguageModel.GPT4oMini
]


class Context(DataClass, ABC):
    pass

    @staticmethod
    @abstractmethod
    def get_system_context(message: str) -> "Context":
        pass

    @staticmethod
    @abstractmethod
    def get_user_context(message: str) -> "Context":
        pass

    @staticmethod
    @abstractmethod
    def get_image_from_url_context(message: str, image_url: str) -> "Context":
        pass

    @staticmethod
    @abstractmethod
    def get_image_from_path_context(message: str, image_path: str) -> "Context":
        pass


class Function(DataClass, ABC):
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]
    function_documentation: Dict[str, Any]


class Assistant(DataClass, ABC):
    large_language_model: LargeLanguageModel
    temperature: float
    context_list: List[Context] = []
    function_list: List[Function] = []
    max_tokens: int | NotGiven = NOT_GIVEN
    instructions_long_term_memory_list: List[LongTermMemory]
    knowledge_long_term_memory_list: List[LongTermMemory]

    @staticmethod
    def get(large_language_model: LargeLanguageModel,
            temperature: float | None = 0.2,
            context_list: List[Context] | None = None,
            function_list: List[Function] | None = None,
            prompt_template: str = "You are a helpful assistant",
            instructions_long_term_memory_list: List[LongTermMemory] | None = None,
            knowledge_long_term_memory_list: List[LongTermMemory] | None = None
            ) -> "Assistant":
        context_list = [] if context_list is None else context_list
        function_list = [] if function_list is None else function_list
        instructions_long_term_memory_list = [] if instructions_long_term_memory_list is None else instructions_long_term_memory_list
        knowledge_long_term_memory_list = [] if knowledge_long_term_memory_list is None else knowledge_long_term_memory_list

        if large_language_model in open_ai_large_language_model_list:
            from sirius.archive.ai.open_ai import OpenAIGPTAssistant, OpenAIGPTContext
            context_list.append(OpenAIGPTContext.get_system_context(prompt_template))
            return OpenAIGPTAssistant(large_language_model=large_language_model,
                                      temperature=temperature,
                                      context_list=context_list,
                                      function_list=function_list,
                                      instructions_long_term_memory_list=instructions_long_term_memory_list,
                                      knowledge_long_term_memory_list=knowledge_long_term_memory_list)

        raise OperationNotSupportedException(f"{large_language_model.value} is not yet supported")

    @abstractmethod
    async def ask(self, question: str, image_url: str | None = None, image_path: str | None = None) -> str:
        pass
