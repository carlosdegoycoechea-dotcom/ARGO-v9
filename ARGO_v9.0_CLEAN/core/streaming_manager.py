"""
ARGO v9.0 - Streaming Manager
Manages real-time streaming responses from LLMs for better UX.

Author: ARGO Development Team
Date: 2025-11-19
"""

import logging
from typing import Generator, Callable, Optional, Dict, Any, List
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


@dataclass
class StreamChunk:
    """Represents a chunk of streamed content"""
    content: str
    role: str = "assistant"
    finish_reason: Optional[str] = None
    model: Optional[str] = None
    usage: Optional[Dict[str, int]] = None


class StreamingManager:
    """
    Manages streaming responses from OpenAI and Anthropic models.

    Features:
    - Real-time word-by-word display
    - Progress callbacks for UI updates
    - Error handling during streaming
    - Support for both OpenAI and Anthropic APIs
    - Token usage tracking

    Usage:
        streaming_manager = StreamingManager()

        # Stream from OpenAI
        for chunk in streaming_manager.stream_openai(client, messages, model):
            print(chunk.content, end='', flush=True)

        # Stream from Anthropic
        for chunk in streaming_manager.stream_anthropic(client, messages, model):
            print(chunk.content, end='', flush=True)
    """

    def __init__(self, chunk_size: int = 1):
        """
        Initialize streaming manager.

        Args:
            chunk_size: Number of tokens per chunk (1 = word-by-word)
        """
        self.chunk_size = chunk_size
        self.current_stream = None
        self.total_tokens = 0
        logger.info(f"StreamingManager initialized with chunk_size={chunk_size}")

    def stream_openai(
        self,
        client,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Generator[StreamChunk, None, None]:
        """
        Stream response from OpenAI API.

        Args:
            client: OpenAI client instance
            messages: List of message dictionaries
            model: Model name (default: gpt-4o)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters for API call

        Yields:
            StreamChunk objects with incremental content

        Example:
            for chunk in streaming_manager.stream_openai(client, messages):
                display_text(chunk.content)
                full_response += chunk.content
        """
        try:
            logger.info(f"Starting OpenAI stream with model={model}")

            # Create streaming request
            stream_params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": True,
                **kwargs
            }

            if max_tokens:
                stream_params["max_tokens"] = max_tokens

            # Start streaming
            response = client.chat.completions.create(**stream_params)
            self.current_stream = response

            full_content = ""
            chunk_count = 0

            # Process stream
            for chunk in response:
                chunk_count += 1

                # Extract content from chunk
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    finish_reason = chunk.choices[0].finish_reason

                    content = delta.content if hasattr(delta, 'content') and delta.content else ""

                    if content:
                        full_content += content

                        yield StreamChunk(
                            content=content,
                            role="assistant",
                            finish_reason=finish_reason,
                            model=model
                        )

                    # Check if stream is complete
                    if finish_reason:
                        logger.info(f"OpenAI stream complete: {chunk_count} chunks, {len(full_content)} chars")

                        # Try to get usage info from last chunk
                        usage = chunk.usage if hasattr(chunk, 'usage') else None
                        if usage:
                            usage_dict = {
                                "prompt_tokens": usage.prompt_tokens,
                                "completion_tokens": usage.completion_tokens,
                                "total_tokens": usage.total_tokens
                            }
                            self.total_tokens = usage.total_tokens

                            yield StreamChunk(
                                content="",
                                finish_reason=finish_reason,
                                model=model,
                                usage=usage_dict
                            )
                        break

            logger.info(f"OpenAI streaming completed successfully")

        except Exception as e:
            logger.error(f"OpenAI streaming error: {str(e)}", exc_info=True)
            yield StreamChunk(
                content=f"\n\n[Streaming error: {str(e)}]",
                finish_reason="error"
            )

    def stream_anthropic(
        self,
        client,
        messages: List[Dict[str, str]],
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system: Optional[str] = None,
        **kwargs
    ) -> Generator[StreamChunk, None, None]:
        """
        Stream response from Anthropic API.

        Args:
            client: Anthropic client instance
            messages: List of message dictionaries (without system message)
            model: Model name (default: claude-3-5-sonnet)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate (required by Anthropic)
            system: System prompt (separate from messages)
            **kwargs: Additional parameters for API call

        Yields:
            StreamChunk objects with incremental content

        Example:
            for chunk in streaming_manager.stream_anthropic(client, messages, system="You are helpful"):
                display_text(chunk.content)
        """
        try:
            logger.info(f"Starting Anthropic stream with model={model}")

            # Prepare messages (filter out system messages as Anthropic handles them separately)
            filtered_messages = [
                msg for msg in messages
                if msg.get('role') != 'system'
            ]

            # Extract system message if not provided
            if not system:
                system_messages = [msg for msg in messages if msg.get('role') == 'system']
                if system_messages:
                    system = system_messages[0].get('content', '')

            # Create streaming request
            stream_params = {
                "model": model,
                "messages": filtered_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
                **kwargs
            }

            if system:
                stream_params["system"] = system

            # Start streaming
            full_content = ""
            chunk_count = 0

            with client.messages.stream(**stream_params) as stream:
                self.current_stream = stream

                for text in stream.text_stream:
                    chunk_count += 1
                    full_content += text

                    yield StreamChunk(
                        content=text,
                        role="assistant",
                        model=model
                    )

                # Get final message for usage info
                final_message = stream.get_final_message()

                if final_message:
                    usage_dict = {
                        "prompt_tokens": final_message.usage.input_tokens,
                        "completion_tokens": final_message.usage.output_tokens,
                        "total_tokens": final_message.usage.input_tokens + final_message.usage.output_tokens
                    }
                    self.total_tokens = usage_dict["total_tokens"]

                    yield StreamChunk(
                        content="",
                        finish_reason=final_message.stop_reason,
                        model=model,
                        usage=usage_dict
                    )

            logger.info(f"Anthropic stream complete: {chunk_count} chunks, {len(full_content)} chars")

        except Exception as e:
            logger.error(f"Anthropic streaming error: {str(e)}", exc_info=True)
            yield StreamChunk(
                content=f"\n\n[Streaming error: {str(e)}]",
                finish_reason="error"
            )

    def stream_with_callback(
        self,
        stream_generator: Generator[StreamChunk, None, None],
        callback: Callable[[str], None],
        delay: float = 0.01
    ) -> str:
        """
        Stream content with callback function for UI updates.

        Args:
            stream_generator: Generator from stream_openai() or stream_anthropic()
            callback: Function to call for each chunk (e.g., update UI)
            delay: Delay between chunks in seconds (for visual effect)

        Returns:
            Full accumulated response text

        Example:
            def update_ui(text):
                placeholder.markdown(current_text + text)

            full_response = streaming_manager.stream_with_callback(
                streaming_manager.stream_openai(client, messages),
                callback=update_ui
            )
        """
        full_response = ""

        try:
            for chunk in stream_generator:
                if chunk.content:
                    full_response += chunk.content

                    # Call callback with new content
                    if callback:
                        callback(chunk.content)

                    # Small delay for visual effect (optional)
                    if delay > 0:
                        time.sleep(delay)

                # Log usage info if available
                if chunk.usage:
                    logger.info(f"Token usage: {chunk.usage}")
                    self.total_tokens = chunk.usage.get('total_tokens', 0)

        except Exception as e:
            logger.error(f"Streaming callback error: {str(e)}", exc_info=True)
            error_msg = f"\n\n[Error during streaming: {str(e)}]"
            full_response += error_msg
            if callback:
                callback(error_msg)

        return full_response

    def stop_stream(self):
        """
        Attempt to stop current stream.
        Note: Not all streaming APIs support cancellation.
        """
        if self.current_stream:
            try:
                if hasattr(self.current_stream, 'close'):
                    self.current_stream.close()
                logger.info("Stream stopped by user")
            except Exception as e:
                logger.warning(f"Could not stop stream: {e}")

        self.current_stream = None

    def get_stats(self) -> Dict[str, Any]:
        """
        Get streaming statistics.

        Returns:
            Dictionary with streaming stats
        """
        return {
            "total_tokens": self.total_tokens,
            "is_streaming": self.current_stream is not None
        }


