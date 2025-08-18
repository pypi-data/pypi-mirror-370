from __future__ import annotations

import logging
import numbers
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

logger = logging.getLogger(__name__)

# making distinct types here because we want a separation between numeric and object buckets. They should never mix
NumericDefinitionType = tuple[float, float] | float
ObjectDefinitionType = str | list[str]
BucketDefinitionType = NumericDefinitionType | ObjectDefinitionType

T = TypeVar("T")


class Bucket(BaseModel, ABC, Generic[T]):
    """
    Abstract base class for all bucket types. bucket types can be whatever you want them to be. We have two concrete
    implementations: NumericBucket and ObjectBucket.
    Subclasses must implement get_score get_sort_key and overlaps_with methods.
    TODO: Can we do away with sort keys and display_definition or make them nicer/easier to work with since it is only a visual thing?
    TODO: think about whether an ABC is the best way to go here. Do we need BaseModel?
    """

    definition: BucketDefinitionType
    score: float

    @abstractmethod
    def contains(self, value: float | int | str) -> bool:
        """Check if this bucket contains the given value"""
        pass

    @abstractmethod
    def get_sort_key(self) -> tuple[int, Any]:
        """Generate a sort key for natural ordering of buckets"""
        pass

    @abstractmethod
    def overlaps_with(self, other: T) -> bool:
        """Check if this bucket overlaps with another bucket of the same type"""
        pass

    @abstractmethod
    def display_definition(self) -> str:
        """Return a human-readable string representation of the bucket definition"""
        pass


class NumericBucket(Bucket["NumericBucket"]):
    """
    Implementation of a Bucket class for numeric values. Numerical buckets are made up of ranges or exact values.
    Usually exact values are used for "special cases" such as a number than has a special meaning like 99999 or 0.
    Ranges are used for "normal cases" such as 18-25, 26-65, 66-100.
    """

    definition: NumericDefinitionType
    left_inclusive: bool = True
    right_inclusive: bool = False

    def contains(self, value: float | int | str) -> bool:
        # Use numbers.Number to check for any numeric type (stdlib + numpy)
        if not isinstance(value, numbers.Number):
            raise TypeError(
                f"NumericBucket only accepts numeric values, got {type(value).__name__}: {value}")

        # Convert to float for consistent processing
        value = float(value)

        if isinstance(self.definition, tuple):
            left_bound, right_bound = self.definition

            left_condition = value >= left_bound if self.left_inclusive else value > left_bound
            right_condition = value <= right_bound if self.right_inclusive else value < right_bound

            return left_condition and right_condition
        elif isinstance(self.definition, float):
            return value == self.definition

        return False

    def get_sort_key(self) -> tuple[int, float]:
        """Sort ranges first by lowest score, then exact values"""
        if isinstance(self.definition, tuple):
            return (0, self.score)
        else:
            return (1, self.score)

    def overlaps_with(self, other: NumericBucket) -> bool:
        """Check if this numeric bucket overlaps with another numeric bucket"""
        self_range = self._get_range()
        other_range = other._get_range()

        self_left, self_right = self_range
        other_left, other_right = other_range

        # Two ranges overlap if there's any value that belongs to both ranges
        # We can check this by finding the intersection and seeing if it's non-empty

        intersection_left = max(self_left, other_left)
        intersection_right = min(self_right, other_right)

        if intersection_left > intersection_right:
            return False

        if intersection_left < intersection_right:
            return True

        # If intersection_left == intersection_right, check if both ranges include this point
        boundary_point = intersection_left

        # Check if self includes the boundary point
        self_includes = (
            (boundary_point == self_left and self.left_inclusive)
            or (boundary_point == self_right and self.right_inclusive)
            or (self_left < boundary_point < self_right)
        )

        # Check if other includes the boundary point
        other_includes = (
            (boundary_point == other_left and other.left_inclusive)
            or (boundary_point == other_right and other.right_inclusive)
            or (other_left < boundary_point < other_right)
        )

        return self_includes and other_includes

    def _get_range(self) -> tuple[float, float]:
        """Get the range covered by this bucket"""
        if isinstance(self.definition, tuple):
            return self.definition
        else:
            # Exact value is treated as a range [value, value]
            return (float(self.definition), float(self.definition))

    def display_definition(self) -> str:
        """Return a human-readable string representation of the bucket definition"""
        if isinstance(self.definition, tuple):
            left_bracket = "[" if self.left_inclusive else "("
            right_bracket = "]" if self.right_inclusive else ")"

            # Format infinity values nicely
            left_val = "-∞" if self.definition[0] == float(
                '-inf') else str(self.definition[0])
            right_val = "∞" if self.definition[1] == float(
                'inf') else str(self.definition[1])

            return f"{left_bracket}{left_val}, {right_val}{right_bracket}"
        else:
            return f"= {self.definition}"


class ObjectBucket(Bucket["ObjectBucket"]):
    """
    Bucket for string/categorical values. Supports single strings or lists of strings.
    """

    definition: ObjectDefinitionType

    def contains(self, value: float | int | str) -> bool:
        if not isinstance(value, str):
            raise TypeError(
                f"ObjectBucket only accepts string values, got {type(value).__name__}: {value}")

        if isinstance(self.definition, str):
            return value == self.definition
        elif isinstance(self.definition, list):
            return value in self.definition

        return False

    def get_sort_key(self) -> tuple[int, float]:
        """Sort lists before strings"""
        if isinstance(self.definition, str):
            return (1, self.score)
        else:
            return (0, self.score)

    def overlaps_with(self, other: ObjectBucket) -> bool:
        """Check if this object bucket overlaps with another object bucket"""
        # Get sets of values for both buckets
        self_values = self._get_values()
        other_values = other._get_values()

        # Check for intersection
        return bool(self_values.intersection(other_values))

    def _get_values(self) -> set[str]:
        """Get the set of values covered by this bucket"""
        if isinstance(self.definition, str):
            return {self.definition}
        else:
            return set(self.definition)

    def display_definition(self) -> str:
        """Return a human-readable string representation of the bucket definition"""
        if isinstance(self.definition, str):
            return f"'{self.definition}'"
        else:
            return f"{self.definition}"
