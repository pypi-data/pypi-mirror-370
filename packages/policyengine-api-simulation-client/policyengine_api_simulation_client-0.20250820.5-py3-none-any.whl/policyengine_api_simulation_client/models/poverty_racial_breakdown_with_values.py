from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.racial_baseline_reform_values import RacialBaselineReformValues


T = TypeVar("T", bound="PovertyRacialBreakdownWithValues")


@_attrs_define
class PovertyRacialBreakdownWithValues:
    """
    Attributes:
        poverty (RacialBaselineReformValues):
    """

    poverty: "RacialBaselineReformValues"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        poverty = self.poverty.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "poverty": poverty,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.racial_baseline_reform_values import RacialBaselineReformValues

        d = dict(src_dict)
        poverty = RacialBaselineReformValues.from_dict(d.pop("poverty"))

        poverty_racial_breakdown_with_values = cls(
            poverty=poverty,
        )

        poverty_racial_breakdown_with_values.additional_properties = d
        return poverty_racial_breakdown_with_values

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
