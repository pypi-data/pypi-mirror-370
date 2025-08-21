from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.baseline_reform_values import BaselineReformValues


T = TypeVar("T", bound="AgeGroupBaselineReformValues")


@_attrs_define
class AgeGroupBaselineReformValues:
    """
    Attributes:
        child (BaselineReformValues):
        adult (BaselineReformValues):
        senior (BaselineReformValues):
        all_ (BaselineReformValues):
    """

    child: "BaselineReformValues"
    adult: "BaselineReformValues"
    senior: "BaselineReformValues"
    all_: "BaselineReformValues"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        child = self.child.to_dict()

        adult = self.adult.to_dict()

        senior = self.senior.to_dict()

        all_ = self.all_.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "child": child,
                "adult": adult,
                "senior": senior,
                "all": all_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.baseline_reform_values import BaselineReformValues

        d = dict(src_dict)
        child = BaselineReformValues.from_dict(d.pop("child"))

        adult = BaselineReformValues.from_dict(d.pop("adult"))

        senior = BaselineReformValues.from_dict(d.pop("senior"))

        all_ = BaselineReformValues.from_dict(d.pop("all"))

        age_group_baseline_reform_values = cls(
            child=child,
            adult=adult,
            senior=senior,
            all_=all_,
        )

        age_group_baseline_reform_values.additional_properties = d
        return age_group_baseline_reform_values

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
