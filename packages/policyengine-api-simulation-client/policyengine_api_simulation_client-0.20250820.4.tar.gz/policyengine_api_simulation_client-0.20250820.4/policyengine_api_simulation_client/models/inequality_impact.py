from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.baseline_reform_values import BaselineReformValues


T = TypeVar("T", bound="InequalityImpact")


@_attrs_define
class InequalityImpact:
    """
    Attributes:
        gini (BaselineReformValues):
        top_10_pct_share (BaselineReformValues):
        top_1_pct_share (BaselineReformValues):
    """

    gini: "BaselineReformValues"
    top_10_pct_share: "BaselineReformValues"
    top_1_pct_share: "BaselineReformValues"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        gini = self.gini.to_dict()

        top_10_pct_share = self.top_10_pct_share.to_dict()

        top_1_pct_share = self.top_1_pct_share.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "gini": gini,
                "top_10_pct_share": top_10_pct_share,
                "top_1_pct_share": top_1_pct_share,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.baseline_reform_values import BaselineReformValues

        d = dict(src_dict)
        gini = BaselineReformValues.from_dict(d.pop("gini"))

        top_10_pct_share = BaselineReformValues.from_dict(d.pop("top_10_pct_share"))

        top_1_pct_share = BaselineReformValues.from_dict(d.pop("top_1_pct_share"))

        inequality_impact = cls(
            gini=gini,
            top_10_pct_share=top_10_pct_share,
            top_1_pct_share=top_1_pct_share,
        )

        inequality_impact.additional_properties = d
        return inequality_impact

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
