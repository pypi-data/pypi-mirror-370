from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.release_metadata_obj_result_item_type_0 import ReleaseMetadataObjResultItemType0


T = TypeVar("T", bound="ReleaseMetadataObj")


@_attrs_define
class ReleaseMetadataObj:
    """
    Attributes:
        result (list[Union['ReleaseMetadataObjResultItemType0', None]]):
    """

    result: list[Union["ReleaseMetadataObjResultItemType0", None]]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.release_metadata_obj_result_item_type_0 import ReleaseMetadataObjResultItemType0

        result = []
        for result_item_data in self.result:
            result_item: Union[None, dict[str, Any]]
            if isinstance(result_item_data, ReleaseMetadataObjResultItemType0):
                result_item = result_item_data.to_dict()
            else:
                result_item = result_item_data
            result.append(result_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "result": result,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.release_metadata_obj_result_item_type_0 import ReleaseMetadataObjResultItemType0

        d = src_dict.copy()
        result = []
        _result = d.pop("result")
        for result_item_data in _result:

            def _parse_result_item(data: object) -> Union["ReleaseMetadataObjResultItemType0", None]:
                if data is None:
                    return data
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    result_item_type_0 = ReleaseMetadataObjResultItemType0.from_dict(data)

                    return result_item_type_0
                except:  # noqa: E722
                    pass
                return cast(Union["ReleaseMetadataObjResultItemType0", None], data)

            result_item = _parse_result_item(result_item_data)

            result.append(result_item)

        release_metadata_obj = cls(
            result=result,
        )

        release_metadata_obj.additional_properties = d
        return release_metadata_obj

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
