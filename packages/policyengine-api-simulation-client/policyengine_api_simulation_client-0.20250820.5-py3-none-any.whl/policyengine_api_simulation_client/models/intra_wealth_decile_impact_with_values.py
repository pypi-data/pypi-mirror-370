from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.intra_wealth_decile_impact_with_values_all import IntraWealthDecileImpactWithValuesAll
    from ..models.intra_wealth_decile_impact_with_values_deciles import IntraWealthDecileImpactWithValuesDeciles


T = TypeVar("T", bound="IntraWealthDecileImpactWithValues")


@_attrs_define
class IntraWealthDecileImpactWithValues:
    """
    Attributes:
        deciles (IntraWealthDecileImpactWithValuesDeciles):
        all_ (IntraWealthDecileImpactWithValuesAll):
    """

    deciles: "IntraWealthDecileImpactWithValuesDeciles"
    all_: "IntraWealthDecileImpactWithValuesAll"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        deciles = self.deciles.to_dict()

        all_ = self.all_.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "deciles": deciles,
                "all": all_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.intra_wealth_decile_impact_with_values_all import IntraWealthDecileImpactWithValuesAll
        from ..models.intra_wealth_decile_impact_with_values_deciles import IntraWealthDecileImpactWithValuesDeciles

        d = dict(src_dict)
        deciles = IntraWealthDecileImpactWithValuesDeciles.from_dict(d.pop("deciles"))

        all_ = IntraWealthDecileImpactWithValuesAll.from_dict(d.pop("all"))

        intra_wealth_decile_impact_with_values = cls(
            deciles=deciles,
            all_=all_,
        )

        intra_wealth_decile_impact_with_values.additional_properties = d
        return intra_wealth_decile_impact_with_values

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
