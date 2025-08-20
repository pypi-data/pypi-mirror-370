from abc import ABC, abstractmethod


class AbstractFlow(ABC):

    @abstractmethod
    async def start(self, **kwargs):
        """Start Method called on every component.
        """

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def run(self):
        """Execute the code for component.
        """
