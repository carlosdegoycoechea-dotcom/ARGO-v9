"""
Unit tests for ConversationSummarizer

Author: ARGO Development Team
Date: 2025-11-19
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.conversation_summarizer import ConversationSummarizer


class TestConversationSummarizer(unittest.TestCase):
    """Test cases for ConversationSummarizer"""

    def setUp(self):
        """Set up test fixtures"""
        # Create mock LLM
        self.mock_llm = Mock()
        self.mock_llm.chat = Mock()
        self.mock_llm.chat.completions = Mock()

        # Mock response
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "This is a test summary of the conversation."
        mock_choice.message = mock_message

        mock_response = Mock()
        mock_response.choices = [mock_choice]

        self.mock_llm.chat.completions.create = Mock(return_value=mock_response)

        # Create summarizer
        self.summarizer = ConversationSummarizer(
            llm=self.mock_llm,
            threshold=15,
            max_summary_tokens=500
        )

    def test_initialization(self):
        """Test summarizer initialization"""
        self.assertEqual(self.summarizer.threshold, 15)
        self.assertEqual(self.summarizer.max_summary_tokens, 500)
        self.assertIs(self.summarizer.llm, self.mock_llm)

    def test_needs_summary_below_threshold(self):
        """Test needs_summary returns False when below threshold"""
        result = self.summarizer.needs_summary(10)
        self.assertFalse(result)

    def test_needs_summary_at_threshold(self):
        """Test needs_summary returns False at threshold"""
        result = self.summarizer.needs_summary(15)
        self.assertFalse(result)

    def test_needs_summary_above_threshold(self):
        """Test needs_summary returns True when above threshold"""
        result = self.summarizer.needs_summary(16)
        self.assertTrue(result)

    def test_compress_history_short(self):
        """Test compress_history with short history (no compression needed)"""
        messages = [
            {"role": "user", "content": "Message 1"},
            {"role": "assistant", "content": "Response 1"},
            {"role": "user", "content": "Message 2"},
        ]

        summary, compressed = self.summarizer.compress_history(messages, keep_recent=6)

        self.assertEqual(summary, "")
        self.assertEqual(compressed, messages)
        self.assertEqual(len(compressed), 3)

    def test_compress_history_long(self):
        """Test compress_history with long history (compression needed)"""
        # Create 20 messages
        messages = []
        for i in range(20):
            role = "user" if i % 2 == 0 else "assistant"
            messages.append({
                "role": role,
                "content": f"Message {i+1} content here"
            })

        summary, compressed = self.summarizer.compress_history(messages, keep_recent=6)

        # Should have summary + 6 recent messages
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 0)
        self.assertEqual(len(compressed), 7)  # 1 system message + 6 recent

        # First message should be system with summary
        self.assertEqual(compressed[0]['role'], 'system')
        self.assertIn('Previous conversation summary', compressed[0]['content'])

        # Remaining messages should be the last 6 originals
        for i, msg in enumerate(compressed[1:]):
            original_idx = 14 + i  # Last 6 messages from original
            self.assertEqual(msg, messages[original_idx])

    def test_compress_history_keep_recent(self):
        """Test compress_history keeps specified number of recent messages"""
        messages = []
        for i in range(15):
            messages.append({"role": "user", "content": f"Msg {i}"})

        summary, compressed = self.summarizer.compress_history(messages, keep_recent=3)

        # Should have 1 system + 3 recent = 4 total
        self.assertEqual(len(compressed), 4)
        self.assertEqual(compressed[0]['role'], 'system')

        # Last 3 should be messages 12, 13, 14
        self.assertEqual(compressed[1]['content'], "Msg 12")
        self.assertEqual(compressed[2]['content'], "Msg 13")
        self.assertEqual(compressed[3]['content'], "Msg 14")

    def test_format_messages_for_summary(self):
        """Test _format_messages_for_summary"""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
            {"role": "user", "content": "How are you?"}
        ]

        formatted = self.summarizer._format_messages_for_summary(messages)

        self.assertIn("USER: Hello", formatted)
        self.assertIn("ASSISTANT: Hi there", formatted)
        self.assertIn("USER: How are you?", formatted)

    def test_create_fallback_summary(self):
        """Test _create_fallback_summary without LLM"""
        messages = [
            {"role": "user", "content": "Question 1"},
            {"role": "assistant", "content": "Answer 1"},
            {"role": "user", "content": "Question 2"},
            {"role": "assistant", "content": "Answer 2"},
        ]

        summary = self.summarizer._create_fallback_summary(messages)

        self.assertIn("2 user queries", summary)
        self.assertIn("2 assistant responses", summary)
        self.assertGreater(len(summary), 20)

    def test_estimate_tokens(self):
        """Test estimate_tokens approximation"""
        messages = [
            {"role": "user", "content": "This is a test message"},
            {"role": "assistant", "content": "This is another test message"}
        ]

        tokens = self.summarizer.estimate_tokens(messages)

        # Rough estimate: ~50 chars total / 4 = ~12 tokens
        self.assertGreater(tokens, 0)
        self.assertLess(tokens, 100)

    def test_get_compression_stats(self):
        """Test get_compression_stats"""
        original = [{"role": "user", "content": "x" * 100}] * 20  # 20 messages
        compressed = [{"role": "user", "content": "x" * 50}] * 7  # 7 messages

        stats = self.summarizer.get_compression_stats(original, compressed)

        self.assertEqual(stats['original_message_count'], 20)
        self.assertEqual(stats['compressed_message_count'], 7)
        self.assertGreater(stats['original_tokens'], stats['compressed_tokens'])
        self.assertGreater(stats['compression_ratio'], 0)
        self.assertIn('timestamp', stats)

    def test_generate_summary_calls_llm(self):
        """Test _generate_summary calls LLM correctly"""
        messages = [
            {"role": "user", "content": "Test question"},
            {"role": "assistant", "content": "Test answer"}
        ]

        summary = self.summarizer._generate_summary(messages)

        # Should call LLM
        self.mock_llm.chat.completions.create.assert_called_once()

        # Should return summary text
        self.assertEqual(summary, "This is a test summary of the conversation.")

    def test_generate_summary_handles_llm_error(self):
        """Test _generate_summary falls back on LLM error"""
        # Make LLM raise error
        self.mock_llm.chat.completions.create.side_effect = Exception("API Error")

        messages = [
            {"role": "user", "content": "Test"},
            {"role": "assistant", "content": "Response"}
        ]

        summary = self.summarizer._generate_summary(messages)

        # Should fall back to simple summary
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 0)
        self.assertIn("user queries", summary.lower())

    def test_compression_with_different_thresholds(self):
        """Test that different thresholds work correctly"""
        summarizer_low = ConversationSummarizer(self.mock_llm, threshold=5)
        summarizer_high = ConversationSummarizer(self.mock_llm, threshold=25)

        self.assertTrue(summarizer_low.needs_summary(6))
        self.assertFalse(summarizer_high.needs_summary(6))

        self.assertTrue(summarizer_low.needs_summary(20))
        self.assertFalse(summarizer_high.needs_summary(20))

        self.assertTrue(summarizer_high.needs_summary(26))

    def test_empty_messages(self):
        """Test handling of empty message list"""
        summary, compressed = self.summarizer.compress_history([], keep_recent=6)

        self.assertEqual(summary, "")
        self.assertEqual(compressed, [])

    def test_single_message(self):
        """Test handling of single message"""
        messages = [{"role": "user", "content": "Hello"}]

        summary, compressed = self.summarizer.compress_history(messages, keep_recent=6)

        self.assertEqual(summary, "")
        self.assertEqual(compressed, messages)

    def test_estimate_tokens_empty(self):
        """Test token estimation with empty messages"""
        tokens = self.summarizer.estimate_tokens([])
        self.assertEqual(tokens, 0)

    def test_stats_with_empty_messages(self):
        """Test stats calculation with empty messages"""
        stats = self.summarizer.get_compression_stats([], [])

        self.assertEqual(stats['original_message_count'], 0)
        self.assertEqual(stats['compressed_message_count'], 0)
        self.assertEqual(stats['compression_ratio'], 0)


class TestConversationSummarizerIntegration(unittest.TestCase):
    """Integration tests that test the full flow"""

    def setUp(self):
        """Set up integration test fixtures"""
        self.mock_llm = Mock()
        self.mock_llm.chat.completions.create = Mock()

        # Create mock response
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Comprehensive test summary"
        mock_choice.message = mock_message
        mock_response = Mock()
        mock_response.choices = [mock_choice]

        self.mock_llm.chat.completions.create.return_value = mock_response

        self.summarizer = ConversationSummarizer(self.mock_llm, threshold=10)

    def test_full_compression_workflow(self):
        """Test complete workflow from detection to compression"""
        # Create conversation that exceeds threshold
        messages = []
        for i in range(15):
            messages.append({"role": "user", "content": f"User message {i}"})
            messages.append({"role": "assistant", "content": f"Assistant response {i}"})

        # Check if summarization is needed
        needs_summary = self.summarizer.needs_summary(len(messages))
        self.assertTrue(needs_summary)

        # Perform compression
        summary, compressed = self.summarizer.compress_history(messages, keep_recent=6)

        # Verify results
        self.assertIsNotNone(summary)
        self.assertGreater(len(summary), 0)
        self.assertEqual(len(compressed), 7)  # 1 system + 6 recent

        # Get statistics
        stats = self.summarizer.get_compression_stats(messages, compressed)

        self.assertEqual(stats['original_message_count'], 30)
        self.assertEqual(stats['compressed_message_count'], 7)
        self.assertGreater(stats['compression_ratio'], 50)  # Should save >50%


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConversationSummarizer))
    suite.addTests(loader.loadTestsFromTestCase(TestConversationSummarizerIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
