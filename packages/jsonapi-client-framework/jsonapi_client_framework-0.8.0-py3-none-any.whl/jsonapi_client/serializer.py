from datetime import date, datetime
from typing import Any

JsonType = int | float | str | bool | date | datetime | None


class JsonAPISerializer:
    @classmethod
    def tojsonapi(cls, **kwargs: list[Any] | dict[str, Any] | JsonType) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for key, value in kwargs.items():
            cls.populate_value(data, key, value)
        return {"data": data}

    @classmethod
    def populate_value(
        cls,
        data: dict[str, Any],
        key: str,
        value: list[Any] | dict[str, Any] | JsonType,
    ) -> None:
        if isinstance(value, list) and isinstance(value[0], dict) and "id" in value[0]:
            relationships = data.setdefault("relationships", {})
            relationship = relationships.setdefault(key, {})
            relationship_data = relationship.setdefault("data", [])
            for item in value:
                if item["id"] is not None:
                    relationship_data.append(item)
            return

        if isinstance(value, dict) and "id" in value:
            relationships = data.setdefault("relationships", {})
            relationship = relationships.setdefault(key, {})
            relationship_data = relationship.get("data", None)
            if relationship_data is None:
                relationship["data"] = value
            if value["id"] is None:
                relationship["data"] = None
            if isinstance(relationship_data, list):
                relationship_data.append(value)
            return

        attributes = data.setdefault("attributes", {})
        attribute = attributes.get(key, None)
        if attribute is None:
            attributes[key] = value
        if isinstance(attribute, list):
            attribute.append(value)
