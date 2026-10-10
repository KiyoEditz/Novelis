"""Abstract Base Class for Novelis LLM Adapters.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseLLMClient(ABC):
    """Abstract interface defining standard generation contracts."""

    @abstractmethod
    def generate(
        self,
        system_instruction: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> str:
        """Generates natural language prose or analysis from prompts."""
        pass
