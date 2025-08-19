from pydantic.v1 import BaseModel
from typing import Any, Dict, Optional

class AdditionalData(BaseModel):
    data: Dict[str, Any]

    def get(self, key: str) -> Optional[Any]:
        """
        Get the value associated with the key, or return None if the key doesn't exist.

        :param key: The key to look for in the dictionary.
        :return: The value associated with the key, or None.
        """
        return self.data.get(key)


EMPTY = AdditionalData(data={})