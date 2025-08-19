from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel


class Notification(BaseModel):
    data: Any


class Notifier(ABC):

    @abstractmethod
    def notify(self, notification: Notification):
        pass
