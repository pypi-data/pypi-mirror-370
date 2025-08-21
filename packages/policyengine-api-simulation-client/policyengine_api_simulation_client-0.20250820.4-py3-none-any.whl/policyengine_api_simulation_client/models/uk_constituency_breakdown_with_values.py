from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.uk_constituency_breakdown_with_values_by_constituency import (
        UKConstituencyBreakdownWithValuesByConstituency,
    )
    from ..models.uk_constituency_breakdown_with_values_outcomes_by_region import (
        UKConstituencyBreakdownWithValuesOutcomesByRegion,
    )


T = TypeVar("T", bound="UKConstituencyBreakdownWithValues")


@_attrs_define
class UKConstituencyBreakdownWithValues:
    """
    Attributes:
        by_constituency (UKConstituencyBreakdownWithValuesByConstituency):
        outcomes_by_region (UKConstituencyBreakdownWithValuesOutcomesByRegion):
    """

    by_constituency: "UKConstituencyBreakdownWithValuesByConstituency"
    outcomes_by_region: "UKConstituencyBreakdownWithValuesOutcomesByRegion"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        by_constituency = self.by_constituency.to_dict()

        outcomes_by_region = self.outcomes_by_region.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "by_constituency": by_constituency,
                "outcomes_by_region": outcomes_by_region,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.uk_constituency_breakdown_with_values_by_constituency import (
            UKConstituencyBreakdownWithValuesByConstituency,
        )
        from ..models.uk_constituency_breakdown_with_values_outcomes_by_region import (
            UKConstituencyBreakdownWithValuesOutcomesByRegion,
        )

        d = dict(src_dict)
        by_constituency = UKConstituencyBreakdownWithValuesByConstituency.from_dict(d.pop("by_constituency"))

        outcomes_by_region = UKConstituencyBreakdownWithValuesOutcomesByRegion.from_dict(d.pop("outcomes_by_region"))

        uk_constituency_breakdown_with_values = cls(
            by_constituency=by_constituency,
            outcomes_by_region=outcomes_by_region,
        )

        uk_constituency_breakdown_with_values.additional_properties = d
        return uk_constituency_breakdown_with_values

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
