from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.baseline_reform_values import BaselineReformValues


T = TypeVar("T", bound="RacialBaselineReformValues")


@_attrs_define
class RacialBaselineReformValues:
    """
    Attributes:
        white (BaselineReformValues):
        black (BaselineReformValues):
        hispanic (BaselineReformValues):
        other (BaselineReformValues):
    """

    white: "BaselineReformValues"
    black: "BaselineReformValues"
    hispanic: "BaselineReformValues"
    other: "BaselineReformValues"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        white = self.white.to_dict()

        black = self.black.to_dict()

        hispanic = self.hispanic.to_dict()

        other = self.other.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "white": white,
                "black": black,
                "hispanic": hispanic,
                "other": other,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.baseline_reform_values import BaselineReformValues

        d = dict(src_dict)
        white = BaselineReformValues.from_dict(d.pop("white"))

        black = BaselineReformValues.from_dict(d.pop("black"))

        hispanic = BaselineReformValues.from_dict(d.pop("hispanic"))

        other = BaselineReformValues.from_dict(d.pop("other"))

        racial_baseline_reform_values = cls(
            white=white,
            black=black,
            hispanic=hispanic,
            other=other,
        )

        racial_baseline_reform_values.additional_properties = d
        return racial_baseline_reform_values

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
