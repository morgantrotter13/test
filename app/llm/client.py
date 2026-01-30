"""
LLM client wrapper for OpenAI chat completions.
"""
from typing import Optional
from openai import OpenAI
from app.config import settings


class LLMClient:
    """Simple wrapper around OpenAI Chat Completions."""

    def __init__(
        self,
        api_key: Optional[str],
        model: str,
        temperature: float,
        max_tokens: int,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = OpenAI(api_key=api_key) if api_key else None

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: float = 30.0,
    ) -> str:
        if not self._client:
            raise ValueError("LLM API key not configured. Set OPENAI_API_KEY.")

        response = self._client.chat.completions.create(
            model=model or self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens if max_tokens is not None else self.max_tokens,
            timeout=timeout,
        )
        return response.choices[0].message.content


llm_client = LLMClient(
    api_key=settings.OPENAI_API_KEY,
    model=settings.OPENAI_MODEL,
    temperature=settings.OPENAI_TEMPERATURE,
    max_tokens=settings.OPENAI_MAX_TOKENS,
)
