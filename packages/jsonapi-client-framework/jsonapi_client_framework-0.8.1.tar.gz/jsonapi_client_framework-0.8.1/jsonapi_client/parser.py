from typing import Any, cast

Json = dict[str, Any] | list[dict[str, Any]]

class JsonAPIParser:
    @classmethod
    def parse(
        cls,
        *,
        data: Json,
        included: list[dict[str, Any]] | None = None,
        parsed_by_type_and_id: dict[str, dict[str, Json]] | None = None,
        **__: dict[str, Any],
    ) -> Json:
        included = included or []
        parsed_by_type_and_id = parsed_by_type_and_id or {}
        if isinstance(data, list):
            return cast(
                "list[dict[str, Any]]",
                [cls.parse(data=item, included=included, parsed_by_type_and_id=parsed_by_type_and_id) for item in data],
            )

        parsed = {"id": data["id"]}
        parsed_by_type = parsed_by_type_and_id.setdefault(data["type"], {})
        parsed_by_type[data["id"]] = parsed
        parsed.update(data["attributes"])
        if data.get("relationships", None):
            parsed.update(
                {
                    key: cls.parse_relationship(key, value["data"], included, parsed_by_type_and_id)
                    for key, value in data["relationships"].items()
                },
            )
        return parsed

    @classmethod
    def parse_relationship(
        cls,
        key: str,
        data: Json | None,
        included: list[dict[str, Any]],
        parsed_by_type_and_id: dict[str, dict[str, Json]],
    ) -> Json | None:
        if data is None:
            return None

        if isinstance(data, list):
            return cast(
                "list[dict[str, Any]]",
                [cls.parse_relationship(key, d, included, parsed_by_type_and_id) for d in data],
            )

        cached = parsed_by_type_and_id.get(data["type"], {}).get(data["id"], None)
        if cached:
            return cached

        included_data = cls.find_included_data(data, included)
        if included_data:
            return cls.parse(data=included_data, included=included, parsed_by_type_and_id=parsed_by_type_and_id)

        return data

    @classmethod
    def find_included_data(
        cls,
        identifier: dict[str, Any],
        included: list[dict[str, Any]],
    ) -> Json | None:
        for element in included:
            if element["id"] == identifier["id"] and element["type"] == identifier["type"]:
                return element

        return None
