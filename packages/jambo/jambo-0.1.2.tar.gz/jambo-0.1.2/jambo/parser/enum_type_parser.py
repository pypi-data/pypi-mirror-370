from jambo.parser._type_parser import GenericTypeParser
from jambo.types.json_schema_type import JSONSchemaNativeTypes
from jambo.types.type_parser_options import TypeParserOptions

from typing_extensions import Unpack

from enum import Enum


class EnumTypeParser(GenericTypeParser):
    json_schema_type = "enum"

    def from_properties_impl(
        self, name, properties, **kwargs: Unpack[TypeParserOptions]
    ):
        if "enum" not in properties:
            raise ValueError(f"Enum type {name} must have 'enum' property defined.")

        enum_values = properties["enum"]

        if not isinstance(enum_values, list):
            raise ValueError(f"Enum type {name} must have 'enum' as a list of values.")

        if any(
            not isinstance(value, JSONSchemaNativeTypes) for value in enum_values
        ):
            raise ValueError(
                f"Enum type {name} must have 'enum' values of allowed types: {JSONSchemaNativeTypes}."
            )

        # Create a new Enum type dynamically
        enum_type = Enum(name, {str(value).upper(): value for value in enum_values})
        parsed_properties = self.mappings_properties_builder(properties, **kwargs)

        if (
            "default" in parsed_properties and parsed_properties["default"] is not None
        ):            
            parsed_properties["default"] = enum_type(parsed_properties["default"])

        return enum_type, parsed_properties
