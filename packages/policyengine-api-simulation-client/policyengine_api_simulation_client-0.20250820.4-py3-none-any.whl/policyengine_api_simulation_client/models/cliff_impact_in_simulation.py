from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CliffImpactInSimulation")


@_attrs_define
class CliffImpactInSimulation:
    """
    Attributes:
        cliff_gap (float):
        cliff_share (float):
    """

    cliff_gap: float
    cliff_share: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cliff_gap = self.cliff_gap

        cliff_share = self.cliff_share

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cliff_gap": cliff_gap,
                "cliff_share": cliff_share,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cliff_gap = d.pop("cliff_gap")

        cliff_share = d.pop("cliff_share")

        cliff_impact_in_simulation = cls(
            cliff_gap=cliff_gap,
            cliff_share=cliff_share,
        )

        cliff_impact_in_simulation.additional_properties = d
        return cliff_impact_in_simulation

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
