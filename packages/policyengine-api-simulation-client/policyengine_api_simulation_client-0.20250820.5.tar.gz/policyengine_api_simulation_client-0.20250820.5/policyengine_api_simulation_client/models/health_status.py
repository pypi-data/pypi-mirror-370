from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.system_status import SystemStatus


T = TypeVar("T", bound="HealthStatus")


@_attrs_define
class HealthStatus:
    """
    Attributes:
        healthy (bool):
        systems (list['SystemStatus']):
    """

    healthy: bool
    systems: list["SystemStatus"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        healthy = self.healthy

        systems = []
        for systems_item_data in self.systems:
            systems_item = systems_item_data.to_dict()
            systems.append(systems_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "healthy": healthy,
                "systems": systems,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.system_status import SystemStatus

        d = dict(src_dict)
        healthy = d.pop("healthy")

        systems = []
        _systems = d.pop("systems")
        for systems_item_data in _systems:
            systems_item = SystemStatus.from_dict(systems_item_data)

            systems.append(systems_item)

        health_status = cls(
            healthy=healthy,
            systems=systems,
        )

        health_status.additional_properties = d
        return health_status

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
