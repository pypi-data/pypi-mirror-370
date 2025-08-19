from abc import ABC, abstractmethod

from igbot_base.tool import ToolCall


class ToolPreMerger(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def supports_tools(self) -> list[str]:
        pass

    @abstractmethod
    def process_tool_results(self, tool_calls: list[ToolCall]):
        pass