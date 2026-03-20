# src/glm4_handler.py
import time
import asyncio
import logging
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from zhipuai import ZhipuAI

logger = logging.getLogger(__name__)


@dataclass
class RateLimiter:
    max_per_minute: int = 10
    max_per_day: int = 100
    requests_this_minute: List[float] = field(default_factory=list)
    requests_today: List[float] = field(default_factory=list)

    def can_make_request(self) -> bool:
        now = time.time()
        minute_ago = now - 60
        day_ago = now - 86400

        # Clean old requests
        self.requests_this_minute = [t for t in self.requests_this_minute if t > minute_ago]
        self.requests_today = [t for t in self.requests_today if t > day_ago]

        return (
            len(self.requests_this_minute) < self.max_per_minute
            and len(self.requests_today) < self.max_per_day
        )

    def record_request(self):
        now = time.time()
        self.requests_this_minute.append(now)
        self.requests_today.append(now)


class GLM4Handler:
    SYSTEM_PROMPT = """You are a helpful code assistant that answers questions about the MS365_Agents project.
You have access to the project's file structure and relevant code snippets.

When answering:
1. Be concise and accurate
2. Reference specific files when relevant
3. Include code snippets if helpful (use markdown code blocks)
4. If you don't know something, say so clearly"""

    def __init__(
        self,
        api_key: str,
        model: str = "glm-4-flash",
        max_retries: int = 3,
        rate_limit_per_minute: int = 10,
        rate_limit_per_day: int = 100,
    ):
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries
        self.client = ZhipuAI(api_key=api_key)
        self.rate_limiter = RateLimiter(
            max_per_minute=rate_limit_per_minute,
            max_per_day=rate_limit_per_day,
        )

    def query(
        self,
        user_question: str,
        project_context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Send a query to GLM-4 and return the response.

        Args:
            user_question: The user's question
            project_context: Context about the project (file structure, code snippets)
            conversation_history: Optional list of previous messages

        Returns:
            The model's response text

        Raises:
            Exception: If rate limit exceeded or API error after retries
        """
        if not self.rate_limiter.can_make_request():
            raise Exception("Rate limit exceeded. Please try again later.")

        messages = self._build_messages(user_question, project_context, conversation_history)

        last_error = None
        for attempt in range(self.max_retries):
            try:
                self.rate_limiter.record_request()
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                )
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                logger.warning(f"API call failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s, etc.
                    backoff = 2 ** attempt
                    time.sleep(backoff)

        raise Exception(f"Failed after {self.max_retries} retries: {last_error}")

    async def query_async(
        self,
        user_question: str,
        project_context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Async wrapper for query method.

        Args:
            user_question: The user's question
            project_context: Context about the project
            conversation_history: Optional list of previous messages

        Returns:
            The model's response text
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.query,
            user_question,
            project_context,
            conversation_history,
        )

    def _build_messages(
        self,
        user_question: str,
        project_context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> List[Dict[str, str]]:
        """Build the messages list for the API call.

        Args:
            user_question: The user's question
            project_context: Context about the project
            conversation_history: Optional list of previous messages

        Returns:
            List of message dictionaries
        """
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        # Add project context as a system message
        messages.append({
            "role": "system",
            "content": f"Project Context:\n{project_context}"
        })

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add the user's question
        messages.append({"role": "user", "content": user_question})

        return messages
