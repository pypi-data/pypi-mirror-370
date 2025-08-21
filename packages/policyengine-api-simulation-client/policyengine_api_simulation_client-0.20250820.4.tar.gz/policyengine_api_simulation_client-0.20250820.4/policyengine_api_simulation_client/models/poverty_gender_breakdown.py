from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.gender_baseline_reform_values import GenderBaselineReformValues


T = TypeVar("T", bound="PovertyGenderBreakdown")


@_attrs_define
class PovertyGenderBreakdown:
    """
    Attributes:
        poverty (GenderBaselineReformValues):
        deep_poverty (GenderBaselineReformValues):
    """

    poverty: "GenderBaselineReformValues"
    deep_poverty: "GenderBaselineReformValues"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        poverty = self.poverty.to_dict()

        deep_poverty = self.deep_poverty.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "poverty": poverty,
                "deep_poverty": deep_poverty,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.gender_baseline_reform_values import GenderBaselineReformValues

        d = dict(src_dict)
        poverty = GenderBaselineReformValues.from_dict(d.pop("poverty"))

        deep_poverty = GenderBaselineReformValues.from_dict(d.pop("deep_poverty"))

        poverty_gender_breakdown = cls(
            poverty=poverty,
            deep_poverty=deep_poverty,
        )

        poverty_gender_breakdown.additional_properties = d
        return poverty_gender_breakdown

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