class StreamlitStreamingHelper:
    """
    Helper class for integrating streaming with Streamlit.
    Handles Streamlit-specific UI updates.
    """

    @staticmethod
    def stream_to_placeholder(
        streaming_manager: StreamingManager,
        stream_generator: Generator[StreamChunk, None, None],
        placeholder,
        delay: float = 0.01
    ) -> str:
        """
        Stream content to Streamlit placeholder with real-time updates.

        Args:
            streaming_manager: StreamingManager instance
            stream_generator: Stream generator from streaming_manager
            placeholder: Streamlit placeholder object (st.empty())
            delay: Delay between updates

        Returns:
            Full response text

        Example:
            placeholder = st.empty()

            response = StreamlitStreamingHelper.stream_to_placeholder(
                streaming_manager,
                streaming_manager.stream_openai(client, messages),
                placeholder
            )
        """
        full_response = ""

        def update_placeholder(new_content):
            nonlocal full_response
            placeholder.markdown(full_response + new_content)

        full_response = streaming_manager.stream_with_callback(
            stream_generator,
            callback=update_placeholder,
            delay=delay
        )

        # Final update
        placeholder.markdown(full_response)

        return full_response


def main():
    """Test streaming manager functionality."""
    from openai import OpenAI
    import os

    print("Testing StreamingManager...")

    # Initialize
    streaming_manager = StreamingManager()

    # Test messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a haiku about coding."}
    ]

    # Test OpenAI streaming
    print("\n=== Testing OpenAI Streaming ===")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        full_response = ""
        for chunk in streaming_manager.stream_openai(
            client=client,
            messages=messages,
            model="gpt-4o-mini",
            max_tokens=100
        ):
            if chunk.content:
                print(chunk.content, end='', flush=True)
                full_response += chunk.content

            if chunk.usage:
                print(f"\n\nUsage: {chunk.usage}")

        print(f"\n\nFull response ({len(full_response)} chars):")
        print(full_response)

    except Exception as e:
        print(f"Error: {e}")

    # Stats
    print(f"\nStats: {streaming_manager.get_stats()}")


if __name__ == "__main__":
    main()
