from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserPrivate")


@_attrs_define
class UserPrivate:
    """
    Attributes:
        username (Union[Unset, str]):
        id (Union[None, Unset, int]):
        auth0_sub (Union[Unset, str]):
    """

    username: Union[Unset, str] = UNSET
    id: Union[None, Unset, int] = UNSET
    auth0_sub: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        username = self.username

        id: Union[None, Unset, int]
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        auth0_sub = self.auth0_sub

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if username is not UNSET:
            field_dict["username"] = username
        if id is not UNSET:
            field_dict["id"] = id
        if auth0_sub is not UNSET:
            field_dict["auth0_sub"] = auth0_sub

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        username = d.pop("username", UNSET)

        def _parse_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        id = _parse_id(d.pop("id", UNSET))

        auth0_sub = d.pop("auth0_sub", UNSET)

        user_private = cls(
            username=username,
            id=id,
            auth0_sub=auth0_sub,
        )

        user_private.additional_properties = d
        return user_private

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
