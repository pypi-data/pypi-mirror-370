from enum import Enum
from typing import Optional

class Type(Enum):
    SUCCESS = 1,
    NO_CONTENT = 2,
    ERROR = 3


class AgentResponse:

    def __init__(self, response: any, response_type: Type, exception: Optional[Exception]):
        self.__response = response
        self.__type = response_type
        self.__exception = exception

    def is_successful(self):
        return self.__type == Type.SUCCESS

    def is_error(self):
        return self.__type == Type.ERROR

    def is_no_content(self):
        return self.__type == Type.NO_CONTENT

    def get_response(self):
        return self.__response

    @staticmethod
    def error(error_message: str, exception: Optional[Exception]):
        return AgentResponse(error_message, Type.ERROR, exception)

    @staticmethod
    def success(response: any):
        return AgentResponse(response, Type.SUCCESS, None)

    @staticmethod
    def no_content():
        return AgentResponse("", Type.NO_CONTENT, None)

    def get_exception(self):
        return self.__exception
