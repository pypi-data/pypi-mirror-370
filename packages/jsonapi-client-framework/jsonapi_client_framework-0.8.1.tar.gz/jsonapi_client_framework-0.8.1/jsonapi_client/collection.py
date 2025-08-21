from abc import ABC
from typing import Any, Generic, TypeVar
from urllib.parse import quote

from requests.auth import AuthBase  # type: ignore[import-untyped]

from .query import JsonAPIFilterValue, JsonAPIIncludeValue, JsonAPIQuery, JsonAPISortValue
from .client import JsonAPIClient
from .resource import JsonAPIResource
from .resources_list import JsonAPIResourcesList
from .schema import JsonAPIResourceSchema
from .serializer import JsonAPISerializer, JsonType

T = TypeVar("T", bound=JsonAPIResourceSchema)


class JsonAPISingleton(ABC, Generic[T]):
    endpoint: str
    schema: type[JsonAPIResourceSchema]

    def __init__(self, base_url: str, auth: AuthBase | None = None, include: JsonAPIIncludeValue | None = None) -> None:
        self.base_url = base_url
        self.auth = auth
        self.include = include

    def resource(self) -> JsonAPIResource[T]:
        url = f"{self.base_url}{self.endpoint}"
        client = JsonAPIClient[T](url=url, schema=self.schema, auth=self.auth)
        return JsonAPIResource[T](client, include=self.include)


class JsonAPICollection(ABC, Generic[T]):
    endpoint: str
    schema: type[JsonAPIResourceSchema]

    def __init__(
        self,
        base_url: str,
        auth: AuthBase | None = None,
        default_page_size: int | None = None,
        include: JsonAPIIncludeValue | None = None,
    ) -> None:
        self.base_url = base_url
        self.auth = auth
        self.default_page_size = default_page_size
        self.include = include

    def resource(self, resource_id: str) -> JsonAPIResource[T]:
        url = f"{self.base_url}{self.endpoint}/{quote(resource_id)}"
        client = JsonAPIClient[T](url=url, schema=self.schema, auth=self.auth)
        return JsonAPIResource[T](client, include=self.include)

    def create(self, **kwargs: list[Any] | dict[str, Any] | JsonType) -> T:
        url = f"{self.base_url}{self.endpoint}"
        client = JsonAPIClient[T](url=url, schema=self.schema, auth=self.auth)
        query = JsonAPIQuery(include=self.include)
        payload = JsonAPISerializer.tojsonapi(**kwargs)
        return client.post(payload, query.to_request_params())[0]

    def list(
        self,
        filters: dict[str, JsonAPIFilterValue] | None = None,
        sort: JsonAPISortValue | None = None,
        extra_params: dict[str, str] | None = None,
    ) -> JsonAPIResourcesList[T]:
        url = f"{self.base_url}{self.endpoint}"
        client = JsonAPIClient[T](url=url, schema=self.schema, auth=self.auth)
        return JsonAPIResourcesList[T](
            client=client,
            default_page_size=self.default_page_size,
            filters=filters,
            sort=sort,
            include=self.include,
            extra_params=extra_params,
        )

