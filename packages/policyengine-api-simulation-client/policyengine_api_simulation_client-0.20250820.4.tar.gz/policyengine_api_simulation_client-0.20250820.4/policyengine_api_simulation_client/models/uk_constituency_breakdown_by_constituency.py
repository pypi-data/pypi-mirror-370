from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UKConstituencyBreakdownByConstituency")


@_attrs_define
class UKConstituencyBreakdownByConstituency:
    """
    Attributes:
        average_household_income_change (float):
        relative_household_income_change (float):
        x (int):
        y (int):
    """

    average_household_income_change: float
    relative_household_income_change: float
    x: int
    y: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        average_household_income_change = self.average_household_income_change

        relative_household_income_change = self.relative_household_income_change

        x = self.x

        y = self.y

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "average_household_income_change": average_household_income_change,
                "relative_household_income_change": relative_household_income_change,
                "x": x,
                "y": y,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        average_household_income_change = d.pop("average_household_income_change")

        relative_household_income_change = d.pop("relative_household_income_change")

        x = d.pop("x")

        y = d.pop("y")

        uk_constituency_breakdown_by_constituency = cls(
            average_household_income_change=average_household_income_change,
            relative_household_income_change=relative_household_income_change,
            x=x,
            y=y,
        )

        uk_constituency_breakdown_by_constituency.additional_properties = d
        return uk_constituency_breakdown_by_constituency

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
