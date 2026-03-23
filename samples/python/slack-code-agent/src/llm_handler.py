# src/llm_handler.py
import os
import time
import logging
import requests
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    text: str
    tokens_used: int
    success: bool
    error: Optional[str] = None

class LLMHandler:
    """Handler for MiniMax2.7 API calls."""

    SYSTEM_PROMPT = """You are a helpful code and document assistant that answers questions about the configured project.
You have access to the project's file structure, code files, and optionally document data stored in KuzuDB.

When answering:
1. Be concise and accurate
2. Reference specific files or documents when relevant
3. Include code snippets if helpful
4. If you don't know, say so
"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY", "")
        self.base_url = base_url or os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat")
        self.model = "MiniMax-Text-01"
        self.max_retries = 3
        self.rate_limit_per_minute = 20
        self._last_request_time = 0

    def build_messages(self, user_query: str, context: str = "", document_context: str = "") -> List[Dict[str, str]]:
        """Build messages list for API call."""
        system_content = self.SYSTEM_PROMPT

        if context:
            system_content += f"\n\nProject context:\n{context}"

        if document_context:
            system_content += f"\n\nDocument context (from KuzuDB):\n{document_context}"

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_query}
        ]

        return messages

    def generate(self, user_query: str, context: str = "", document_context: str = "") -> LLMResponse:
        """Generate response from MiniMax2.7 API."""
        if not self.api_key:
            return LLMResponse(
                text="AI service not configured. Please set MINIMAX_API_KEY.",
                tokens_used=0,
                success=False,
                error="Missing API key"
            )

        messages = self.build_messages(user_query, context, document_context)

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/v1/text/chatcompletion_pro",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    choices = data.get("choices", [])
                    if choices and len(choices) > 0:
                        choice = choices[0]
                        if isinstance(choice, dict) and "messages" in choice:
                            for msg in choice["messages"]:
                                if msg.get("role") == "assistant":
                                    return LLMResponse(
                                        text=msg.get("content", ""),
                                        tokens_used=data.get("usage", {}).get("total_tokens", 0),
                                        success=True
                                    )
                        if isinstance(choice, dict) and "text" in choice:
                            return LLMResponse(
                                text=choice["text"],
                                tokens_used=data.get("usage", {}).get("total_tokens", 0),
                                success=True
                            )
                    return LLMResponse(
                        text=data.get("choices", [{}])[0].get("text", "No response"),
                        tokens_used=data.get("usage", {}).get("total_tokens", 0),
                        success=True
                    )
                elif response.status_code == 429:
                    logger.warning("Rate limited, retrying...")
                    time.sleep(2 ** attempt)
                    continue
                else:
                    return LLMResponse(
                        text=f"API error: {response.status_code}",
                        tokens_used=0,
                        success=False,
                        error=f"HTTP {response.status_code}"
                    )

            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Request timeout, retry {attempt + 1}/{self.max_retries}")
                    time.sleep(2 ** attempt)
                    continue
                return LLMResponse(
                    text="Request timed out. Please try again.",
                    tokens_used=0,
                    success=False,
                    error="Timeout"
                )
            except Exception as e:
                logger.error(f"Error calling MiniMax API: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return LLMResponse(
                    text=f"Error: {str(e)}",
                    tokens_used=0,
                    success=False,
                    error=str(e)
                )

        return LLMResponse(
            text="Max retries exceeded. Please try again.",
            tokens_used=0,
            success=False,
            error="Max retries"
        )