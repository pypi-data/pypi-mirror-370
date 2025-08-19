from abc import ABC, abstractmethod
from typing import Union, Dict, List
import json
import tiktoken


class BaseTokenizer(ABC):
    @abstractmethod
    def count_tokens(self, data: Union[str, Dict, None]) -> int:
        pass


class OpenAiTokenizer(BaseTokenizer):

    def __init__(self, model_name):
        self.__tokenizer = tiktoken.encoding_for_model(model_name)

    def count_tokens(self, data: Union[str: Dict, List, None]) -> int:
        if data is None:
            return 0
        elif isinstance(data, str):
            return len(self.__tokenizer.encode(data))
        elif isinstance(data, dict):
            dict_as_str = json.dumps(data, separators=(",", ":"))
            return len(self.__tokenizer.encode(dict_as_str))
        elif isinstance(data, list):
            token_number = 0
            for datum in data:
                token_number += self.count_tokens(datum)
            return token_number
        else:
            raise TypeError("Expected either a string, a dictionary, a list,  or None.")
