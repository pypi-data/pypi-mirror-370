from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.wealth_decile_impact_with_values_average import WealthDecileImpactWithValuesAverage
    from ..models.wealth_decile_impact_with_values_relative import WealthDecileImpactWithValuesRelative


T = TypeVar("T", bound="WealthDecileImpactWithValues")


@_attrs_define
class WealthDecileImpactWithValues:
    """
    Attributes:
        relative (WealthDecileImpactWithValuesRelative):
        average (WealthDecileImpactWithValuesAverage):
    """

    relative: "WealthDecileImpactWithValuesRelative"
    average: "WealthDecileImpactWithValuesAverage"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        relative = self.relative.to_dict()

        average = self.average.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "relative": relative,
                "average": average,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.wealth_decile_impact_with_values_average import WealthDecileImpactWithValuesAverage
        from ..models.wealth_decile_impact_with_values_relative import WealthDecileImpactWithValuesRelative

        d = dict(src_dict)
        relative = WealthDecileImpactWithValuesRelative.from_dict(d.pop("relative"))

        average = WealthDecileImpactWithValuesAverage.from_dict(d.pop("average"))

        wealth_decile_impact_with_values = cls(
            relative=relative,
            average=average,
        )

        wealth_decile_impact_with_values.additional_properties = d
        return wealth_decile_impact_with_values

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
