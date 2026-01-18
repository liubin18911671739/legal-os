from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseLLM(ABC):
    """Base class for language models"""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        """Generate text from a prompt

        Args:
            prompt: Input prompt
            **kwargs: Additional model-specific parameters

        Returns:
            Generated text
        """
        pass

    @abstractmethod
    async def generate_with_messages(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Generate text from a list of messages

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional model-specific parameters

        Returns:
            Generated text
        """
        pass

    @abstractmethod
    async def stream_generate(
        self,
        prompt: str,
        **kwargs
    ):
        """Stream generated text

        Args:
            prompt: Input prompt
            **kwargs: Additional model-specific parameters

        Yields:
            Chunks of generated text
        """
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the name of the model"""
        pass
