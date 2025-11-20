"""
ARGO v9.0 - Memory Manager
Manages user feedback and learning from interactions.

Author: ARGO Development Team
Date: 2025-11-19
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FeedbackEntry:
    """Represents a single feedback entry"""
    id: Optional[int]
    project_id: str
    session_id: str
    query: str
    response: str
    rating: int  # 1 = helpful, -1 = not helpful, 0 = neutral
    feedback_text: Optional[str]
    sources: Optional[str]
    confidence: Optional[float]
    timestamp: str


class MemoryManager:
    """
    Manages user feedback and system learning.

    Features:
    - Stores positive/negative feedback from users
    - Tracks which responses were helpful
    - Identifies patterns in successful queries
    - Provides feedback-based improvements
    - Generates insights from user interactions

    Usage:
        memory_manager = MemoryManager(unified_db)

        # Save positive feedback
        memory_manager.save_feedback(
            project_id="proj_123",
            session_id="session_456",
            query="What is the budget?",
            response="The budget is $500K",
            rating=1,
            sources="budget.pdf"
        )

        # Get recent feedback
        recent = memory_manager.get_recent_feedback(project_id="proj_123", limit=10)

        # Get feedback insights
        insights = memory_manager.get_feedback_insights(project_id="proj_123")
    """

    def __init__(self, unified_db):
        """
        Initialize memory manager.

        Args:
            unified_db: UnifiedDatabase instance
        """
        self.db = unified_db
        logger.info("MemoryManager initialized")

    def save_feedback(
        self,
        project_id: str,
        session_id: str,
        query: str,
        response: str,
        rating: int,
        feedback_text: Optional[str] = None,
        sources: Optional[str] = None,
        confidence: Optional[float] = None
    ) -> int:
        """
        Save user feedback for a query-response pair.

        Args:
            project_id: Project identifier
            session_id: Session identifier
            query: User query
            response: Assistant response
            rating: 1 (helpful), -1 (not helpful), 0 (neutral)
            feedback_text: Optional text feedback from user
            sources: Sources used for response
            confidence: Confidence score of response

        Returns:
            Feedback entry ID

        Example:
            feedback_id = memory_manager.save_feedback(
                project_id="proj_123",
                session_id="sess_456",
                query="What are the project risks?",
                response="The main risks are...",
                rating=1,
                sources="risk_analysis.pdf (0.95)"
            )
        """
        try:
            feedback_id = self.db.save_feedback(
                project_id=project_id,
                session_id=session_id,
                query=query,
                response=response,
                rating=rating,
                feedback_text=feedback_text,
                sources=sources,
                confidence=confidence
            )

            logger.info(f"Feedback saved: project={project_id}, rating={rating}, id={feedback_id}")
            return feedback_id

        except Exception as e:
            logger.error(f"Failed to save feedback: {str(e)}", exc_info=True)
            raise

    def get_recent_feedback(
        self,
        project_id: str,
        limit: int = 10,
        rating_filter: Optional[int] = None
    ) -> List[FeedbackEntry]:
        """
        Get recent feedback entries.

        Args:
            project_id: Project identifier
            limit: Maximum number of entries to return
            rating_filter: Filter by rating (1, -1, or 0)

        Returns:
            List of FeedbackEntry objects

        Example:
            # Get last 10 helpful responses
            helpful = memory_manager.get_recent_feedback(
                project_id="proj_123",
                limit=10,
                rating_filter=1
            )
        """
        try:
            entries = self.db.get_feedback(
                project_id=project_id,
                limit=limit,
                rating=rating_filter
            )

            feedback_list = []
            for entry in entries:
                feedback_list.append(FeedbackEntry(
                    id=entry.get('id'),
                    project_id=entry.get('project_id'),
                    session_id=entry.get('session_id'),
                    query=entry.get('query'),
                    response=entry.get('response'),
                    rating=entry.get('rating'),
                    feedback_text=entry.get('feedback_text'),
                    sources=entry.get('sources'),
                    confidence=entry.get('confidence'),
                    timestamp=entry.get('timestamp')
                ))

            logger.info(f"Retrieved {len(feedback_list)} feedback entries")
            return feedback_list

        except Exception as e:
            logger.error(f"Failed to get feedback: {str(e)}", exc_info=True)
            return []

    def get_feedback_insights(self, project_id: str) -> Dict[str, any]:
        """
        Generate insights from user feedback.

        Args:
            project_id: Project identifier

        Returns:
            Dictionary with feedback insights

        Insights include:
        - Total feedback count
        - Helpful vs not helpful ratio
        - Average confidence for helpful responses
        - Common topics in helpful queries
        - Common topics in not helpful queries

        Example:
            insights = memory_manager.get_feedback_insights("proj_123")
            print(f"Helpfulness ratio: {insights['helpfulness_ratio']:.2%}")
        """
        try:
            # Get all feedback
            all_feedback = self.get_recent_feedback(project_id, limit=1000)

            if not all_feedback:
                return {
                    "total_feedback": 0,
                    "helpful_count": 0,
                    "not_helpful_count": 0,
                    "neutral_count": 0,
                    "helpfulness_ratio": 0.0,
                    "avg_confidence_helpful": 0.0,
                    "avg_confidence_not_helpful": 0.0
                }

            # Calculate statistics
            helpful = [f for f in all_feedback if f.rating == 1]
            not_helpful = [f for f in all_feedback if f.rating == -1]
            neutral = [f for f in all_feedback if f.rating == 0]

            total = len(all_feedback)
            helpful_count = len(helpful)
            not_helpful_count = len(not_helpful)
            neutral_count = len(neutral)

            helpfulness_ratio = helpful_count / total if total > 0 else 0.0

            # Calculate average confidence for helpful responses
            helpful_with_conf = [f for f in helpful if f.confidence is not None]
            avg_conf_helpful = (
                sum(f.confidence for f in helpful_with_conf) / len(helpful_with_conf)
                if helpful_with_conf else 0.0
            )

            # Calculate average confidence for not helpful responses
            not_helpful_with_conf = [f for f in not_helpful if f.confidence is not None]
            avg_conf_not_helpful = (
                sum(f.confidence for f in not_helpful_with_conf) / len(not_helpful_with_conf)
                if not_helpful_with_conf else 0.0
            )

            insights = {
                "total_feedback": total,
                "helpful_count": helpful_count,
                "not_helpful_count": not_helpful_count,
                "neutral_count": neutral_count,
                "helpfulness_ratio": helpfulness_ratio,
                "avg_confidence_helpful": avg_conf_helpful,
                "avg_confidence_not_helpful": avg_conf_not_helpful,
                "feedback_entries": {
                    "helpful": helpful[:5],  # Top 5 helpful
                    "not_helpful": not_helpful[:5]  # Top 5 not helpful
                }
            }

            logger.info(f"Feedback insights: {helpful_count}/{total} helpful ({helpfulness_ratio:.1%})")
            return insights

        except Exception as e:
            logger.error(f"Failed to generate insights: {str(e)}", exc_info=True)
            return {}

    def get_helpful_examples(
        self,
        project_id: str,
        limit: int = 5,
        min_confidence: float = 0.7
    ) -> List[Tuple[str, str]]:
        """
        Get examples of helpful query-response pairs.

        Args:
            project_id: Project identifier
            limit: Maximum number of examples
            min_confidence: Minimum confidence score

        Returns:
            List of (query, response) tuples

        Example:
            examples = memory_manager.get_helpful_examples("proj_123")
            for query, response in examples:
                print(f"Q: {query}")
                print(f"A: {response[:100]}...")
        """
        try:
            helpful = self.get_recent_feedback(
                project_id=project_id,
                limit=limit * 2,  # Get more to filter
                rating_filter=1
            )

            # Filter by confidence
            filtered = [
                (f.query, f.response)
                for f in helpful
                if f.confidence is None or f.confidence >= min_confidence
            ]

            return filtered[:limit]

        except Exception as e:
            logger.error(f"Failed to get helpful examples: {str(e)}", exc_info=True)
            return []

    def get_improvement_suggestions(self, project_id: str) -> List[str]:
        """
        Generate improvement suggestions based on negative feedback.

        Args:
            project_id: Project identifier

        Returns:
            List of suggestion strings

        Example:
            suggestions = memory_manager.get_improvement_suggestions("proj_123")
            for suggestion in suggestions:
                print(f"- {suggestion}")
        """
        try:
            insights = self.get_feedback_insights(project_id)

            if insights.get('total_feedback', 0) == 0:
                return ["Not enough feedback data to generate suggestions"]

            suggestions = []

            # Analyze helpfulness ratio
            ratio = insights.get('helpfulness_ratio', 0)
            if ratio < 0.5:
                suggestions.append(
                    f"Low helpfulness ratio ({ratio:.1%}). Consider improving response quality or source relevance."
                )

            # Analyze confidence scores
            conf_helpful = insights.get('avg_confidence_helpful', 0)
            conf_not_helpful = insights.get('avg_confidence_not_helpful', 0)

            if conf_not_helpful > conf_helpful:
                suggestions.append(
                    "Not helpful responses have higher confidence scores. "
                    "Review confidence calculation or source quality."
                )

            if conf_helpful < 0.5:
                suggestions.append(
                    f"Average confidence for helpful responses is low ({conf_helpful:.1%}). "
                    "Consider adding more relevant documents or improving embeddings."
                )

            # Check feedback volume
            total = insights.get('total_feedback', 0)
            if total < 10:
                suggestions.append(
                    f"Only {total} feedback entries. Encourage more user feedback for better insights."
                )

            if not suggestions:
                suggestions.append("System performing well. Keep monitoring feedback patterns.")

            logger.info(f"Generated {len(suggestions)} improvement suggestions")
            return suggestions

        except Exception as e:
            logger.error(f"Failed to generate suggestions: {str(e)}", exc_info=True)
            return ["Error generating suggestions"]

    def delete_feedback(self, feedback_id: int) -> bool:
        """
        Delete a feedback entry.

        Args:
            feedback_id: Feedback entry ID

        Returns:
            True if deleted successfully
        """
        try:
            self.db.delete_feedback(feedback_id)
            logger.info(f"Feedback deleted: id={feedback_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete feedback: {str(e)}", exc_info=True)
            return False


def main():
    """Test memory manager functionality."""
    from core.unified_database import UnifiedDatabase
    from pathlib import Path

    print("Testing MemoryManager...")

    # Initialize (requires real database)
    db_path = Path("test_memory.db")
    db = UnifiedDatabase(db_path)

    memory_manager = MemoryManager(db)

    # Test save feedback
    print("\n=== Saving Feedback ===")
    feedback_id = memory_manager.save_feedback(
        project_id="test_project",
        session_id="test_session",
        query="What is the project budget?",
        response="The project budget is $500,000",
        rating=1,
        sources="budget.pdf (0.95)",
        confidence=0.92
    )
    print(f"Saved feedback ID: {feedback_id}")

    # Test get recent feedback
    print("\n=== Recent Feedback ===")
    recent = memory_manager.get_recent_feedback("test_project", limit=5)
    for entry in recent:
        print(f"- Query: {entry.query[:50]}...")
        print(f"  Rating: {entry.rating}, Confidence: {entry.confidence}")

    # Test insights
    print("\n=== Feedback Insights ===")
    insights = memory_manager.get_feedback_insights("test_project")
    for key, value in insights.items():
        if key != "feedback_entries":
            print(f"  {key}: {value}")

    # Test suggestions
    print("\n=== Improvement Suggestions ===")
    suggestions = memory_manager.get_improvement_suggestions("test_project")
    for suggestion in suggestions:
        print(f"  - {suggestion}")

    # Cleanup
    db_path.unlink(missing_ok=True)
    print("\nTest complete!")


if __name__ == "__main__":
    main()
