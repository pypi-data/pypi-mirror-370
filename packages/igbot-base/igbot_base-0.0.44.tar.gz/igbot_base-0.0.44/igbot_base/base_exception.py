


class IgBotBaseException(Exception):

    def __init__(self, message, cause: Exception = None):
        super().__init__(message)
        self.cause = cause

    def __str__(self):
        result = self.args[0]
        if self.cause:
            result += f" Caused by: {self.cause}"

        return result


class BaseAgentException(IgBotBaseException):

    def __init__(self, message, agent: object, cause: Exception = None):
        super().__init__(message, cause)
        self.agent = agent.__str__()

    def __str__(self):
        result = super().__str__()
        result += f" at agent {self.agent}"


class BaseLlmException(IgBotBaseException):

    def __init__(self, message, llm: object, cause: Exception = None):
        super().__init__(message, cause)
        self.llm = llm.__str__()

    def __str__(self):
        result = super().__str__()
        result += f" at llm {self.llm}"


class BaseMemoryException(IgBotBaseException):

    def __init__(self, message, memory: object, cause: Exception = None):
        super().__init__(message, cause)
        self.memory = memory.__str__()

    def __str__(self):
        result = super().__str__()
        result += f" at memory {self.memory}"


class BasePromptException(IgBotBaseException):

    def __init__(self, message, prompt: object, cause: Exception = None):
        super().__init__(message, cause)
        self.prompt = prompt.__str__()

    def __str__(self):
        result = super().__str__()
        result += f" at prompt {self.prompt}"


class BaseRetrieverException(IgBotBaseException):

    def __init__(self, message, retriever: object, cause: Exception = None):
        super().__init__(message, cause)
        self.retriever = retriever.__str__()

    def __str__(self):
        result = super().__str__()
        result += f" at retriever {self.retriever}"


class BaseToolException(IgBotBaseException):

    def __init__(self, message, tool: object, cause: Exception = None):
        super().__init__(message, cause)
        self.tool = tool.__str__()

    def __str__(self):
        result = super().__str__()
        result += f" at tool {self.tool}"
