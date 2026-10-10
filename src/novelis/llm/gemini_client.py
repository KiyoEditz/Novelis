"""Google Gemini LLM Adapter (Default Provider)
Supports Gemini 3.8 (gemini-3.8-flash / gemini-3.8-pro) via official SDK.
"""

from typing import Optional
from novelis.config import config
from novelis.llm.base import BaseLLMClient


class GeminiClient(BaseLLMClient):
    """Google Gemini API client optimized for long narrative context windows."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model_name = model or config.GEMINI_MODEL

        # Client setup
        self._genai_client = None
        self._init_client()

    def _init_client(self) -> None:
        """Initializes Gemini client using google.genai or google.generativeai."""
        if not self.api_key:
            return

        try:
            # Modern Google GenAI SDK
            from google import genai
            self._genai_client = genai.Client(api_key=self.api_key)
            self._mode = "genai"
        except ImportError:
            try:
                # Alternative google.generativeai SDK
                import google.generativeai as legacy_genai
                legacy_genai.configure(api_key=self.api_key)
                self._genai_client = legacy_genai
                self._mode = "legacy"
            except ImportError:
                self._genai_client = None
                self._mode = None

    def generate(
        self,
        system_instruction: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> str:
        """Executes text generation on Gemini 3.8."""
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. Please set it in your .env file or pass it to GeminiClient."
            )

        if self._genai_client is None:
            raise RuntimeError(
                "Neither 'google-genai' nor 'google-generativeai' is installed. "
                "Run: pip install google-genai"
            )

        if self._mode == "genai":
            response = self._genai_client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "system_instruction": system_instruction,
                    "temperature": temperature,
                    "max_output_tokens": max_tokens
                }
            )
            return response.text or ""

        elif self._mode == "legacy":
            model = self._genai_client.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction
            )
            response = model.generate_content(
                prompt,
                generation_config=self._genai_client.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            return response.text or ""

        return ""
