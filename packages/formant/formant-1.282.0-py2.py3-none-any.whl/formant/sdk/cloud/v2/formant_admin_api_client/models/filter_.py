from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.filter_types_item import FilterTypesItem
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.tag_sets import TagSets




T = TypeVar("T", bound="Filter")

@attr.s(auto_attribs=True)
class Filter:
    """
    Attributes:
        device_ids (Union[Unset, List[str]]):
        names (Union[Unset, List[str]]):
        types (Union[Unset, List[FilterTypesItem]]):
        not_tags (Union[Unset, List['TagSets']]): One or more TagSets (combined with OR logic)
        not_names (Union[Unset, List[str]]):
        agent_ids (Union[Unset, List[str]]):
        tags (Union[Unset, List['TagSets']]): One or more TagSets (combined with OR logic)
    """

    device_ids: Union[Unset, List[str]] = UNSET
    names: Union[Unset, List[str]] = UNSET
    types: Union[Unset, List[FilterTypesItem]] = UNSET
    not_tags: Union[Unset, List['TagSets']] = UNSET
    not_names: Union[Unset, List[str]] = UNSET
    agent_ids: Union[Unset, List[str]] = UNSET
    tags: Union[Unset, List['TagSets']] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        device_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.device_ids, Unset):
            device_ids = self.device_ids




        names: Union[Unset, List[str]] = UNSET
        if not isinstance(self.names, Unset):
            names = self.names




        types: Union[Unset, List[str]] = UNSET
        if not isinstance(self.types, Unset):
            types = []
            for types_item_data in self.types:
                types_item = types_item_data.value

                types.append(types_item)




        not_tags: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.not_tags, Unset):
            not_tags = []
            for not_tags_item_data in self.not_tags:
                not_tags_item = not_tags_item_data.to_dict()

                not_tags.append(not_tags_item)




        not_names: Union[Unset, List[str]] = UNSET
        if not isinstance(self.not_names, Unset):
            not_names = self.not_names




        agent_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.agent_ids, Unset):
            agent_ids = self.agent_ids




        tags: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = []
            for tags_item_data in self.tags:
                tags_item = tags_item_data.to_dict()

                tags.append(tags_item)





        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if device_ids is not UNSET:
            field_dict["deviceIds"] = device_ids
        if names is not UNSET:
            field_dict["names"] = names
        if types is not UNSET:
            field_dict["types"] = types
        if not_tags is not UNSET:
            field_dict["notTags"] = not_tags
        if not_names is not UNSET:
            field_dict["notNames"] = not_names
        if agent_ids is not UNSET:
            field_dict["agentIds"] = agent_ids
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.tag_sets import TagSets
        d = src_dict.copy()
        device_ids = cast(List[str], d.pop("deviceIds", UNSET))


        names = cast(List[str], d.pop("names", UNSET))


        types = []
        _types = d.pop("types", UNSET)
        for types_item_data in (_types or []):
            types_item = FilterTypesItem(types_item_data)



            types.append(types_item)


        not_tags = []
        _not_tags = d.pop("notTags", UNSET)
        for not_tags_item_data in (_not_tags or []):
            not_tags_item = TagSets.from_dict(not_tags_item_data)



            not_tags.append(not_tags_item)


        not_names = cast(List[str], d.pop("notNames", UNSET))


        agent_ids = cast(List[str], d.pop("agentIds", UNSET))


        tags = []
        _tags = d.pop("tags", UNSET)
        for tags_item_data in (_tags or []):
            tags_item = TagSets.from_dict(tags_item_data)



            tags.append(tags_item)


        filter_ = cls(
            device_ids=device_ids,
            names=names,
            types=types,
            not_tags=not_tags,
            not_names=not_names,
            agent_ids=agent_ids,
            tags=tags,
        )

        filter_.additional_properties = d
        return filter_

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
