from unittest import TestCase

from jsonapi_client.serializer import JsonAPISerializer


class TestSerializer(TestCase):
    def test_serializer_resource_attribute(self) -> None:
        serialized = JsonAPISerializer.tojsonapi(name="Lana Wachowski")

        self.assertEqual(
            serialized,
            {
                "data": {
                    "attributes": {
                        "name": "Lana Wachowski",
                    },
                },
            },
        )

    def test_serializer_resource_attribute_none(self) -> None:
        serialized = JsonAPISerializer.tojsonapi(gender=None)

        self.assertEqual(
            serialized,
            {
                "data": {
                    "attributes": {
                        "gender": None,
                    },
                },
            },
        )

    def test_serializer_resource_attribute_list(self) -> None:
        serialized = JsonAPISerializer.tojsonapi(sequence=[1, 2, 3])

        self.assertEqual(
            serialized,
            {
                "data": {
                    "attributes": {
                        "sequence": [1, 2, 3],
                    },
                },
            },
        )

    def test_serializer_resource_relationship(self) -> None:
        serialized = JsonAPISerializer.tojsonapi(director={"id": "1", "type": "person"})

        self.assertEqual(
            serialized,
            {
                "data": {
                    "relationships": {
                        "director": {
                            "data": {"id": "1", "type": "person"},
                        },
                    },
                },
            },
        )

    def test_serializer_resource_relationship_none(self) -> None:
        serialized = JsonAPISerializer.tojsonapi(director={"id": None})

        self.assertEqual(
            serialized, {
                "data": {
                    "relationships": {
                        "director": {
                            "data": None,
                        },
                    },
                },
            },
        )

    def test_serializer_resource_relationship_list(self) -> None:
        serialized = JsonAPISerializer.tojsonapi(
            directors=[
                {"id": "1", "type": "person"},
                {"id": "2", "type": "person"},
            ],
        )

        self.assertEqual(
            serialized,
            {
                "data": {
                    "relationships": {
                        "directors": {
                            "data": [
                                {"id": "1", "type": "person"},
                                {"id": "2", "type": "person"},
                            ],
                        },
                    },
                },
            },
        )

    def test_serializer_resource_relationship_list_empty(self) -> None:
        serialized = JsonAPISerializer.tojsonapi(children=[{"id": None}])

        self.assertEqual(
            serialized,
            {
                "data": {
                    "relationships": {
                        "children": {
                            "data": [],
                        },
                    },
                },
            },
        )
