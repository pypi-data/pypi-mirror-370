from types import UnionType
from typing import Any, Generic, TypeVar, cast, get_args

import jsonpickle  # type: ignore[import-untyped]
from requests import request  # type: ignore[import-untyped]
from requests.auth import AuthBase  # type: ignore[import-untyped]
from requests.models import Response  # type: ignore[import-untyped]

from .parser import JsonAPIParser
from .schema import JsonAPIResourceSchema, JsonAPIError

T = TypeVar("T", bound=JsonAPIResourceSchema)

DEFAULT_TIMEOUT = 10  # seconds
HTTP_422_UNPROCESSABLE_ENTITY = 422

def handle_status_code(response: Response) -> None:
    """
    Handle API status codes.

    Raises:
        APIError: If the response status code is 422.

    """
    if response.status_code == HTTP_422_UNPROCESSABLE_ENTITY:
        jsonapi_errors = [cast("Any", JsonAPIError).from_dict(e) for e in response.json()["errors"]]
        raise APIError(response.status_code, jsonapi_errors)

    response.raise_for_status()


class APIError(Exception):
    """Exception raised for error responses from the API."""

    def __init__(self, status_code: int, jsonapi_errors: list[JsonAPIError]) -> None:
        self.status_code = status_code
        self.jsonapi_errors = jsonapi_errors
        super().__init__(f"API responded with status code {status_code}")


class JsonAPIClient(Generic[T]):
    def __init__(self, url: str, schema: type[JsonAPIResourceSchema] | UnionType, auth: AuthBase | None = None) -> None:
        self.url = url
        self.schema = schema
        self.auth = auth

    def get(self, params: dict[str, Any] | None = None) -> tuple[T | list[T], dict[str, Any]]:
        response = self.__perform_request("GET", params)
        return self.__deserialize_payload(response)

    def post(self, payload: dict[str, Any], params: dict[str, Any] | None = None) -> tuple[T, dict[str, Any]]:
        response = self.__perform_request("POST", params, payload)
        resource, meta = self.__deserialize_payload(response)
        return cast("T", resource), meta

    def put(self, payload: dict[str, Any], params: dict[str, Any] | None = None) -> tuple[T, dict[str, Any]]:
        response = self.__perform_request("PUT", params, payload)
        resource, meta = self.__deserialize_payload(response)
        return cast("T", resource), meta

    def delete(self) -> None:
        self.__perform_request("DELETE")

    def __perform_request(
      self,
      method: str,
      params: dict[str, Any] | None = None,
      payload: dict[str, Any] | None = None
    ) -> Response:
        body = None if payload is None else jsonpickle.encode(payload, unpicklable=False)
        response = request(
          method=method,
          url=self.url,
          auth=self.auth,
          params=params,
          data=body,
          headers={"Content-Type": "application/json"},
          timeout=DEFAULT_TIMEOUT,
        )
        handle_status_code(response)
        return response

    def __deserialize_payload(self, response: Response) -> tuple[T | list[T], dict[str, Any]]:
        json = response.json()
        parsed = JsonAPIParser().parse(**json)
        meta = cast("dict[str, Any]", json["meta"])
        if isinstance(parsed, list):
            results = [self.__deserializer_resource(r) for r in parsed]
            return results, meta

        return self.__deserializer_resource(parsed), meta

    def __deserializer_resource(self, jsonapi_resource: dict[str, Any]) -> T:
        if isinstance(self.schema, UnionType):
            for schema_type in get_args(self.schema):
                try:
                    return cast("T", cast("Any", schema_type).from_dict(jsonapi_resource))
                except KeyError as e:
                    last_error = e
                    pass
            raise last_error

        return cast("T", cast("Any", self.schema).from_dict(jsonapi_resource))
