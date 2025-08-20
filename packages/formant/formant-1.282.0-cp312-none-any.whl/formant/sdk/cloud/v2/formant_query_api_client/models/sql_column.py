from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="SqlColumn")

@attr.s(auto_attribs=True)
class SqlColumn:
    """
    Attributes:
        name (str):
        data_type (str):
        is_nullable (bool):
        table_name (str):
    """

    name: str
    data_type: str
    is_nullable: bool
    table_name: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        data_type = self.data_type
        is_nullable = self.is_nullable
        table_name = self.table_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "dataType": data_type,
            "isNullable": is_nullable,
            "tableName": table_name,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        data_type = d.pop("dataType")

        is_nullable = d.pop("isNullable")

        table_name = d.pop("tableName")

        sql_column = cls(
            name=name,
            data_type=data_type,
            is_nullable=is_nullable,
            table_name=table_name,
        )

        sql_column.additional_properties = d
        return sql_column

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
