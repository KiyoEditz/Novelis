"""OpenAI-Compatible LLM Adapter (Secondary / Alternative Provider)
Supports OpenRouter, Groq, DeepSeek, and local Ollama instances.
"""

from typing import Optional
from novelis.config import config
from novelis.llm.base import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    """Client for any OpenAI-compatible chat completion endpoint."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or config.OPENAI_API_KEY
        self.base_url = base_url or config.OPENAI_BASE_URL
        self.model_name = model or config.OPENAI_MODEL
        self._client = None
        self._init_client()

    def _init_client(self) -> None:
        """Initializes openai.OpenAI client."""
        if not self.api_key:
            return
        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        except ImportError:
            self._client = None

    def generate(
        self,
        system_instruction: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> str:
        """Executes chat completion request."""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set.")
        if self._client is None:
            raise RuntimeError("The 'openai' library is not installed. Run: pip install openai")

        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content or ""
