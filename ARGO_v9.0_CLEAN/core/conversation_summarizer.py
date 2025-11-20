"""
ARGO v9.0 - Conversation Summarizer
Automatically compresses long conversation histories to prevent token limit issues.

Author: ARGO Development Team
Date: 2025-11-19
"""

import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ConversationSummarizer:
    """
    Manages conversation history compression for long conversations.

    Features:
    - Automatic detection when summarization is needed
    - Keeps recent messages for context continuity
    - Generates concise summaries of older messages
    - Prevents token limit errors in LLM calls

    Usage:
        summarizer = ConversationSummarizer(llm, threshold=15)

        if summarizer.needs_summary(len(messages)):
            summary, compressed = summarizer.compress_history(messages, keep_recent=6)
            # Use compressed instead of full history
    """

    def __init__(self, llm, threshold: int = 15, max_summary_tokens: int = 500):
        """
        Initialize conversation summarizer.

        Args:
            llm: Language model instance for generating summaries
            threshold: Number of messages before summarization triggers
            max_summary_tokens: Maximum tokens for summary generation
        """
        self.llm = llm
        self.threshold = threshold
        self.max_summary_tokens = max_summary_tokens
        logger.info(f"ConversationSummarizer initialized with threshold={threshold}")

    def needs_summary(self, message_count: int) -> bool:
        """
        Check if conversation history needs summarization.

        Args:
            message_count: Current number of messages in conversation

        Returns:
            True if summarization is recommended
        """
        needs_it = message_count > self.threshold

        if needs_it:
            logger.info(f"Summarization triggered: {message_count} messages > {self.threshold} threshold")

        return needs_it

    def compress_history(
        self,
        messages: List[Dict[str, str]],
        keep_recent: int = 6
    ) -> Tuple[str, List[Dict[str, str]]]:
        """
        Compress conversation history by summarizing older messages.

        Strategy:
        1. Keep the most recent N messages intact (for immediate context)
        2. Summarize all older messages into a single context block
        3. Return summary + recent messages

        Args:
            messages: Full conversation history [{"role": "user/assistant", "content": "..."}]
            keep_recent: Number of recent messages to keep intact

        Returns:
            Tuple of (summary_text, compressed_messages_list)

        Example:
            Given 20 messages, keep_recent=6:
            - Messages 1-14 → Summarized into single text
            - Messages 15-20 → Kept intact
            - Returns: (summary, [msg15, msg16, ..., msg20])
        """
        if len(messages) <= keep_recent:
            logger.debug(f"No compression needed: {len(messages)} <= {keep_recent}")
            return "", messages

        # Split messages into "old" (to summarize) and "recent" (to keep)
        old_messages = messages[:-keep_recent]
        recent_messages = messages[-keep_recent:]

        logger.info(f"Compressing {len(old_messages)} old messages, keeping {len(recent_messages)} recent")

        # Generate summary of old messages
        summary = self._generate_summary(old_messages)

        # Create compressed history with system message containing summary
        compressed = []

        if summary:
            compressed.append({
                "role": "system",
                "content": f"Previous conversation summary:\n{summary}"
            })

        compressed.extend(recent_messages)

        logger.info(f"Compression complete: {len(messages)} → {len(compressed)} messages")

        return summary, compressed

    def _generate_summary(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate concise summary of message history using LLM.

        Args:
            messages: List of messages to summarize

        Returns:
            Concise summary text
        """
        if not messages:
            return ""

        # Build conversation text for summarization
        conversation_text = self._format_messages_for_summary(messages)

        # Create summarization prompt
        summary_prompt = f"""Summarize the following conversation concisely. Focus on:
- Main topics discussed
- Key questions asked
- Important answers provided
- Any decisions or conclusions

Keep the summary under 200 words and focus on information that would be useful for continuing the conversation.

Conversation:
{conversation_text}

Summary:"""

        try:
            # Generate summary using LLM
            summary_messages = [{"role": "user", "content": summary_prompt}]

            response = self.llm.chat.completions.create(
                model="gpt-4o-mini",  # Use faster/cheaper model for summarization
                messages=summary_messages,
                max_tokens=self.max_summary_tokens,
                temperature=0.3  # Lower temperature for more consistent summaries
            )

            summary = response.choices[0].message.content.strip()

            logger.info(f"Generated summary: {len(summary)} characters")
            return summary

        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            # Fallback: Create basic summary without LLM
            return self._create_fallback_summary(messages)

    def _format_messages_for_summary(self, messages: List[Dict[str, str]]) -> str:
        """
        Format messages into readable text for summarization.

        Args:
            messages: List of message dictionaries

        Returns:
            Formatted conversation text
        """
        lines = []

        for msg in messages:
            role = msg.get('role', 'unknown').upper()
            content = msg.get('content', '').strip()

            if content:
                lines.append(f"{role}: {content}")

        return "\n\n".join(lines)

    def _create_fallback_summary(self, messages: List[Dict[str, str]]) -> str:
        """
        Create basic summary without LLM (fallback method).

        Args:
            messages: List of messages to summarize

        Returns:
            Basic summary text
        """
        user_messages = [m for m in messages if m.get('role') == 'user']
        assistant_messages = [m for m in messages if m.get('role') == 'assistant']

        summary_parts = [
            f"Previous conversation covered {len(user_messages)} user queries",
            f"with {len(assistant_messages)} assistant responses.",
        ]

        # Include first and last user messages if available
        if user_messages:
            first_query = user_messages[0].get('content', '')[:100]
            last_query = user_messages[-1].get('content', '')[:100]

            summary_parts.append(f"Topics included: {first_query}...")
            if len(user_messages) > 1:
                summary_parts.append(f"Most recently discussing: {last_query}...")

        return " ".join(summary_parts)

    def estimate_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Rough estimation of token count for messages.
        Uses approximation: 1 token ≈ 4 characters for English text.

        Args:
            messages: List of messages

        Returns:
            Estimated token count
        """
        total_chars = sum(
            len(msg.get('content', ''))
            for msg in messages
        )

        estimated_tokens = total_chars // 4

        logger.debug(f"Estimated tokens: {estimated_tokens} ({total_chars} chars)")

        return estimated_tokens

    def get_compression_stats(
        self,
        original_messages: List[Dict[str, str]],
        compressed_messages: List[Dict[str, str]]
    ) -> Dict[str, any]:
        """
        Calculate compression statistics.

        Args:
            original_messages: Original message list
            compressed_messages: Compressed message list

        Returns:
            Dictionary with compression statistics
        """
        original_tokens = self.estimate_tokens(original_messages)
        compressed_tokens = self.estimate_tokens(compressed_messages)

        reduction = original_tokens - compressed_tokens
        reduction_pct = (reduction / original_tokens * 100) if original_tokens > 0 else 0

        stats = {
            "original_message_count": len(original_messages),
            "compressed_message_count": len(compressed_messages),
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "tokens_saved": reduction,
            "compression_ratio": reduction_pct,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"Compression stats: {reduction_pct:.1f}% reduction ({reduction} tokens saved)")

        return stats


def main():
    """Test conversation summarizer functionality."""

    # Mock LLM for testing
    class MockLLM:
        class Chat:
            class Completions:
                @staticmethod
                def create(**kwargs):
                    class MockResponse:
                        class Choice:
                            class Message:
                                content = "This is a test summary of the conversation covering various topics."
                        choices = [Choice()]
                    return MockResponse()
            completions = Completions()
        chat = Chat()

    # Create test messages
    test_messages = []
    for i in range(20):
        test_messages.append({
            "role": "user" if i % 2 == 0 else "assistant",
            "content": f"Test message {i+1} with some content to simulate a real conversation."
        })

    # Initialize summarizer
    summarizer = ConversationSummarizer(MockLLM(), threshold=15)

    # Test needs_summary
    print(f"Messages: {len(test_messages)}")
    print(f"Needs summary: {summarizer.needs_summary(len(test_messages))}")

    # Test compression
    summary, compressed = summarizer.compress_history(test_messages, keep_recent=6)

    print(f"\nOriginal messages: {len(test_messages)}")
    print(f"Compressed messages: {len(compressed)}")
    print(f"\nSummary:\n{summary}")

    # Test statistics
    stats = summarizer.get_compression_stats(test_messages, compressed)
    print(f"\nCompression Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
