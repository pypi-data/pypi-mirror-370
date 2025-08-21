from unittest import TestCase
from jsonapi_client.schema import JsonAPIResourceIdentifier

class TestResourceIdentifier(TestCase):
  def test_resource_equality(self) -> None:
    identifier1 = JsonAPIResourceIdentifier(id="123", type="movies")
    identifier2 = JsonAPIResourceIdentifier(id="123", type="movies")

    self.assertEqual(identifier1, identifier2)

  def test_resource_equality_different_id(self) -> None:
    identifier1 = JsonAPIResourceIdentifier(id="123", type="movies")
    identifier2 = JsonAPIResourceIdentifier(id="456", type="movies")

    self.assertNotEqual(identifier1, identifier2)

  def test_resource_equality_different_type(self) -> None:
    identifier1 = JsonAPIResourceIdentifier(id="123", type="movies")
    identifier2 = JsonAPIResourceIdentifier(id="123", type="theaters")

    self.assertNotEqual(identifier1, identifier2)

  def test_resource_equality_different_classes(self) -> None:
    class A(JsonAPIResourceIdentifier):
      pass

    identifier1 = JsonAPIResourceIdentifier(id="123", type="movies")
    identifier2 = A(id="123", type="movies")

    self.assertNotEqual(identifier1, identifier2)
