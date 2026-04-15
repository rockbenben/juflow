from abc import ABC, abstractmethod

class BaseNotifier(ABC):
    channel: str

    @abstractmethod
    async def send(self, user_settings: dict, article, source) -> bool:
        ...
