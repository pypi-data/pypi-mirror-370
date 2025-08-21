from unittest import TestCase
from jsonapi_client.schema import JsonAPIResourceSchema

class TestResourceSchema(TestCase):
  def test_resource_equality(self) -> None:
    resource1 = JsonAPIResourceSchema(id="123")
    resource2 = JsonAPIResourceSchema(id="123")

    self.assertEqual(resource1, resource2)

  def test_resource_equality_different_id(self) -> None:
    resource1 = JsonAPIResourceSchema(id="123")
    resource2 = JsonAPIResourceSchema(id="456")

    self.assertNotEqual(resource1, resource2)

  def test_resource_equality_different_classes(self) -> None:
    class A(JsonAPIResourceSchema):
      pass

    class B(JsonAPIResourceSchema):
      pass

    resource1 = A(id="123")
    resource2 = B(id="123")

    self.assertNotEqual(resource1, resource2)
