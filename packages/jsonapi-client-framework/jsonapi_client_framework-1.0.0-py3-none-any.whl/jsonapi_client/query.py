from datetime import date
from typing import Any, TypeAlias

JsonAPIFilterValue: TypeAlias = str | bool | date | list[str] | list[date]
JsonAPISortValue: TypeAlias = str | list[str]
JsonAPIIncludeValue: TypeAlias = str | list[str]


class JsonAPIQuery:
    def __init__(
        self,
        filters: dict[str, JsonAPIFilterValue] | None = None,
        page: dict[str, int] | None = None,
        sort: JsonAPISortValue | None = None,
        include: JsonAPIIncludeValue | None = None,
    ) -> None:
        self.filters = filters
        self.page = page
        self.sort = sort
        self.include = include

    def to_request_params(self) -> dict[str, Any]:
        return {
            **self.filter_params(self.filters),
            **self.sort_params(self.sort),
            **self.page_params(self.page),
            **self.include_params(self.include),
        }

    @classmethod
    def filter_params(cls, filters: dict[str, JsonAPIFilterValue] | None) -> dict[str, str]:
        if filters is None:
            return {}

        return {f"filter[{k}]": cls.to_query_param_value(v) for k, v in filters.items()}

    @classmethod
    def sort_params(cls, sort: JsonAPISortValue | None) -> dict[str, str]:
        if sort is None:
            return {}

        return {"sort": cls.to_query_param_value(sort)}

    @staticmethod
    def page_params(page: dict[str, int] | None) -> dict[str, int]:
        if page is None:
            return {}

        return {f"page[{k}]": v for k, v in page.items()}

    @classmethod
    def include_params(cls, include: JsonAPIIncludeValue | None) -> dict[str, str]:
        if include is None:
            return {}

        return {"include": cls.to_query_param_value(include)}

    @staticmethod
    def to_query_param_value(value: JsonAPIFilterValue | JsonAPISortValue) -> str:
        if isinstance(value, bool):
            return str(value).lower()

        if isinstance(value, list):
            return ",".join(map(JsonAPIQuery.to_query_param_value, value))

        return str(value)
