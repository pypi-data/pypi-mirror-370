from enum import Enum
from openai import OpenAI

from igbot_base.tokenizer import BaseTokenizer, OpenAiTokenizer


class ModelInfo:

    def __init__(self, name, client, tokenizer: BaseTokenizer, max_tokens):
        self.__name = name
        self.__client = client
        self.__tokenizer = tokenizer
        self.__max_tokens = max_tokens

    def get_name(self):
        return self.__name

    def get_client(self):
        return self.__client()

    def get_tokenizer(self) -> BaseTokenizer:
        return self.__tokenizer

    def get_max_tokens(self):
        return self.__max_tokens


class Model(Enum):
    OLLAMA_3_2_LOCAL = ModelInfo("llama3.2", lambda: OpenAI(base_url="http://localhost:11434/v1", api_key='ollama'),
                                 OpenAiTokenizer("gpt-4o"), 128_000)
    OPENAI_GPT_4o_MINI = ModelInfo("gpt-4o-mini", lambda: OpenAI(),
                                   OpenAiTokenizer("gpt-4o"), 128_000)
    OPENAI_GPT_4o = ModelInfo("gpt-4o", lambda: OpenAI(),
                              OpenAiTokenizer("gpt-4o"), 128_000)
    OPENAI_GPT_4o_MINI_JSON = ModelInfo("gpt-4o-mini-2024-07-18", lambda: OpenAI(),
                                        OpenAiTokenizer("gpt-4o"), 128_000)
    OPENAI_GPT_4_1_NANO = ModelInfo("gpt-4.1-nano", lambda: OpenAI(),
                                    OpenAiTokenizer("gpt-4o"), 1_047_576)
    OPENAI_GPT_5 = ModelInfo("gpt-5", lambda: OpenAI(),
                                    OpenAiTokenizer("gpt-4o"), 200_000)
    OPENAI_GPT_5_MINI = ModelInfo("gpt-5-mini", lambda: OpenAI(),
                             OpenAiTokenizer("gpt-4o"), 200_000)
    OPENAI_GPT_5_NANO = ModelInfo("gpt-5-nano", lambda: OpenAI(),
                             OpenAiTokenizer("gpt-4o"), 200_000)
    OPENAI_GPT_5_THINKING_NANO = ModelInfo("gpt-5-thinking-nano", lambda: OpenAI(),
                                  OpenAiTokenizer("gpt-4o"), 150_000)
