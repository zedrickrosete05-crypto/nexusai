"""AI service layer abstracting LLM provider calls.

Provides a single, provider-agnostic interface for generating
completions. Supports OpenAI and Ollama, selected via the
AI_PROVIDER setting, so calling code never depends on a specific SDK.
"""

from typing import AsyncGenerator, List

import httpx
from openai import AsyncOpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.exceptions import AIServiceException
from app.core.logging import get_logger
from app.schemas.chat import ChatMessage, CompletionRequest, CompletionResponse

logger = get_logger(__name__)


class AIService:
    """Provider-agnostic service for LLM text generation.

    Selects between OpenAI and Ollama based on settings.AI_PROVIDER.
    The public methods (generate, stream) define a stable contract
    regardless of which provider is active.
    """

    def __init__(self) -> None:
        """Initialize the AI service with the configured provider's client."""
        self.provider = settings.AI_PROVIDER
        if self.provider == "openai":
            self._openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self._default_model = settings.OPENAI_MODEL
        else:
            self._ollama_base_url = settings.OLLAMA_BASE_URL
            self._default_model = settings.OLLAMA_MODEL

    @retry(
        retry=retry_if_exception_type(AIServiceException),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    async def generate(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a single, non-streamed completion from the configured provider.

        Args:
            request: The completion request containing messages and params.

        Returns:
            A CompletionResponse with the generated text and token usage.

        Raises:
            AIServiceException: If the provider call fails after retries.
        """
        if self.provider == "openai":
            return await self._generate_openai(request)
        return await self._generate_ollama(request)

    async def stream(self, request: CompletionRequest) -> AsyncGenerator[str, None]:
        """Stream a completion from the configured provider, yielding text chunks.

        Args:
            request: The completion request containing messages and params.

        Yields:
            Successive text chunks of the model's response as they arrive.

        Raises:
            AIServiceException: If the provider stream fails.
        """
        if self.provider == "openai":
            async for chunk in self._stream_openai(request):
                yield chunk
        else:
            async for chunk in self._stream_ollama(request):
                yield chunk

    # === OpenAI implementation ===

    async def _generate_openai(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a completion using the OpenAI provider."""
        model = request.model or self._default_model
        try:
            response = await self._openai_client.chat.completions.create(
                model=model,
                messages=self._to_openai_messages(request.messages),
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
        except Exception as exc:
            logger.error("ai_generate_failed", provider="openai", error=str(exc))
            raise AIServiceException(provider="openai", original_error=str(exc)) from exc

        choice = response.choices[0]
        usage = response.usage
        logger.info(
            "ai_generate_succeeded", provider="openai", model=model,
            total_tokens=usage.total_tokens if usage else 0,
        )
        return CompletionResponse(
            content=choice.message.content or "",
            model=response.model,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
        )

    async def _stream_openai(self, request: CompletionRequest) -> AsyncGenerator[str, None]:
        """Stream a completion using the OpenAI provider."""
        model = request.model or self._default_model
        try:
            stream = await self._openai_client.chat.completions.create(
                model=model,
                messages=self._to_openai_messages(request.messages),
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as exc:
            logger.error("ai_stream_failed", provider="openai", error=str(exc))
            raise AIServiceException(provider="openai", original_error=str(exc)) from exc

    @staticmethod
    def _to_openai_messages(messages: List[ChatMessage]) -> List[dict]:
        """Convert internal ChatMessage objects into OpenAI's expected dict format."""
        return [{"role": m.role, "content": m.content} for m in messages]

    # === Ollama implementation ===

    async def _generate_ollama(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a completion using the local Ollama provider."""
        model = request.model or self._default_model
        payload = {
            "model": model,
            "messages": self._to_openai_messages(request.messages),
            "stream": False,
            "options": {"temperature": request.temperature},
        }
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self._ollama_base_url}/api/chat", json=payload
                )
                response.raise_for_status()
                data = response.json()
        except Exception as exc:
            logger.error("ai_generate_failed", provider="ollama", error=str(exc))
            raise AIServiceException(provider="ollama", original_error=str(exc)) from exc

        content = data.get("message", {}).get("content", "")
        logger.info("ai_generate_succeeded", provider="ollama", model=model)
        return CompletionResponse(content=content, model=model)

    async def _stream_ollama(self, request: CompletionRequest) -> AsyncGenerator[str, None]:
        """Stream a completion using the local Ollama provider."""
        model = request.model or self._default_model
        payload = {
            "model": model,
            "messages": self._to_openai_messages(request.messages),
            "stream": True,
            "options": {"temperature": request.temperature},
        }
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST", f"{self._ollama_base_url}/api/chat", json=payload
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        import json

                        chunk = json.loads(line)
                        delta = chunk.get("message", {}).get("content", "")
                        if delta:
                            yield delta
        except Exception as exc:
            logger.error("ai_stream_failed", provider="ollama", error=str(exc))
            raise AIServiceException(provider="ollama", original_error=str(exc)) from exc