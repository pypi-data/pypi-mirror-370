from abc import ABC, abstractmethod
from typing import Any, Optional, Callable

from pydantic import BaseModel


class ToolResponse(BaseModel):
    message: Optional[str] = None
    data: Optional[Any] = None
    tool_name: str

class ToolCall(BaseModel):
    args: Optional[dict] = None
    tool_name: str

class Tool(ABC):

    def __init__(
            self,
            name: str):
        self._name = name

    def get_name(self):
        return self._name

    @abstractmethod
    def get_function(self) -> Callable[..., ToolResponse]:
        pass

    @abstractmethod
    def get_definition(self):
        pass

    @abstractmethod
    def describe(self):
        pass

    def __str__(self):
        return self.describe()