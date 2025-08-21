from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.cliff_impact_in_simulation import CliffImpactInSimulation


T = TypeVar("T", bound="CliffImpact")


@_attrs_define
class CliffImpact:
    """
    Attributes:
        baseline (CliffImpactInSimulation):
        reform (CliffImpactInSimulation):
    """

    baseline: "CliffImpactInSimulation"
    reform: "CliffImpactInSimulation"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        baseline = self.baseline.to_dict()

        reform = self.reform.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "baseline": baseline,
                "reform": reform,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cliff_impact_in_simulation import CliffImpactInSimulation

        d = dict(src_dict)
        baseline = CliffImpactInSimulation.from_dict(d.pop("baseline"))

        reform = CliffImpactInSimulation.from_dict(d.pop("reform"))

        cliff_impact = cls(
            baseline=baseline,
            reform=reform,
        )

        cliff_impact.additional_properties = d
        return cliff_impact

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
