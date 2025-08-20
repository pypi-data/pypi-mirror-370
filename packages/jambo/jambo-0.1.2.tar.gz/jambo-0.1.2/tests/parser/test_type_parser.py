from jambo.parser import StringTypeParser
from jambo.parser._type_parser import GenericTypeParser

from unittest import TestCase


class TestGenericTypeParser(TestCase):
    def test_get_impl(self):
        parser = GenericTypeParser._get_impl({"type": "string"})

        self.assertIsInstance(parser(), StringTypeParser)

    def test_get_impl_invalid_json_schema(self):
        with self.assertRaises(RuntimeError):
            StringTypeParser.json_schema_type = None
            GenericTypeParser._get_impl({"type": "string"})
        StringTypeParser.json_schema_type = "type:string"

    def test_get_impl_invalid_type(self):
        with self.assertRaises(ValueError):
            GenericTypeParser._get_impl({"type": "invalid_type"})