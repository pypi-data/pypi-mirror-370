from abc import ABC, abstractmethod


class LlmMemory(ABC):

    @abstractmethod
    def retrieve(self):
        pass

    @abstractmethod
    def append_user(self, content: str):
        pass

    @abstractmethod
    def append_assistant(self, content: str):
        pass

    @abstractmethod
    def append_system(self, content: str):
        pass

    @abstractmethod
    def append_tool_request(self, message):
        pass

    @abstractmethod
    def append_tool_response(self, tool_call_id: str, content: str):
        pass

    @abstractmethod
    def clean_conversation(self):
        pass

    @abstractmethod
    def delete_last_user_message(self):
        pass

    @abstractmethod
    def delete_last_tool_message(self):
        pass

    @abstractmethod
    def delete_last_assistant_message(self):
        pass

    @abstractmethod
    def revert_to_snapshot(self):
        pass

    @abstractmethod
    def set_snapshot(self):
        pass

    @abstractmethod
    def describe(self):
        pass

    @abstractmethod
    def slice(self, messages_number, skip_tool=True):
        pass

    def __str__(self):
        return self.describe()
