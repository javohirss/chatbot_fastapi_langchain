from abc import ABC, abstractmethod

class LLMModel(ABC):

    @abstractmethod
    def run(self):
        pass


