"""Quick manual test for AIService against the real OpenAI API."""

import asyncio

from app.schemas.chat import ChatMessage, CompletionRequest
from app.services.ai_service import AIService


async def main() -> None:
    """Test both generate() and stream() against the real OpenAI API."""
    service = AIService()

    request = CompletionRequest(
        messages=[
            ChatMessage(role="system", content="You are a concise assistant."),
            ChatMessage(role="user", content="Say hello in exactly 5 words."),
        ],
        max_tokens=30,
    )

    print("=== Testing generate() ===")
    response = await service.generate(request)
    print(f"Content: {response.content}")
    print(f"Model: {response.model}")
    print(f"Tokens used: {response.total_tokens}")

    print("\n=== Testing stream() ===")
    print("Streamed output: ", end="", flush=True)
    async for chunk in service.stream(request):
        print(chunk, end="", flush=True)
    print()

    print("\n=== AI Service tests passed! ===")


if __name__ == "__main__":
    asyncio.run(main())