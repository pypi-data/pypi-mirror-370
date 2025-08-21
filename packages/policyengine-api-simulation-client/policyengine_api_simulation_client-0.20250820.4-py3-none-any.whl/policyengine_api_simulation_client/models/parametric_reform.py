from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.parameter_change_dict import ParameterChangeDict


T = TypeVar("T", bound="ParametricReform")


@_attrs_define
class ParametricReform:
    """A reform that just changes parameter values.

    This is a dict that equates a parameter name to either a single value or a dict of changes.

    """

    additional_properties: dict[str, Union["ParameterChangeDict", Any]] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.parameter_change_dict import ParameterChangeDict

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            if isinstance(prop, ParameterChangeDict):
                field_dict[prop_name] = prop.to_dict()
            else:
                field_dict[prop_name] = prop

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.parameter_change_dict import ParameterChangeDict

        d = dict(src_dict)
        parametric_reform = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():

            def _parse_additional_property(data: object) -> Union["ParameterChangeDict", Any]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    additional_property_type_1 = ParameterChangeDict.from_dict(data)

                    return additional_property_type_1
                except:  # noqa: E722
                    pass
                return cast(Union["ParameterChangeDict", Any], data)

            additional_property = _parse_additional_property(prop_dict)

            additional_properties[prop_name] = additional_property

        parametric_reform.additional_properties = additional_properties
        return parametric_reform

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Union["ParameterChangeDict", Any]:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Union["ParameterChangeDict", Any]) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
