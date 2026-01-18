from typing import List, Dict, Any, AsyncIterator, Optional
import logging
import httpx
import json

logger = logging.getLogger(__name__)


class ZhipuLLM:
    """ZhipuAI GLM language model implementation"""

    def __init__(
        self,
        api_key: str,
        model: str = "glm-4",
        base_url: str = "https://open.bigmodel.cn/api/paas/v4",
        timeout: int = 60,
    ):
        """Initialize ZhipuAI LLM

        Args:
            api_key: ZhipuAI API key
            model: Model name (glm-4, glm-4-flash, glm-4-0520, etc.)
            base_url: API base URL
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = timeout

        self.client = httpx.AsyncClient(timeout=timeout)
        logger.info(f"ZhipuAI LLM initialized: {model}")

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """Generate text from prompt

        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            logger.error(f"ZhipuAI API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Failed to generate text: {e}")
            raise

    async def generate_with_messages(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """Generate text from message list

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            logger.error(f"ZhipuAI API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Failed to generate text: {e}")
            raise

    async def stream_generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate text with streaming

        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Yields:
            Generated text chunks
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
            **kwargs,
        }

        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    
                    data_str = line[6:]  # Remove "data: " prefix
                    
                    if data_str == "[DONE]":
                        break
                    
                    try:
                        data_json = json.loads(data_str)
                        if "choices" in data_json and len(data_json["choices"]) > 0:
                            delta = data_json["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue

        except httpx.HTTPStatusError as e:
            logger.error(f"ZhipuAI API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Failed to stream generate: {e}")
            raise

    async def count_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        # Rough estimation: ~2 characters per token for Chinese
        return len(text) // 2

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information

        Returns:
            Dictionary with model details
        """
        return {
            "model": self.model,
            "base_url": self.base_url,
            "timeout": self.timeout,
        }

    async def close(self) -> None:
        """Close HTTP client"""
        await self.client.aclose()
