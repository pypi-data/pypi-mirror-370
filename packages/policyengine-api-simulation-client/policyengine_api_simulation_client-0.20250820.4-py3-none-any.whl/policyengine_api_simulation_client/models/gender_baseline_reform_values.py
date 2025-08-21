from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.baseline_reform_values import BaselineReformValues


T = TypeVar("T", bound="GenderBaselineReformValues")


@_attrs_define
class GenderBaselineReformValues:
    """
    Attributes:
        male (BaselineReformValues):
        female (BaselineReformValues):
    """

    male: "BaselineReformValues"
    female: "BaselineReformValues"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        male = self.male.to_dict()

        female = self.female.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "male": male,
                "female": female,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.baseline_reform_values import BaselineReformValues

        d = dict(src_dict)
        male = BaselineReformValues.from_dict(d.pop("male"))

        female = BaselineReformValues.from_dict(d.pop("female"))

        gender_baseline_reform_values = cls(
            male=male,
            female=female,
        )

        gender_baseline_reform_values.additional_properties = d
        return gender_baseline_reform_values

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
