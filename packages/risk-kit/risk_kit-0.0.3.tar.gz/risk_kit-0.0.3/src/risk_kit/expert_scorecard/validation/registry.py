from __future__ import annotations

from risk_kit.expert_scorecard.validation.validators import ScorecardValidator


class ValidatorRegistry:
    _validators: dict[str, type[ScorecardValidator]] = {}

    @property
    def validators(self) -> dict[str, type[ScorecardValidator]]:
        return self._validators

    def register(self, validator: type[ScorecardValidator]) -> None:
        if validator.name in self._validators.keys():
            raise ValueError(
                f"Validator with name '{validator.name}' already registered")
        self._validators[validator.name] = validator

    def clear(self) -> None:
        self._validators.clear()
