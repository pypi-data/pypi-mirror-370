import re
from typing import Optional

from igbot_base.exception_handler import ExceptionHandler, PrintingExceptionHandler
from igbot_base.logging_adapter import get_logger

logger = get_logger("application")


class Prompt:

    def __init__(
            self,
            content: str,
            variables,
            exception_handler: ExceptionHandler = PrintingExceptionHandler()):
        self.__content = content
        self.__variables = variables
        self.__exception_handler = exception_handler

    def __str__(self):
        return f"Prompt({self.__get_content_short()} ({",".join(self.__variables)}))"

    @staticmethod
    def replace_placeholders(text: str, values: dict) -> str:
        def replacer(match):
            key = match.group(1)
            return str(values.get(key, match.group(0)))

        return re.sub(r"\{\{(\w+)\}\}", replacer, text)

    def parse(self, params: Optional[dict]) -> str:
        if len(self.__variables) == 0:
            return self.__content

        try:
            return self.replace_placeholders(self.__content, params)
        except KeyError as e:
            logger.exception("Exception occurred when parsing prompt %s... %s", self.__get_content_short(), e)
            self.__exception_handler.handle(e)

        raise Exception(f"Error while substituting values for prompt")

    def get_content(self) -> str:
        return self.__content

    def __get_content_short(self):
        if len(self.__content) > 15:
            return self.__content[:15]
        else:
            return self.__content
