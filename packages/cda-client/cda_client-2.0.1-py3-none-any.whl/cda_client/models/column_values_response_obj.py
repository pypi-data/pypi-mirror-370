from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.column_values_response_obj_result_item_type_0 import ColumnValuesResponseObjResultItemType0


T = TypeVar("T", bound="ColumnValuesResponseObj")


@_attrs_define
class ColumnValuesResponseObj:
    """
    Attributes:
        result (list[Union['ColumnValuesResponseObjResultItemType0', None]]): List of query result json objects
        query_sql (Union[None, str]): SQL Query generated to yield the results
        total_row_count (Union[None, Unset, int]): Count of total number of results from the query
        next_url (Union[None, Unset, str]): URL to get to next page of results
    """

    result: list[Union["ColumnValuesResponseObjResultItemType0", None]]
    query_sql: Union[None, str]
    total_row_count: Union[None, Unset, int] = UNSET
    next_url: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.column_values_response_obj_result_item_type_0 import ColumnValuesResponseObjResultItemType0

        result = []
        for result_item_data in self.result:
            result_item: Union[None, dict[str, Any]]
            if isinstance(result_item_data, ColumnValuesResponseObjResultItemType0):
                result_item = result_item_data.to_dict()
            else:
                result_item = result_item_data
            result.append(result_item)

        query_sql: Union[None, str]
        query_sql = self.query_sql

        total_row_count: Union[None, Unset, int]
        if isinstance(self.total_row_count, Unset):
            total_row_count = UNSET
        else:
            total_row_count = self.total_row_count

        next_url: Union[None, Unset, str]
        if isinstance(self.next_url, Unset):
            next_url = UNSET
        else:
            next_url = self.next_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "result": result,
                "query_sql": query_sql,
            }
        )
        if total_row_count is not UNSET:
            field_dict["total_row_count"] = total_row_count
        if next_url is not UNSET:
            field_dict["next_url"] = next_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.column_values_response_obj_result_item_type_0 import ColumnValuesResponseObjResultItemType0

        d = src_dict.copy()
        result = []
        _result = d.pop("result")
        for result_item_data in _result:

            def _parse_result_item(data: object) -> Union["ColumnValuesResponseObjResultItemType0", None]:
                if data is None:
                    return data
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    result_item_type_0 = ColumnValuesResponseObjResultItemType0.from_dict(data)

                    return result_item_type_0
                except:  # noqa: E722
                    pass
                return cast(Union["ColumnValuesResponseObjResultItemType0", None], data)

            result_item = _parse_result_item(result_item_data)

            result.append(result_item)

        def _parse_query_sql(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        query_sql = _parse_query_sql(d.pop("query_sql"))

        def _parse_total_row_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        total_row_count = _parse_total_row_count(d.pop("total_row_count", UNSET))

        def _parse_next_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        next_url = _parse_next_url(d.pop("next_url", UNSET))

        column_values_response_obj = cls(
            result=result,
            query_sql=query_sql,
            total_row_count=total_row_count,
            next_url=next_url,
        )

        column_values_response_obj.additional_properties = d
        return column_values_response_obj

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
