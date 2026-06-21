"""Chat business logic service.

Orchestrates conversation management and message exchange, coordinating
ConversationRepository, MessageRepository, AIService, and the RAG
pipeline. Contains no direct database queries or HTTP-specific logic.
"""

import uuid
from typing import AsyncGenerator, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConversationNotFoundException
from app.core.logging import get_logger
from app.models.conversation import Conversation
from app.models.message import Message
from app.rag.retriever import build_rag_prompt, retrieve_context
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.chat import ChatMessage, CompletionRequest
from app.services.ai_service import AIService
from app.services.vector_service import VectorService

logger = get_logger(__name__)

SYSTEM_PROMPT = (
    "You are NexusAI, a helpful and concise AI research and coding assistant."
)


class ChatService:
    """Service handling conversation and message orchestration logic."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the chat service with a database session.

        Args:
            session: The active async database session.
        """
        self.session = session
        self.conversation_repository = ConversationRepository(session)
        self.message_repository = MessageRepository(session)
        self.ai_service = AIService()
        self.vector_service = VectorService()

    async def create_conversation(
        self, *, user_id: uuid.UUID, title: str = "New Conversation"
    ) -> Conversation:
        """Create a new conversation for a user.

        Args:
            user_id: The owning user's id.
            title: An initial display title.

        Returns:
            The newly created Conversation instance.
        """
        conversation = await self.conversation_repository.create(user_id=user_id, title=title)
        logger.info(
            "conversation_created", conversation_id=str(conversation.id), user_id=str(user_id)
        )
        return conversation

    async def list_conversations(self, *, user_id: uuid.UUID) -> List[Conversation]:
        """List all conversations belonging to a user.

        Args:
            user_id: The owning user's id.

        Returns:
            A list of the user's conversations, most recent first.
        """
        return await self.conversation_repository.list_for_user(user_id)

    async def get_conversation(
        self, *, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> Conversation:
        """Fetch a single conversation with its full message history.

        Args:
            conversation_id: The conversation's id.
            user_id: The requesting user's id, to enforce ownership.

        Returns:
            The matching Conversation with messages loaded.

        Raises:
            ConversationNotFoundException: If not found or not owned by this user.
        """
        conversation = await self.conversation_repository.get_by_id_for_user(
            conversation_id, user_id
        )
        if conversation is None:
            raise ConversationNotFoundException(conversation_id=str(conversation_id))
        await self.session.refresh(conversation, attribute_names=["messages"])
        return conversation

    async def send_message(
        self, *, conversation_id: uuid.UUID, user_id: uuid.UUID, content: str
    ) -> Message:
        """Send a user message and generate a non-streamed AI response.

        Args:
            conversation_id: The conversation to send the message in.
            user_id: The requesting user's id, to enforce ownership.
            content: The user's message text.

        Returns:
            The newly created assistant Message instance.

        Raises:
            ConversationNotFoundException: If not found or not owned by this user.
        """
        conversation = await self.get_conversation(
            conversation_id=conversation_id, user_id=user_id
        )

        await self.message_repository.create(
            conversation_id=conversation.id, role="user", content=content
        )

        history = self._build_history(
            conversation, new_user_content=content, user_id=user_id
        )
        response = await self.ai_service.generate(CompletionRequest(messages=history))

        assistant_message = await self.message_repository.create(
            conversation_id=conversation.id,
            role="assistant",
            content=response.content,
            total_tokens=response.total_tokens,
        )

        logger.info(
            "message_exchanged",
            conversation_id=str(conversation.id),
            total_tokens=response.total_tokens,
        )
        return assistant_message

    async def stream_message(
        self, *, conversation_id: uuid.UUID, user_id: uuid.UUID, content: str
    ) -> AsyncGenerator[str, None]:
        """Send a user message and stream the AI response token-by-token.

        Persists the user message immediately, streams the AI response
        to the caller, then persists the complete assistant message
        once streaming finishes.

        Args:
            conversation_id: The conversation to send the message in.
            user_id: The requesting user's id, to enforce ownership.
            content: The user's message text.

        Yields:
            Successive text chunks of the AI's response.

        Raises:
            ConversationNotFoundException: If not found or not owned by this user.
        """
        conversation = await self.get_conversation(
            conversation_id=conversation_id, user_id=user_id
        )

        await self.message_repository.create(
            conversation_id=conversation.id, role="user", content=content
        )
        await self.session.commit()

        history = self._build_history(
            conversation, new_user_content=content, user_id=user_id
        )
        full_response = ""

        async for chunk in self.ai_service.stream(CompletionRequest(messages=history)):
            full_response += chunk
            yield chunk

        await self.message_repository.create(
            conversation_id=conversation.id, role="assistant", content=full_response
        )
        await self.session.commit()

        logger.info("message_streamed", conversation_id=str(conversation.id))

    def _build_history(
        self, conversation: Conversation, *, new_user_content: str, user_id: uuid.UUID
    ) -> List[ChatMessage]:
        """Build the full message history to send to the LLM, augmented with RAG.

        If the user has relevant uploaded documents, retrieves the most
        relevant chunks and grounds the final user message in them with
        citation instructions.

        Args:
            conversation: The conversation containing prior messages.
            new_user_content: The newest user message, not yet persisted
                in conversation.messages at call time.
            user_id: The owning user's id, to scope document retrieval.

        Returns:
            A list of ChatMessage objects, system prompt first, followed
            by prior history, ending with the (possibly RAG-augmented)
            new user message.
        """
        history = [ChatMessage(role="system", content=SYSTEM_PROMPT)]
        for msg in conversation.messages:
            history.append(ChatMessage(role=msg.role, content=msg.content))

        context = retrieve_context(
            query=new_user_content, user_id=user_id, vector_service=self.vector_service
        )
        augmented_content = build_rag_prompt(query=new_user_content, context=context)
        history.append(ChatMessage(role="user", content=augmented_content))
        return history