from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.budgetary_impact import BudgetaryImpact
    from ..models.cliff_impact import CliffImpact
    from ..models.decile_impact import DecileImpact
    from ..models.economy_comparison_detailed_budget_type_0 import EconomyComparisonDetailedBudgetType0
    from ..models.inequality_impact import InequalityImpact
    from ..models.intra_decile_impact import IntraDecileImpact
    from ..models.intra_wealth_decile_impact_with_values import IntraWealthDecileImpactWithValues
    from ..models.labor_supply_response import LaborSupplyResponse
    from ..models.poverty_gender_breakdown import PovertyGenderBreakdown
    from ..models.poverty_impact import PovertyImpact
    from ..models.poverty_racial_breakdown_with_values import PovertyRacialBreakdownWithValues
    from ..models.uk_constituency_breakdown_with_values import UKConstituencyBreakdownWithValues
    from ..models.wealth_decile_impact_with_values import WealthDecileImpactWithValues


T = TypeVar("T", bound="EconomyComparison")


@_attrs_define
class EconomyComparison:
    """
    Attributes:
        budget (BudgetaryImpact):
        detailed_budget (Union['EconomyComparisonDetailedBudgetType0', None]):
        decile (DecileImpact):
        inequality (InequalityImpact):
        poverty (PovertyImpact):
        poverty_by_gender (PovertyGenderBreakdown):
        poverty_by_race (Union['PovertyRacialBreakdownWithValues', None]):
        intra_decile (IntraDecileImpact):
        wealth_decile (Union['WealthDecileImpactWithValues', None]):
        intra_wealth_decile (Union['IntraWealthDecileImpactWithValues', None]):
        labor_supply_response (LaborSupplyResponse):
        constituency_impact (Union['UKConstituencyBreakdownWithValues', None]):
        cliff_impact (Union['CliffImpact', None]):
        model_version (Union[None, Unset, str]):
        data_version (Union[None, Unset, str]):
    """

    budget: "BudgetaryImpact"
    detailed_budget: Union["EconomyComparisonDetailedBudgetType0", None]
    decile: "DecileImpact"
    inequality: "InequalityImpact"
    poverty: "PovertyImpact"
    poverty_by_gender: "PovertyGenderBreakdown"
    poverty_by_race: Union["PovertyRacialBreakdownWithValues", None]
    intra_decile: "IntraDecileImpact"
    wealth_decile: Union["WealthDecileImpactWithValues", None]
    intra_wealth_decile: Union["IntraWealthDecileImpactWithValues", None]
    labor_supply_response: "LaborSupplyResponse"
    constituency_impact: Union["UKConstituencyBreakdownWithValues", None]
    cliff_impact: Union["CliffImpact", None]
    model_version: Union[None, Unset, str] = UNSET
    data_version: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.cliff_impact import CliffImpact
        from ..models.economy_comparison_detailed_budget_type_0 import EconomyComparisonDetailedBudgetType0
        from ..models.intra_wealth_decile_impact_with_values import IntraWealthDecileImpactWithValues
        from ..models.poverty_racial_breakdown_with_values import PovertyRacialBreakdownWithValues
        from ..models.uk_constituency_breakdown_with_values import UKConstituencyBreakdownWithValues
        from ..models.wealth_decile_impact_with_values import WealthDecileImpactWithValues

        budget = self.budget.to_dict()

        detailed_budget: Union[None, dict[str, Any]]
        if isinstance(self.detailed_budget, EconomyComparisonDetailedBudgetType0):
            detailed_budget = self.detailed_budget.to_dict()
        else:
            detailed_budget = self.detailed_budget

        decile = self.decile.to_dict()

        inequality = self.inequality.to_dict()

        poverty = self.poverty.to_dict()

        poverty_by_gender = self.poverty_by_gender.to_dict()

        poverty_by_race: Union[None, dict[str, Any]]
        if isinstance(self.poverty_by_race, PovertyRacialBreakdownWithValues):
            poverty_by_race = self.poverty_by_race.to_dict()
        else:
            poverty_by_race = self.poverty_by_race

        intra_decile = self.intra_decile.to_dict()

        wealth_decile: Union[None, dict[str, Any]]
        if isinstance(self.wealth_decile, WealthDecileImpactWithValues):
            wealth_decile = self.wealth_decile.to_dict()
        else:
            wealth_decile = self.wealth_decile

        intra_wealth_decile: Union[None, dict[str, Any]]
        if isinstance(self.intra_wealth_decile, IntraWealthDecileImpactWithValues):
            intra_wealth_decile = self.intra_wealth_decile.to_dict()
        else:
            intra_wealth_decile = self.intra_wealth_decile

        labor_supply_response = self.labor_supply_response.to_dict()

        constituency_impact: Union[None, dict[str, Any]]
        if isinstance(self.constituency_impact, UKConstituencyBreakdownWithValues):
            constituency_impact = self.constituency_impact.to_dict()
        else:
            constituency_impact = self.constituency_impact

        cliff_impact: Union[None, dict[str, Any]]
        if isinstance(self.cliff_impact, CliffImpact):
            cliff_impact = self.cliff_impact.to_dict()
        else:
            cliff_impact = self.cliff_impact

        model_version: Union[None, Unset, str]
        if isinstance(self.model_version, Unset):
            model_version = UNSET
        else:
            model_version = self.model_version

        data_version: Union[None, Unset, str]
        if isinstance(self.data_version, Unset):
            data_version = UNSET
        else:
            data_version = self.data_version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "budget": budget,
                "detailed_budget": detailed_budget,
                "decile": decile,
                "inequality": inequality,
                "poverty": poverty,
                "poverty_by_gender": poverty_by_gender,
                "poverty_by_race": poverty_by_race,
                "intra_decile": intra_decile,
                "wealth_decile": wealth_decile,
                "intra_wealth_decile": intra_wealth_decile,
                "labor_supply_response": labor_supply_response,
                "constituency_impact": constituency_impact,
                "cliff_impact": cliff_impact,
            }
        )
        if model_version is not UNSET:
            field_dict["model_version"] = model_version
        if data_version is not UNSET:
            field_dict["data_version"] = data_version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.budgetary_impact import BudgetaryImpact
        from ..models.cliff_impact import CliffImpact
        from ..models.decile_impact import DecileImpact
        from ..models.economy_comparison_detailed_budget_type_0 import EconomyComparisonDetailedBudgetType0
        from ..models.inequality_impact import InequalityImpact
        from ..models.intra_decile_impact import IntraDecileImpact
        from ..models.intra_wealth_decile_impact_with_values import IntraWealthDecileImpactWithValues
        from ..models.labor_supply_response import LaborSupplyResponse
        from ..models.poverty_gender_breakdown import PovertyGenderBreakdown
        from ..models.poverty_impact import PovertyImpact
        from ..models.poverty_racial_breakdown_with_values import PovertyRacialBreakdownWithValues
        from ..models.uk_constituency_breakdown_with_values import UKConstituencyBreakdownWithValues
        from ..models.wealth_decile_impact_with_values import WealthDecileImpactWithValues

        d = dict(src_dict)
        budget = BudgetaryImpact.from_dict(d.pop("budget"))

        def _parse_detailed_budget(data: object) -> Union["EconomyComparisonDetailedBudgetType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                detailed_budget_type_0 = EconomyComparisonDetailedBudgetType0.from_dict(data)

                return detailed_budget_type_0
            except:  # noqa: E722
                pass
            return cast(Union["EconomyComparisonDetailedBudgetType0", None], data)

        detailed_budget = _parse_detailed_budget(d.pop("detailed_budget"))

        decile = DecileImpact.from_dict(d.pop("decile"))

        inequality = InequalityImpact.from_dict(d.pop("inequality"))

        poverty = PovertyImpact.from_dict(d.pop("poverty"))

        poverty_by_gender = PovertyGenderBreakdown.from_dict(d.pop("poverty_by_gender"))

        def _parse_poverty_by_race(data: object) -> Union["PovertyRacialBreakdownWithValues", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                poverty_by_race_type_0 = PovertyRacialBreakdownWithValues.from_dict(data)

                return poverty_by_race_type_0
            except:  # noqa: E722
                pass
            return cast(Union["PovertyRacialBreakdownWithValues", None], data)

        poverty_by_race = _parse_poverty_by_race(d.pop("poverty_by_race"))

        intra_decile = IntraDecileImpact.from_dict(d.pop("intra_decile"))

        def _parse_wealth_decile(data: object) -> Union["WealthDecileImpactWithValues", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                wealth_decile_type_0 = WealthDecileImpactWithValues.from_dict(data)

                return wealth_decile_type_0
            except:  # noqa: E722
                pass
            return cast(Union["WealthDecileImpactWithValues", None], data)

        wealth_decile = _parse_wealth_decile(d.pop("wealth_decile"))

        def _parse_intra_wealth_decile(data: object) -> Union["IntraWealthDecileImpactWithValues", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                intra_wealth_decile_type_0 = IntraWealthDecileImpactWithValues.from_dict(data)

                return intra_wealth_decile_type_0
            except:  # noqa: E722
                pass
            return cast(Union["IntraWealthDecileImpactWithValues", None], data)

        intra_wealth_decile = _parse_intra_wealth_decile(d.pop("intra_wealth_decile"))

        labor_supply_response = LaborSupplyResponse.from_dict(d.pop("labor_supply_response"))

        def _parse_constituency_impact(data: object) -> Union["UKConstituencyBreakdownWithValues", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                constituency_impact_type_0 = UKConstituencyBreakdownWithValues.from_dict(data)

                return constituency_impact_type_0
            except:  # noqa: E722
                pass
            return cast(Union["UKConstituencyBreakdownWithValues", None], data)

        constituency_impact = _parse_constituency_impact(d.pop("constituency_impact"))

        def _parse_cliff_impact(data: object) -> Union["CliffImpact", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                cliff_impact_type_0 = CliffImpact.from_dict(data)

                return cliff_impact_type_0
            except:  # noqa: E722
                pass
            return cast(Union["CliffImpact", None], data)

        cliff_impact = _parse_cliff_impact(d.pop("cliff_impact"))

        def _parse_model_version(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        model_version = _parse_model_version(d.pop("model_version", UNSET))

        def _parse_data_version(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        data_version = _parse_data_version(d.pop("data_version", UNSET))

        economy_comparison = cls(
            budget=budget,
            detailed_budget=detailed_budget,
            decile=decile,
            inequality=inequality,
            poverty=poverty,
            poverty_by_gender=poverty_by_gender,
            poverty_by_race=poverty_by_race,
            intra_decile=intra_decile,
            wealth_decile=wealth_decile,
            intra_wealth_decile=intra_wealth_decile,
            labor_supply_response=labor_supply_response,
            constituency_impact=constituency_impact,
            cliff_impact=cliff_impact,
            model_version=model_version,
            data_version=data_version,
        )

        economy_comparison.additional_properties = d
        return economy_comparison

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
