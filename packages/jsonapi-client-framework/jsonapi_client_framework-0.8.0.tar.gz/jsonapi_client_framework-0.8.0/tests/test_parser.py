from typing import cast
from unittest import TestCase

from jsonapi_client.parser import JsonAPIParser

class TestParser(TestCase):
    def test_parse(self) -> None:
        parsed = cast("dict", JsonAPIParser.parse(
            data={
                "id": "1",
                "type": "movie",
                "attributes": {
                    "title": "Das weiße Band - Eine deutsche Kindergeschichte",
                },
                "relationships": {
                    "director": {
                        "data": {
                            "id": "1",
                            "type": "person",
                        },
                    },
                    "characters": {
                        "data": [
                            {
                                "id": "2",
                                "type": "character",
                            },
                            {
                                "id": "3",
                                "type": "character",
                            },
                        ],
                    },
                },
            },
        ))

        self.assertEqual(parsed["id"], "1")
        self.assertEqual(parsed["title"], "Das weiße Band - Eine deutsche Kindergeschichte")
        self.assertEqual(parsed["director"], {"id": "1", "type": "person"})
        self.assertEqual(parsed["characters"], [{"id": "2", "type": "character"}, {"id": "3", "type": "character"}])

    def test_parse_list(self) -> None:
        parsed = cast("list", JsonAPIParser.parse(
            data=[
                {
                    "id": "1",
                    "type": "movie",
                    "attributes": {
                        "title": "Das weiße Band - Eine deutsche Kindergeschichte",
                    },
                },
                {
                    "id": "2",
                    "type": "movie",
                    "attributes": {
                        "title": "Funny Games",
                    },
                },
            ],
        ))

        self.assertEqual(parsed[0]["id"], "1")
        self.assertEqual(parsed[0]["title"], "Das weiße Band - Eine deutsche Kindergeschichte")
        self.assertEqual(parsed[1]["id"], "2")
        self.assertEqual(parsed[1]["title"], "Funny Games")

    def test_parse_included_recursive(self) -> None:
        parsed = cast("dict", JsonAPIParser.parse(
            data={
                "id": "1",
                "type": "movie",
                "attributes": {
                    "title": "Das weiße Band - Eine deutsche Kindergeschichte",
                },
                "relationships": {
                    "director": {
                        "data": {
                            "id": "1",
                            "type": "person",
                        },
                    },
                    "characters": {
                        "data": [
                            {
                                "id": "2",
                                "type": "character",
                            },
                            {
                              "id": "3",
                              "type": "character",
                            },
                        ],
                    },
                },
            },
            included=[
                {
                    "id": "1",
                    "type": "person",
                    "attributes": {
                        "name": "Michael Haneke",
                    },
                    "relationships": {
                        "favorite_movie": {
                            "data": None,
                        },
                    },
                },
                {
                    "id": "2",
                    "type": "character",
                    "attributes": {
                        "name": "Eva",
                    },
                    "relationships": {
                        "movie": {
                            "data": {
                                "id": "1",
                                "type": "movie",
                            },
                        },
                        "related_character": {
                            "data": {
                                "id": "3",
                                "type": "character",
                            },
                        },
                    },
                },
                {
                    "id": "3",
                    "type": "character",
                    "attributes": {
                        "name": "Klara",
                    },
                    "relationships": {
                        "movie": {
                            "data": {
                                "id": "1",
                                "type": "movie",
                            },
                        },
                        "related_character": {
                            "data": {
                                "id": "2",
                                "type": "character",
                            },
                        },
                    },
                },
            ],
        ))

        self.assertEqual(parsed["id"], "1")
        self.assertEqual(parsed["title"], "Das weiße Band - Eine deutsche Kindergeschichte")
        self.assertEqual(parsed["director"], {"id": "1", "name": "Michael Haneke", "favorite_movie": None})
        self.assertEqual(
            parsed["characters"][0],
            {"id": "2", "name": "Eva", "movie": parsed, "related_character": parsed["characters"][1]},
        )
        self.assertEqual(
            parsed["characters"][1],
            {"id": "3", "name": "Klara", "movie": parsed, "related_character": parsed["characters"][0]},
        )
