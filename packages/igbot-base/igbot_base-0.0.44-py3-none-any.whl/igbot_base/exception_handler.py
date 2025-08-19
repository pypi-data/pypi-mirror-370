from abc import ABC, abstractmethod

from igbot_base.agent_response import AgentResponse


class ExceptionHandler(ABC):

    @abstractmethod
    def handle(self, e: Exception):
        pass


class NoopExceptionHandler(ExceptionHandler):

    def handle(self, e: Exception):
        pass


class PrintingExceptionHandler(ExceptionHandler):

    def handle(self, e: Exception):
        print(e)


class ReturnFailedResponseGracefully(ExceptionHandler):

    def handle(self, e: Exception):
        return AgentResponse.error(str(e), e)

