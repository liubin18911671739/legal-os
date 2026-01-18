from typing import List, Dict, Any, AsyncIterator, Optional
from openai import AsyncOpenAI
from .base import BaseLLM


class OpenAILLM(BaseLLM):
    """OpenAI GPT model implementation"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ):
        """Initialize OpenAI LLM

        Args:
            api_key: OpenAI API key
            model: Model name (gpt-4o-mini, gpt-4o, etc.)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens

    async def generate(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        """Generate text from a prompt

        Args:
            prompt: Input prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Generated text
        """
        params = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", self._temperature),
        }

        if self._max_tokens is not None:
            params["max_tokens"] = kwargs.get("max_tokens", self._max_tokens)

        response = await self.client.chat.completions.create(**params)
        return response.choices[0].message.content

    async def generate_with_messages(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Generate text from a list of messages

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        params = {
            "model": self._model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self._temperature),
        }

        if self._max_tokens is not None:
            params["max_tokens"] = kwargs.get("max_tokens", self._max_tokens)

        response = await self.client.chat.completions.create(**params)
        return response.choices[0].message.content

    async def stream_generate(
        self,
        prompt: str,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream generated text

        Args:
            prompt: Input prompt
            **kwargs: Additional parameters

        Yields:
            Chunks of generated text
        """
        params = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", self._temperature),
            "stream": True,
        }

        if self._max_tokens is not None:
            params["max_tokens"] = kwargs.get("max_tokens", self._max_tokens)

        stream = await self.client.chat.completions.create(**params)
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    @property
    def model_name(self) -> str:
        """Return name of model"""
        return self._model
