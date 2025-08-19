from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SummaryRequestBody")


@_attrs_define
class SummaryRequestBody:
    """
    Attributes:
        match_all (Union[None, Unset, list[str]]):
        match_some (Union[None, Unset, list[str]]):
        add_columns (Union[None, Unset, list[str]]):
        exclude_columns (Union[None, Unset, list[str]]):
    """

    match_all: Union[None, Unset, list[str]] = UNSET
    match_some: Union[None, Unset, list[str]] = UNSET
    add_columns: Union[None, Unset, list[str]] = UNSET
    exclude_columns: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        match_all: Union[None, Unset, list[str]]
        if isinstance(self.match_all, Unset):
            match_all = UNSET
        elif isinstance(self.match_all, list):
            match_all = self.match_all

        else:
            match_all = self.match_all

        match_some: Union[None, Unset, list[str]]
        if isinstance(self.match_some, Unset):
            match_some = UNSET
        elif isinstance(self.match_some, list):
            match_some = self.match_some

        else:
            match_some = self.match_some

        add_columns: Union[None, Unset, list[str]]
        if isinstance(self.add_columns, Unset):
            add_columns = UNSET
        elif isinstance(self.add_columns, list):
            add_columns = self.add_columns

        else:
            add_columns = self.add_columns

        exclude_columns: Union[None, Unset, list[str]]
        if isinstance(self.exclude_columns, Unset):
            exclude_columns = UNSET
        elif isinstance(self.exclude_columns, list):
            exclude_columns = self.exclude_columns

        else:
            exclude_columns = self.exclude_columns

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if match_all is not UNSET:
            field_dict["MATCH_ALL"] = match_all
        if match_some is not UNSET:
            field_dict["MATCH_SOME"] = match_some
        if add_columns is not UNSET:
            field_dict["ADD_COLUMNS"] = add_columns
        if exclude_columns is not UNSET:
            field_dict["EXCLUDE_COLUMNS"] = exclude_columns

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_match_all(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                match_all_type_0 = cast(list[str], data)

                return match_all_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        match_all = _parse_match_all(d.pop("MATCH_ALL", UNSET))

        def _parse_match_some(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                match_some_type_0 = cast(list[str], data)

                return match_some_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        match_some = _parse_match_some(d.pop("MATCH_SOME", UNSET))

        def _parse_add_columns(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                add_columns_type_0 = cast(list[str], data)

                return add_columns_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        add_columns = _parse_add_columns(d.pop("ADD_COLUMNS", UNSET))

        def _parse_exclude_columns(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                exclude_columns_type_0 = cast(list[str], data)

                return exclude_columns_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        exclude_columns = _parse_exclude_columns(d.pop("EXCLUDE_COLUMNS", UNSET))

        summary_request_body = cls(
            match_all=match_all,
            match_some=match_some,
            add_columns=add_columns,
            exclude_columns=exclude_columns,
        )

        summary_request_body.additional_properties = d
        return summary_request_body

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
