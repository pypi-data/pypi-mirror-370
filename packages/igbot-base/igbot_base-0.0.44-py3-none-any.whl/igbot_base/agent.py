from abc import ABC, abstractmethod

from igbot_base.additional_data import AdditionalData, EMPTY
from igbot_base.agent_response import AgentResponse

from igbot_base.exception_handler import ExceptionHandler, ReturnFailedResponseGracefully
from igbot_base.logging_adapter import get_logger
from igbot_base.llmmemory import LlmMemory

logger = get_logger("application")


class Agent(ABC):

    def __init__(self, name, exception_handler: ExceptionHandler = ReturnFailedResponseGracefully):
        self.__name = name
        self.__ex_handler = exception_handler

    def invoke(self, query, memory: LlmMemory) -> AgentResponse:
        logger.debug("Invoke %s with query: %s", self.describe(), query)
        try:
            return self._invoke(query, memory)
        except Exception as e:
            logger.exception("Exception occurred at %s for query %s: %s", self.describe(), query, e)
            return self.__ex_handler.handle(e)

    def add_llm_message(self, llm_message, memory: LlmMemory) -> AgentResponse:
        logger.debug("Invoke %s with llm_message: %s", self.describe(), llm_message)
        try:
            return self._add_llm_message(llm_message, memory)
        except Exception as e:
            logger.exception("Exception occurred at %s for llm_message %s: %s", self.describe(), llm_message, e)
            return self.__ex_handler.handle(e)

    @abstractmethod
    def _invoke(self, query, memory: LlmMemory, params: AdditionalData = EMPTY) -> AgentResponse:
        pass

    @abstractmethod
    def _add_llm_message(self, llm_message, memory: LlmMemory) -> AgentResponse:
        pass

    @abstractmethod
    def describe(self):
        pass

    def __str__(self):
        return self.describe()
