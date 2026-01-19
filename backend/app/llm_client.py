"""
ZhipuAI Client wrapper for multi-agent system

This module provides a centralized client for all agents to interact
with ZhipuAI API, with token counting and cost tracking.
"""

import os
import logging
import httpx
import json
from typing import Dict, Any, List, Optional, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """Token usage tracking"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    def add(self, prompt: int, completion: int) -> None:
        """Add tokens to usage"""
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        self.total_tokens += prompt + completion


@dataclass
class CostTracker:
    """Cost tracking for different models"""
    # Pricing per 1K tokens (example prices, update with actual ZhipuAI pricing)
    MODEL_PRICING = {
        "glm-4": {"input": 0.05, "output": 0.05},  # RMB per 1K tokens
        "glm-4-flash": {"input": 0.01, "output": 0.01},
        "glm-4-0520": {"input": 0.04, "output": 0.04},
        "glm-3-turbo": {"input": 0.005, "output": 0.005},
    }
    
    total_cost: float = 0.0
    model_costs: Dict[str, float] = field(default_factory=dict)
    usage_by_agent: Dict[str, TokenUsage] = field(default_factory=dict)
    
    def add_usage(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        agent: str,
    ) -> float:
        """Add usage and calculate cost
        
        Args:
            model: Model name
            prompt_tokens: Input token count
            completion_tokens: Output token count
            agent: Agent name
        
        Returns:
            Cost in RMB
        """
        if model not in self.MODEL_PRICING:
            logger.warning(f"Unknown model {model}, using default pricing")
            pricing = {"input": 0.01, "output": 0.01}
        else:
            pricing = self.MODEL_PRICING[model]
        
        input_cost = (prompt_tokens / 1000) * pricing["input"]
        output_cost = (completion_tokens / 1000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        self.total_cost += total_cost
        self.model_costs[model] = self.model_costs.get(model, 0.0) + total_cost
        
        if agent not in self.usage_by_agent:
            self.usage_by_agent[agent] = TokenUsage()
        self.usage_by_agent[agent].add(prompt_tokens, completion_tokens)
        
        logger.info(
            f"{agent} used {model}: "
            f"{prompt_tokens} input + {completion_tokens} output tokens = ¥{total_cost:.4f}"
        )
        
        return total_cost
    
    def get_summary(self) -> Dict[str, Any]:
        """Get cost summary
        
        Returns:
            Dictionary with cost breakdown
        """
        return {
            "total_cost": self.total_cost,
            "model_costs": self.model_costs,
            "usage_by_agent": {
                agent: {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                }
                for agent, usage in self.usage_by_agent.items()
            },
        }


class ZhipuAIClient:
    """Centralized ZhipuAI client for multi-agent system"""
    
    # Agent-specific model configurations
    AGENT_MODELS = {
        "coordinator": {
            "model": "glm-4",
            "temperature": 0.3,
            "max_tokens": 1024,
        },
        "retrieval": {
            "model": "glm-4-flash",
            "temperature": 0.5,
            "max_tokens": 512,
        },
        "analysis": {
            "model": "glm-4",
            "temperature": 0.2,
            "max_tokens": 2048,
        },
        "review": {
            "model": "glm-4",
            "temperature": 0.2,
            "max_tokens": 2048,
        },
        "validation": {
            "model": "glm-4",
            "temperature": 0.3,
            "max_tokens": 1024,
        },
        "report": {
            "model": "glm-4",
            "temperature": 0.4,
            "max_tokens": 4096,
        },
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://open.bigmodel.cn/api/paas/v4",
        timeout: int = 60,
        enable_tracking: bool = True,
    ):
        """Initialize ZhipuAI client
        
        Args:
            api_key: ZhipuAI API key (defaults to env var ZHIPUAI_API_KEY)
            base_url: API base URL
            timeout: Request timeout
            enable_tracking: Enable cost and token tracking
        """
        self.api_key = api_key or os.getenv("ZHIPUAI_API_KEY")
        if not self.api_key:
            logger.warning("ZHIPUAI_API_KEY not set, using mock mode")
            self.mock_mode = True
        else:
            self.mock_mode = False
        
        self.base_url = base_url
        self.timeout = timeout
        self.enable_tracking = enable_tracking
        
        # HTTP client
        self.client = httpx.AsyncClient(timeout=timeout)
        
        # Cost tracking
        self.cost_tracker = CostTracker() if enable_tracking else None
        
        logger.info(f"ZhipuAIClient initialized (mock_mode={self.mock_mode})")
    
    async def _make_request(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
        **kwargs
    ) -> str:
        """Make API request to ZhipuAI
        
        Args:
            model: Model name
            messages: List of messages
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            stream: Whether to stream response
            **kwargs: Additional parameters
        
        Returns:
            Generated text
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            **kwargs,
        }
        
        response = await self.client.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
        )
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    async def generate(
        self,
        agent: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text for an agent
        
        Args:
            agent: Agent name (coordinator, retrieval, etc.)
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters
        
        Returns:
            Generated text
        """
        if agent not in self.AGENT_MODELS:
            logger.warning(f"Unknown agent {agent}, using default config")
            config = {"model": "glm-4", "temperature": 0.7, "max_tokens": 2048}
        else:
            config = self.AGENT_MODELS[agent]
        
        # Override with provided kwargs
        temperature = kwargs.get("temperature", config["temperature"])
        max_tokens = kwargs.get("max_tokens", config["max_tokens"])
        model = kwargs.get("model", config["model"])
        
        if self.mock_mode:
            logger.warning(f"Mock mode enabled for {agent}, returning simulated response")
            # Check if this is being called for JSON (look at context)
            # For simplicity, return JSON that also works for text
            return '{"mock": true}'
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Estimate tokens
        prompt_tokens = sum(len(msg.get("content", "")) // 2 for msg in messages)
        
        try:
            result = await self._make_request(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            completion_tokens = len(result) // 2
            
            # Track cost
            if self.enable_tracking and self.cost_tracker:
                self.cost_tracker.add_usage(
                    model=model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    agent=agent,
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate for {agent}: {e}", exc_info=True)
            raise
    
    async def generate_json(
        self,
        agent: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate JSON response for an agent
        
        Args:
            agent: Agent name
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters
        
        Returns:
            Parsed JSON response
        """
        # Add JSON format instruction to prompt
        json_instruction = "\n\n请以 JSON 格式返回你的回答，不要包含其他文本。"
        full_prompt = prompt + json_instruction
        
        response = await self.generate(
            agent=agent,
            prompt=full_prompt,
            system_prompt=system_prompt,
            **kwargs,
        )
        
        try:
            # Parse JSON
            # Handle markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from {agent}: {e}")
            logger.error(f"Response: {response[:500]}...")
            raise ValueError(f"Invalid JSON response from {agent}: {e}")
    
    async def stream_generate(
        self,
        agent: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream text generation for an agent
        
        Args:
            agent: Agent name
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters
        
        Yields:
            Generated text chunks
        """
        if agent not in self.AGENT_MODELS:
            config = {"model": "glm-4", "temperature": 0.7, "max_tokens": 2048}
        else:
            config = self.AGENT_MODELS[agent]
        
        temperature = kwargs.get("temperature", config["temperature"])
        max_tokens = kwargs.get("max_tokens", config["max_tokens"])
        model = kwargs.get("model", config["model"])
        
        if self.mock_mode:
            yield f"[MOCK STREAM from {agent}]"
            return
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
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
                
        except Exception as e:
            logger.error(f"Failed to stream generate for {agent}: {e}", exc_info=True)
            raise
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost and usage summary
        
        Returns:
            Dictionary with cost breakdown
        """
        if not self.cost_tracker:
            return {"error": "Cost tracking disabled"}
        
        return self.cost_tracker.get_summary()
    
    async def close(self) -> None:
        """Close HTTP client"""
        await self.client.aclose()
        logger.info("ZhipuAIClient closed")


# Global client instance
_client_instance: Optional[ZhipuAIClient] = None


def get_client() -> ZhipuAIClient:
    """Get or create global ZhipuAI client instance
    
    Returns:
        ZhipuAIClient instance
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = ZhipuAIClient()
    return _client_instance


async def close_client() -> None:
    """Close global ZhipuAI client instance"""
    global _client_instance
    if _client_instance is not None:
        await _client_instance.close()
        _client_instance = None
