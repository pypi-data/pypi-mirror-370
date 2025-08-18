from __future__ import annotations

import logging
from abc import ABC
from typing import Any

from pydantic import BaseModel, Field, model_validator

from risk_kit.expert_scorecard.models.bucket import NumericBucket, ObjectBucket

logger = logging.getLogger(__name__)


class BaseFeature(BaseModel, ABC):
    """Base class for all feature types."""

    name: str = Field(
        description="The name of the feature. This is the name that will be used to identify the feature in the scorecard. It is recommended to match the name of the feature to the name of the column in the data."
    )
    family: str = Field(
        description="The family of the feature. Useful for grouping features together and understanding the dominance of feature families."
    )
    description: str
    buckets: list[NumericBucket] | list[ObjectBucket]
    weight: float = Field(
        description="The weight of the feature in the overall scorecard. This is the weight that will be used to calculate the score for the feature i.e bucket points * weight = final score"
    )
    default_points: float = 0.0

    def _get_bucket_for_value(self, value: float | str) -> NumericBucket | ObjectBucket | None:
        """Get the bucket for a given value."""
        for bucket in self.buckets:
            if bucket.contains(value):
                return bucket
        return None

    def get_score(self, value: float | str) -> float:
        """Get the score for a given value."""
        bucket = self._get_bucket_for_value(value)
        if bucket is not None:
            return bucket.score

        logger.warning(
            f"No bucket found for value: {value} in feature: {self.name}")
        return self.default_points

    @model_validator(mode="after")
    def order_buckets(self) -> BaseFeature:
        # Sort buckets for visual purposes - doesn't change functionality
        self.buckets.sort(key=lambda x: x.get_sort_key())
        return self

    def has_overlapping_buckets(self) -> bool:
        """Check if any buckets in this feature overlap with each other"""
        for i, bucket1 in enumerate(self.buckets):
            for bucket2 in self.buckets[i + 1:]:
                if bucket1.overlaps_with(bucket2):  # type: ignore
                    return True
        return False

    def get_overlapping_buckets(self) -> list[tuple[Any, Any]]:
        """Get all pairs of overlapping buckets in this feature"""
        overlaps = []
        for i, bucket1 in enumerate(self.buckets):
            for bucket2 in self.buckets[i + 1:]:
                if bucket1.overlaps_with(bucket2):  # type: ignore
                    overlaps.append((bucket1, bucket2))
        return overlaps

    def get_table_rows(self) -> list[dict[str, str]]:
        """
        Get table rows for visualization purposes.

        Returns a list of dictionaries, each representing a row in a table view.
        The first row for each feature includes feature-level info, subsequent rows
        only include bucket-specific info.
        """
        rows = []
        for i, bucket in enumerate(self.buckets):
            row = {
                "feature": self.name if i == 0 else "",
                "family": self.family or "" if i == 0 else "",
                "weight": f"{self.weight}" if i == 0 else "",
                "bucket_definition": bucket.display_definition(),  # type: ignore
                "score": f"{bucket.score}",  # type: ignore
                "default_points": f"{self.default_points}" if i == 0 else "",
            }
            rows.append(row)
        return rows


class NumericFeature(BaseFeature):
    """Feature for numeric values using NumericBucket instances."""

    buckets: list[NumericBucket]


class ObjectFeature(BaseFeature):
    """Feature for categorical/string values using ObjectBucket instances."""

    buckets: list[ObjectBucket]
