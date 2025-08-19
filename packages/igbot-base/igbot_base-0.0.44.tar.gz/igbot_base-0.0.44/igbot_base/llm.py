from abc import ABC, abstractmethod
from builtins import dict
from typing import Optional

from igbot_base.additional_data import AdditionalData, EMPTY
from igbot_base.exception_handler import ExceptionHandler, NoopExceptionHandler
from igbot_base.llmmemory import LlmMemory
from igbot_base.models import Model
from igbot_base.logging_adapter import get_logger

from igbot_base.base_exception import BaseLlmException

logger = get_logger("application")


class Llm(ABC):

    def __init__(
            self,
            name: str,
            model: Model,
            temperature: float,
            response_format: Optional[dict],
            llm_exception_handler: ExceptionHandler = NoopExceptionHandler()):
        self._name = name
        self._model = model
        self._temperature = temperature
        self._format = response_format
        self._exception_handler = llm_exception_handler

    def __str__(self):
        return f"Llm({self._name} {self._model.value.get_name()})"

    @abstractmethod
    def _call(self, user_query: str, history: LlmMemory, params: dict, additonal_data: AdditionalData = EMPTY) -> str:
        pass

    @abstractmethod
    def _add_llm_message(self, user_query: str, history: LlmMemory, params: dict) -> str:
        pass

    def _revert_memory(self, history: LlmMemory):
        history.revert_to_snapshot()

    def call(self, user_query: str, history: LlmMemory, params: dict) -> str:
        logger.debug("Call to %s with question: %s", self.__str__(), user_query)
        history.set_snapshot()
        try:
            response = self._call(user_query, history, params)
            logger.debug("LLM %s %s responded: %s", self._name, self._model.value.get_name(), response)
            return response
        except Exception as e:
            logger.error("Error occurred in LLM %s, Model %s at calling the API: %s",
                         self._name, self._model.value.get_name(), e)
            self._revert_memory(history)
            self._exception_handler.handle(e)
            raise BaseLlmException(f"Exception occurred while calling llm api", self, e)

    def add_llm_message(self, llm_message: str, history: LlmMemory, params: dict) -> str:
        logger.debug("Call to %s with llm message: %s", self.__str__(), llm_message)
        history.set_snapshot()
        try:
            response = self._add_llm_message(llm_message, history, params)
            logger.debug("LLM %s %s responded: %s", self._name, self._model.value.get_name(), response)
            return response
        except Exception as e:
            logger.error("Error occurred in LLM %s, Model %s at calling the API: %s",
                         self._name, self._model.value.get_name(), e)
            self._revert_memory(history)
            self._exception_handler.handle(e)
            raise BaseLlmException(f"Exception occurred while calling llm api", self, e)

    def get_additional_llm_args(self):
        args = {}
        if self._temperature is not None:
            args["temperature"] = self._temperature
        if self._format is not None:
            args["response_format"] = self._format

        return args

