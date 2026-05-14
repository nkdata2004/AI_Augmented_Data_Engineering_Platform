from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract LLM provider so real providers can replace the mock provider."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError
