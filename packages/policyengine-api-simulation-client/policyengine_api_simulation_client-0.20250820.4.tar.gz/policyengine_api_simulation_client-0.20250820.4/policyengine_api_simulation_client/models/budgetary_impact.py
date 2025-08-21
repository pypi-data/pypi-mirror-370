from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="BudgetaryImpact")


@_attrs_define
class BudgetaryImpact:
    """
    Attributes:
        budgetary_impact (float):
        tax_revenue_impact (float):
        state_tax_revenue_impact (float):
        benefit_spending_impact (float):
        households (float):
        baseline_net_income (float):
    """

    budgetary_impact: float
    tax_revenue_impact: float
    state_tax_revenue_impact: float
    benefit_spending_impact: float
    households: float
    baseline_net_income: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        budgetary_impact = self.budgetary_impact

        tax_revenue_impact = self.tax_revenue_impact

        state_tax_revenue_impact = self.state_tax_revenue_impact

        benefit_spending_impact = self.benefit_spending_impact

        households = self.households

        baseline_net_income = self.baseline_net_income

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "budgetary_impact": budgetary_impact,
                "tax_revenue_impact": tax_revenue_impact,
                "state_tax_revenue_impact": state_tax_revenue_impact,
                "benefit_spending_impact": benefit_spending_impact,
                "households": households,
                "baseline_net_income": baseline_net_income,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        budgetary_impact = d.pop("budgetary_impact")

        tax_revenue_impact = d.pop("tax_revenue_impact")

        state_tax_revenue_impact = d.pop("state_tax_revenue_impact")

        benefit_spending_impact = d.pop("benefit_spending_impact")

        households = d.pop("households")

        baseline_net_income = d.pop("baseline_net_income")

        budgetary_impact = cls(
            budgetary_impact=budgetary_impact,
            tax_revenue_impact=tax_revenue_impact,
            state_tax_revenue_impact=state_tax_revenue_impact,
            benefit_spending_impact=benefit_spending_impact,
            households=households,
            baseline_net_income=baseline_net_income,
        )

        budgetary_impact.additional_properties = d
        return budgetary_impact

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
