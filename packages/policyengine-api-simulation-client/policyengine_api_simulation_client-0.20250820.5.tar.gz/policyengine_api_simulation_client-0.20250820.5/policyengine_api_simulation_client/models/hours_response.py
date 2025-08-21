from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="HoursResponse")


@_attrs_define
class HoursResponse:
    """
    Attributes:
        baseline (float):
        reform (float):
        change (float):
        income_effect (float):
        substitution_effect (float):
    """

    baseline: float
    reform: float
    change: float
    income_effect: float
    substitution_effect: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        baseline = self.baseline

        reform = self.reform

        change = self.change

        income_effect = self.income_effect

        substitution_effect = self.substitution_effect

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "baseline": baseline,
                "reform": reform,
                "change": change,
                "income_effect": income_effect,
                "substitution_effect": substitution_effect,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        baseline = d.pop("baseline")

        reform = d.pop("reform")

        change = d.pop("change")

        income_effect = d.pop("income_effect")

        substitution_effect = d.pop("substitution_effect")

        hours_response = cls(
            baseline=baseline,
            reform=reform,
            change=change,
            income_effect=income_effect,
            substitution_effect=substitution_effect,
        )

        hours_response.additional_properties = d
        return hours_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
