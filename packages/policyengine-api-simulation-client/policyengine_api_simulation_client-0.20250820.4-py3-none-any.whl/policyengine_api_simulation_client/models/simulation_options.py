from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.simulation_options_country import SimulationOptionsCountry
from ..models.simulation_options_scope import SimulationOptionsScope
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.parametric_reform import ParametricReform
    from ..models.simulation_options_data_type_1 import SimulationOptionsDataType1


T = TypeVar("T", bound="SimulationOptions")


@_attrs_define
class SimulationOptions:
    """
    Attributes:
        country (SimulationOptionsCountry): The country to simulate.
        scope (SimulationOptionsScope): The scope of the simulation.
        data (Union['SimulationOptionsDataType1', Any, None, Unset, str]): The data to simulate.
        time_period (Union[Unset, int]): The time period to simulate. Default: 2025.
        reform (Union['ParametricReform', Any, None, Unset]): The reform to simulate.
        baseline (Union['ParametricReform', Any, None, Unset]): The baseline to simulate.
        region (Union[None, Unset, str]): The region to simulate within the country.
        subsample (Union[None, Unset, int]): How many, if a subsample, households to randomly simulate.
        title (Union[None, Unset, str]): The title of the analysis (for charts). If not provided, a default title will
            be generated. Default: '[Analysis title]'.
        include_cliffs (Union[None, Unset, bool]): Whether to include tax-benefit cliffs in the simulation analyses. If
            True, cliffs will be included. Default: False.
        model_version (Union[None, Unset, str]): The version of the country model used in the simulation. If not
            provided, the current package version will be used. If provided, this package will throw an error if the package
            version does not match. Use this as an extra safety check.
        data_version (Union[None, Unset, str]): The version of the data used in the simulation. If not provided, the
            current data version will be used. If provided, this package will throw an error if the data version does not
            match. Use this as an extra safety check.
    """

    country: SimulationOptionsCountry
    scope: SimulationOptionsScope
    data: Union["SimulationOptionsDataType1", Any, None, Unset, str] = UNSET
    time_period: Union[Unset, int] = 2025
    reform: Union["ParametricReform", Any, None, Unset] = UNSET
    baseline: Union["ParametricReform", Any, None, Unset] = UNSET
    region: Union[None, Unset, str] = UNSET
    subsample: Union[None, Unset, int] = UNSET
    title: Union[None, Unset, str] = "[Analysis title]"
    include_cliffs: Union[None, Unset, bool] = False
    model_version: Union[None, Unset, str] = UNSET
    data_version: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.parametric_reform import ParametricReform
        from ..models.simulation_options_data_type_1 import SimulationOptionsDataType1

        country = self.country.value

        scope = self.scope.value

        data: Union[Any, None, Unset, dict[str, Any], str]
        if isinstance(self.data, Unset):
            data = UNSET
        elif isinstance(self.data, SimulationOptionsDataType1):
            data = self.data.to_dict()
        else:
            data = self.data

        time_period = self.time_period

        reform: Union[Any, None, Unset, dict[str, Any]]
        if isinstance(self.reform, Unset):
            reform = UNSET
        elif isinstance(self.reform, ParametricReform):
            reform = self.reform.to_dict()
        else:
            reform = self.reform

        baseline: Union[Any, None, Unset, dict[str, Any]]
        if isinstance(self.baseline, Unset):
            baseline = UNSET
        elif isinstance(self.baseline, ParametricReform):
            baseline = self.baseline.to_dict()
        else:
            baseline = self.baseline

        region: Union[None, Unset, str]
        if isinstance(self.region, Unset):
            region = UNSET
        else:
            region = self.region

        subsample: Union[None, Unset, int]
        if isinstance(self.subsample, Unset):
            subsample = UNSET
        else:
            subsample = self.subsample

        title: Union[None, Unset, str]
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        include_cliffs: Union[None, Unset, bool]
        if isinstance(self.include_cliffs, Unset):
            include_cliffs = UNSET
        else:
            include_cliffs = self.include_cliffs

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
                "country": country,
                "scope": scope,
            }
        )
        if data is not UNSET:
            field_dict["data"] = data
        if time_period is not UNSET:
            field_dict["time_period"] = time_period
        if reform is not UNSET:
            field_dict["reform"] = reform
        if baseline is not UNSET:
            field_dict["baseline"] = baseline
        if region is not UNSET:
            field_dict["region"] = region
        if subsample is not UNSET:
            field_dict["subsample"] = subsample
        if title is not UNSET:
            field_dict["title"] = title
        if include_cliffs is not UNSET:
            field_dict["include_cliffs"] = include_cliffs
        if model_version is not UNSET:
            field_dict["model_version"] = model_version
        if data_version is not UNSET:
            field_dict["data_version"] = data_version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.parametric_reform import ParametricReform
        from ..models.simulation_options_data_type_1 import SimulationOptionsDataType1

        d = dict(src_dict)
        country = SimulationOptionsCountry(d.pop("country"))

        scope = SimulationOptionsScope(d.pop("scope"))

        def _parse_data(data: object) -> Union["SimulationOptionsDataType1", Any, None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_1 = SimulationOptionsDataType1.from_dict(data)

                return data_type_1
            except:  # noqa: E722
                pass
            return cast(Union["SimulationOptionsDataType1", Any, None, Unset, str], data)

        data = _parse_data(d.pop("data", UNSET))

        time_period = d.pop("time_period", UNSET)

        def _parse_reform(data: object) -> Union["ParametricReform", Any, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                reform_type_0 = ParametricReform.from_dict(data)

                return reform_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ParametricReform", Any, None, Unset], data)

        reform = _parse_reform(d.pop("reform", UNSET))

        def _parse_baseline(data: object) -> Union["ParametricReform", Any, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                baseline_type_0 = ParametricReform.from_dict(data)

                return baseline_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ParametricReform", Any, None, Unset], data)

        baseline = _parse_baseline(d.pop("baseline", UNSET))

        def _parse_region(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        region = _parse_region(d.pop("region", UNSET))

        def _parse_subsample(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        subsample = _parse_subsample(d.pop("subsample", UNSET))

        def _parse_title(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        title = _parse_title(d.pop("title", UNSET))

        def _parse_include_cliffs(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        include_cliffs = _parse_include_cliffs(d.pop("include_cliffs", UNSET))

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

        simulation_options = cls(
            country=country,
            scope=scope,
            data=data,
            time_period=time_period,
            reform=reform,
            baseline=baseline,
            region=region,
            subsample=subsample,
            title=title,
            include_cliffs=include_cliffs,
            model_version=model_version,
            data_version=data_version,
        )

        simulation_options.additional_properties = d
        return simulation_options

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
