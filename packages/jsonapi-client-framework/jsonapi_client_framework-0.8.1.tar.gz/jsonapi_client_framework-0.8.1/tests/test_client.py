
from pathlib import Path

from unittest.mock import MagicMock, patch
from dataclasses import dataclass

from unittest import TestCase

from requests import Response  # type: ignore[import-untyped]

from jsonapi_client import JsonAPIResourceSchema
from jsonapi_client.client import JsonAPIClient


@dataclass
class Person(JsonAPIResourceSchema):
    full_name: str


@dataclass
class Movie(JsonAPIResourceSchema):
    title: str
    year: int
    # By default, the Json:API payload contain the identifer only (id and type)
    director: Person


@dataclass
class Series(JsonAPIResourceSchema):
    title: str
    seasons: int


class TestClient(TestCase):
    @patch("jsonapi_client.client.request")
    def test_get(self, test_request: MagicMock) -> None:
        client: JsonAPIClient = JsonAPIClient(url="http://example.com/api", schema=Movie, auth=None)
        fixture = Path("tests/fixtures/movies.json")
        response = Response()
        response.status_code = 200
        response._content = fixture.read_bytes()
        test_request.return_value = response

        result, meta = client.get()

        self.assertEqual(len(result), 2)
        self.assertEqual(meta["total"], 2)
        self.assertEqual(result[0].title, "Das weiße Band - Eine deutsche Kindergeschichte")
        self.assertEqual(result[0].year, 2009)
        self.assertEqual(result[0].director.full_name, "Michael Haneke")
        self.assertEqual(result[1].title, "Funny Games")
        self.assertEqual(result[1].year, 1997)
        self.assertEqual(result[1].director.full_name, "Michael Haneke")

    @patch("jsonapi_client.client.request")
    def test_get_polymorphic(self, test_request: MagicMock) -> None:
        client: JsonAPIClient = JsonAPIClient(url="http://example.com/api", schema=Movie | Series, auth=None)
        fixture = Path("tests/fixtures/media.json")
        response = Response()
        response.status_code = 200
        response._content = fixture.read_bytes()
        test_request.return_value = response

        result, meta = client.get()

        self.assertEqual(len(result), 2)
        self.assertEqual(meta["total"], 2)
        self.assertIsInstance(result[0], Movie)
        self.assertIsInstance(result[1], Series)

