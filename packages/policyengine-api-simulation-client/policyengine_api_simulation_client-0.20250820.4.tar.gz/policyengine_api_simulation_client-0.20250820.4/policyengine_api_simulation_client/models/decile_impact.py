from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.decile_impact_average import DecileImpactAverage
    from ..models.decile_impact_relative import DecileImpactRelative


T = TypeVar("T", bound="DecileImpact")


@_attrs_define
class DecileImpact:
    """
    Attributes:
        relative (DecileImpactRelative):
        average (DecileImpactAverage):
    """

    relative: "DecileImpactRelative"
    average: "DecileImpactAverage"
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
        from ..models.decile_impact_average import DecileImpactAverage
        from ..models.decile_impact_relative import DecileImpactRelative

        d = dict(src_dict)
        relative = DecileImpactRelative.from_dict(d.pop("relative"))

        average = DecileImpactAverage.from_dict(d.pop("average"))

        decile_impact = cls(
            relative=relative,
            average=average,
        )

        decile_impact.additional_properties = d
        return decile_impact

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
