from abc import ABC, abstractmethod


class AbstractToolkit(ABC):
    @abstractmethod
    def get_tools(self):
        pass
