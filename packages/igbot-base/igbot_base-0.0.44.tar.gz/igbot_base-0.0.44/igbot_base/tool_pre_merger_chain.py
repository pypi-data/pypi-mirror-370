from igbot_base.tool_pre_merger import ToolPreMerger
from igbot_base.tool import ToolCall

from igbot_base.logging_adapter import get_logger

logger = get_logger("application")

class ToolPreMergerChain:
    def __init__(self, mergers: list[ToolPreMerger]):
        self.__mergers = mergers

    def process(self, tool_responses: list[ToolCall]):
        for merger in self.__mergers:
            supported_tools = merger.supports_tools()
            matching_responses = [r for r in tool_responses if r.tool_name in supported_tools]
            if len(matching_responses) != 0:
                logger.debug("Merging responses with %s for tools: %s", merger, supported_tools)
                merger.process_tool_results(matching_responses)
