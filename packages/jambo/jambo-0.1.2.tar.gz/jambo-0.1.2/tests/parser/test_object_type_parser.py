from jambo.parser import ObjectTypeParser

from unittest import TestCase


class TestObjectTypeParser(TestCase):
    def test_object_type_parser(self):
        parser = ObjectTypeParser()

        properties = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
        }

        Model, _args = parser.from_properties_impl("placeholder", properties)

        obj = Model(name="name", age=10)

        self.assertEqual(obj.name, "name")
        self.assertEqual(obj.age, 10)

    def test_object_type_parser_with_default(self):
        parser = ObjectTypeParser()

        properties = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "default": {
                "name": "default_name",
                "age": 20,
            },
        }

        _, type_validator = parser.from_properties_impl("placeholder", properties)

        # Check default value
        default_obj = type_validator["default_factory"]()
        self.assertEqual(default_obj.name, "default_name")
        self.assertEqual(default_obj.age, 20)

        # Chekc default factory new object id
        new_obj = type_validator["default_factory"]()
        self.assertNotEqual(id(default_obj), id(new_obj))
