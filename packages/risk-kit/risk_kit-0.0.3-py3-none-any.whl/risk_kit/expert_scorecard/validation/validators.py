from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic import ValidationError

if TYPE_CHECKING:
    from risk_kit.expert_scorecard.models import ExpertScorecard


class ScorecardValidator(ABC):
    """Abstract base class for scorecard validators"""

    name: str

    @classmethod
    @abstractmethod
    def validate(cls, scorecard: ExpertScorecard) -> None:
        """Validate the scorecard. Raise ValidationError if invalid."""
        pass


class FeatureWeightValidator(ScorecardValidator):
    """
    When assigning weights to features, the goal is that the sum of the weights of all features is 100. This is a common
    requirement in expert scorecard design to ensure that the importance of each feature is correctly proportioned.
    """

    name: str = "feature_weight"

    @classmethod
    def validate(cls, scorecard: ExpertScorecard) -> None:
        total_weight = sum(feature.weight for feature in scorecard.features)
        if abs(total_weight - 100.0) > 0.001:  # Allow for floating point precision
            raise ValidationError.from_exception_data(
                "Weight validation failed",
                [
                    {
                        "type": "value_error",
                        "input": total_weight,
                        "ctx": {"error": f"Feature weights must sum to 100, got {total_weight}"},
                    }
                ],
            )


class OverlapValidator(ScorecardValidator):
    """
    When defining a scorecard, it is important to ensure that the buckets of a feature do not overlap with each other.
    This validator will ensure that the buckets of a feature do not overlap with each other.
    """

    name: str = "overlap"

    @classmethod
    def validate(cls, scorecard: ExpertScorecard) -> None:
        for feature in scorecard.features:
            if feature.has_overlapping_buckets():
                overlapping_pairs = feature.get_overlapping_buckets()
                error_messages = []
                for bucket1, bucket2 in overlapping_pairs:
                    error_messages.append(
                        f"Buckets overlap in feature '{feature.name}': "
                        f"{bucket1.definition} and {bucket2.definition}"
                    )

                raise ValidationError.from_exception_data(
                    "Bucket overlap validation failed",
                    [{"type": "value_error", "input": feature.name,
                        "ctx": {"error": msg}} for msg in error_messages],
                )
