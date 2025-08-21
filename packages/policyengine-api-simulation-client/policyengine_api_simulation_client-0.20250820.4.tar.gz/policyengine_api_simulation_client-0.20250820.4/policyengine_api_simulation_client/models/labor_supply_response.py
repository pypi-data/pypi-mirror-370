from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.hours_response import HoursResponse
    from ..models.labor_supply_response_decile import LaborSupplyResponseDecile
    from ..models.labor_supply_response_relative_lsr import LaborSupplyResponseRelativeLsr


T = TypeVar("T", bound="LaborSupplyResponse")


@_attrs_define
class LaborSupplyResponse:
    """
    Attributes:
        substitution_lsr (float):
        income_lsr (float):
        relative_lsr (LaborSupplyResponseRelativeLsr):
        total_change (float):
        revenue_change (float):
        decile (LaborSupplyResponseDecile):
        hours (HoursResponse):
    """

    substitution_lsr: float
    income_lsr: float
    relative_lsr: "LaborSupplyResponseRelativeLsr"
    total_change: float
    revenue_change: float
    decile: "LaborSupplyResponseDecile"
    hours: "HoursResponse"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        substitution_lsr = self.substitution_lsr

        income_lsr = self.income_lsr

        relative_lsr = self.relative_lsr.to_dict()

        total_change = self.total_change

        revenue_change = self.revenue_change

        decile = self.decile.to_dict()

        hours = self.hours.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "substitution_lsr": substitution_lsr,
                "income_lsr": income_lsr,
                "relative_lsr": relative_lsr,
                "total_change": total_change,
                "revenue_change": revenue_change,
                "decile": decile,
                "hours": hours,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.hours_response import HoursResponse
        from ..models.labor_supply_response_decile import LaborSupplyResponseDecile
        from ..models.labor_supply_response_relative_lsr import LaborSupplyResponseRelativeLsr

        d = dict(src_dict)
        substitution_lsr = d.pop("substitution_lsr")

        income_lsr = d.pop("income_lsr")

        relative_lsr = LaborSupplyResponseRelativeLsr.from_dict(d.pop("relative_lsr"))

        total_change = d.pop("total_change")

        revenue_change = d.pop("revenue_change")

        decile = LaborSupplyResponseDecile.from_dict(d.pop("decile"))

        hours = HoursResponse.from_dict(d.pop("hours"))

        labor_supply_response = cls(
            substitution_lsr=substitution_lsr,
            income_lsr=income_lsr,
            relative_lsr=relative_lsr,
            total_change=total_change,
            revenue_change=revenue_change,
            decile=decile,
            hours=hours,
        )

        labor_supply_response.additional_properties = d
        return labor_supply_response

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
