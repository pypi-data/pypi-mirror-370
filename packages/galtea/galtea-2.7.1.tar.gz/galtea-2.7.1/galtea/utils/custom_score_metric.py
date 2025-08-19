"""
Custom metric utilities for defining and executing custom evaluation metrics.
"""

from abc import ABC, abstractmethod
from typing import Optional


class CustomScoreEvaluationMetric(ABC):
    """
    Abstract base class for custom evaluation metrics.

    This class provides an interface for creating custom metrics that can be
    used with user-defined scoring functions.

    Subclasses must implement the measure method, which should return a float score between 0.0 and 1.0.
    """

    def __init__(self, name: str) -> None:
        self.name: str = name

    @abstractmethod
    def measure(
        self,
        input: Optional[str] = None,
        actual_output: Optional[str] = None,
        expected_output: Optional[str] = None,
        retrieval_context: Optional[str] = None,
        context: Optional[str] = None,
    ) -> float:
        """
        Compute the score for the given actual output.

        Args:
            input (Optional[str]): The user query sent to the AI system.
            actual_output (Optional[str]): The actual output from the AI system.
            expected_output (Optional[str]): The expected output from the AI system.
            retrieval_context (Optional[str]): Context retrieved from the system.
            context (Optional[str]): Additional context for the evaluation.

        Returns:
            float: Score between 0.0 and 1.0.

        Raises:
            ValueError: If the score is not between 0.0 and 1.0.
        """
        pass

    def validate_score(self, score: float) -> float:
        """
        Validate that the score is within the expected range [0.0, 1.0].

        Args:
            score (float): The score to validate.

        Returns:
            float: The validated score.

        Raises:
            ValueError: If the score is not between 0.0 and 1.0.
        """
        if not isinstance(score, (int, float)):
            raise ValueError(f"Score must be a number, got {type(score)}")

        if not (0.0 <= score <= 1.0):
            raise ValueError(f"Score must be between 0.0 and 1.0, got {score}")

        return float(score)

    def __call__(
        self,
        input: Optional[str] = None,
        actual_output: Optional[str] = None,
        expected_output: Optional[str] = None,
        retrieval_context: Optional[str] = None,
        context: Optional[str] = None,
    ) -> float:
        """
        Make the metric callable, returning a validated score.

        Args:
            input (Optional[str]): The user query sent to the AI system.
            actual_output (Optional[str]): The actual output from the AI system.
            expected_output (Optional[str]): The expected output from the AI system.
            retrieval_context (Optional[str]): Context retrieved from the system.
            context (Optional[str]): Additional context for the evaluation.

        Returns:
            float: The validated score.
        """
        score: float = self.measure(
            input=input,
            actual_output=actual_output,
            expected_output=expected_output,
            retrieval_context=retrieval_context,
            context=context,
        )
        return self.validate_score(score)
