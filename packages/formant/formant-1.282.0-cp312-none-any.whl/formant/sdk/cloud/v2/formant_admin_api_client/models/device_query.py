import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..models.device_query_type import DeviceQueryType
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.device_details_sort import DeviceDetailsSort
  from ..models.tag_sets import TagSets




T = TypeVar("T", bound="DeviceQuery")

@attr.s(auto_attribs=True)
class DeviceQuery:
    """
    Attributes:
        external_id (Union[Unset, str]): Query devices by external ID.
        name (Union[Unset, str]): Query devices by name.
        query (Union[Unset, str]): Query partial device names with wildcard `*`.
        organization_id (Union[Unset, str]): Query devices by organization ID.
        tags (Union[Unset, List['TagSets']]): Query devices by tags.
        fleet_id (Union[Unset, None, str]): Query devices by fleet ID.
        enabled (Union[Unset, bool]): Query devices by enabled status.
        fully_configured (Union[Unset, bool]): Query devices by configured status.
        type (Union[Unset, DeviceQueryType]): Query devices by device type.
        count (Union[Unset, float]): Limit the number of devices returned by this query (max 1000).
        offset (Union[Unset, float]): Paginate the results by specifying an offset.
        created_after (Union[Unset, datetime.datetime]): Query devices created after this date.
        disabled_before (Union[Unset, datetime.datetime]): Query devices disabled (deleted) before this date.
        online (Union[Unset, bool]): Query online devices.
        fill_online_status (Union[Unset, bool]): Include device online status in the response.
        fill_last_seen (Union[Unset, bool]): Include last seen timestamp in the response.
        sort (Union[Unset, List['DeviceDetailsSort']]): Sort order for the query results.
        has_external_id (Union[Unset, bool]): Query devices that have an externalId.
    """

    external_id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    query: Union[Unset, str] = UNSET
    organization_id: Union[Unset, str] = UNSET
    tags: Union[Unset, List['TagSets']] = UNSET
    fleet_id: Union[Unset, None, str] = UNSET
    enabled: Union[Unset, bool] = UNSET
    fully_configured: Union[Unset, bool] = UNSET
    type: Union[Unset, DeviceQueryType] = UNSET
    count: Union[Unset, float] = UNSET
    offset: Union[Unset, float] = UNSET
    created_after: Union[Unset, datetime.datetime] = UNSET
    disabled_before: Union[Unset, datetime.datetime] = UNSET
    online: Union[Unset, bool] = UNSET
    fill_online_status: Union[Unset, bool] = UNSET
    fill_last_seen: Union[Unset, bool] = UNSET
    sort: Union[Unset, List['DeviceDetailsSort']] = UNSET
    has_external_id: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        external_id = self.external_id
        name = self.name
        query = self.query
        organization_id = self.organization_id
        tags: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = []
            for tags_item_data in self.tags:
                tags_item = tags_item_data.to_dict()

                tags.append(tags_item)




        fleet_id = self.fleet_id
        enabled = self.enabled
        fully_configured = self.fully_configured
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        count = self.count
        offset = self.offset
        created_after: Union[Unset, str] = UNSET
        if not isinstance(self.created_after, Unset):
            created_after = self.created_after.isoformat()

        disabled_before: Union[Unset, str] = UNSET
        if not isinstance(self.disabled_before, Unset):
            disabled_before = self.disabled_before.isoformat()

        online = self.online
        fill_online_status = self.fill_online_status
        fill_last_seen = self.fill_last_seen
        sort: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.sort, Unset):
            sort = []
            for sort_item_data in self.sort:
                sort_item = sort_item_data.to_dict()

                sort.append(sort_item)




        has_external_id = self.has_external_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if name is not UNSET:
            field_dict["name"] = name
        if query is not UNSET:
            field_dict["query"] = query
        if organization_id is not UNSET:
            field_dict["organizationId"] = organization_id
        if tags is not UNSET:
            field_dict["tags"] = tags
        if fleet_id is not UNSET:
            field_dict["fleetId"] = fleet_id
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if fully_configured is not UNSET:
            field_dict["fullyConfigured"] = fully_configured
        if type is not UNSET:
            field_dict["type"] = type
        if count is not UNSET:
            field_dict["count"] = count
        if offset is not UNSET:
            field_dict["offset"] = offset
        if created_after is not UNSET:
            field_dict["createdAfter"] = created_after
        if disabled_before is not UNSET:
            field_dict["disabledBefore"] = disabled_before
        if online is not UNSET:
            field_dict["online"] = online
        if fill_online_status is not UNSET:
            field_dict["fillOnlineStatus"] = fill_online_status
        if fill_last_seen is not UNSET:
            field_dict["fillLastSeen"] = fill_last_seen
        if sort is not UNSET:
            field_dict["sort"] = sort
        if has_external_id is not UNSET:
            field_dict["hasExternalId"] = has_external_id

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.device_details_sort import DeviceDetailsSort
        from ..models.tag_sets import TagSets
        d = src_dict.copy()
        external_id = d.pop("externalId", UNSET)

        name = d.pop("name", UNSET)

        query = d.pop("query", UNSET)

        organization_id = d.pop("organizationId", UNSET)

        tags = []
        _tags = d.pop("tags", UNSET)
        for tags_item_data in (_tags or []):
            tags_item = TagSets.from_dict(tags_item_data)



            tags.append(tags_item)


        fleet_id = d.pop("fleetId", UNSET)

        enabled = d.pop("enabled", UNSET)

        fully_configured = d.pop("fullyConfigured", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, DeviceQueryType]
        if isinstance(_type,  Unset):
            type = UNSET
        else:
            type = DeviceQueryType(_type)




        count = d.pop("count", UNSET)

        offset = d.pop("offset", UNSET)

        _created_after = d.pop("createdAfter", UNSET)
        created_after: Union[Unset, datetime.datetime]
        if isinstance(_created_after,  Unset):
            created_after = UNSET
        else:
            created_after = isoparse(_created_after)




        _disabled_before = d.pop("disabledBefore", UNSET)
        disabled_before: Union[Unset, datetime.datetime]
        if isinstance(_disabled_before,  Unset):
            disabled_before = UNSET
        else:
            disabled_before = isoparse(_disabled_before)




        online = d.pop("online", UNSET)

        fill_online_status = d.pop("fillOnlineStatus", UNSET)

        fill_last_seen = d.pop("fillLastSeen", UNSET)

        sort = []
        _sort = d.pop("sort", UNSET)
        for sort_item_data in (_sort or []):
            sort_item = DeviceDetailsSort.from_dict(sort_item_data)



            sort.append(sort_item)


        has_external_id = d.pop("hasExternalId", UNSET)

        device_query = cls(
            external_id=external_id,
            name=name,
            query=query,
            organization_id=organization_id,
            tags=tags,
            fleet_id=fleet_id,
            enabled=enabled,
            fully_configured=fully_configured,
            type=type,
            count=count,
            offset=offset,
            created_after=created_after,
            disabled_before=disabled_before,
            online=online,
            fill_online_status=fill_online_status,
            fill_last_seen=fill_last_seen,
            sort=sort,
            has_external_id=has_external_id,
        )

        device_query.additional_properties = d
        return device_query

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
