from abc import ABC, abstractmethod

class CrawlerClient(ABC):

    @abstractmethod
    async def get(self, url : str):
        pass