from typing import Any, Generic, TypeVar, cast


from .query import JsonAPIIncludeValue, JsonAPIQuery
from .client import JsonAPIClient
from .schema import JsonAPIResourceSchema
from .serializer import JsonAPISerializer, JsonType

T = TypeVar("T", bound=JsonAPIResourceSchema)


class JsonAPIResource(Generic[T]):
    def __init__(self, client: JsonAPIClient, *, include: JsonAPIIncludeValue | None = None) -> None:
        self.client = client
        self.include = include

    def get(self) -> T:
        query = JsonAPIQuery(include=self.include)
        return cast("T", self.client.get(query.to_request_params())[0])

    def update(self, **kwargs: list[Any] | dict[str, Any] | JsonType) -> T:
        query = JsonAPIQuery(include=self.include)
        payload = JsonAPISerializer.tojsonapi(**kwargs)
        return cast("T", self.client.put(payload, query.to_request_params())[0])

    def delete(self) -> None:
        self.client.delete()

