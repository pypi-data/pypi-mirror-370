from jambo.parser._type_parser import GenericTypeParser
from jambo.types.type_parser_options import TypeParserOptions

from pydantic import Field
from typing_extensions import Annotated, Union, Unpack


class AnyOfTypeParser(GenericTypeParser):
    mapped_type = Union

    json_schema_type = "anyOf"

    def from_properties_impl(
        self, name, properties, **kwargs: Unpack[TypeParserOptions]
    ):
        if "anyOf" not in properties:
            raise ValueError(f"Invalid JSON Schema: {properties}")

        if not isinstance(properties["anyOf"], list):
            raise ValueError(f"Invalid JSON Schema: {properties['anyOf']}")

        mapped_properties = self.mappings_properties_builder(properties, **kwargs)

        sub_properties = properties["anyOf"]

        sub_types = [
            GenericTypeParser.type_from_properties(name, subProperty, **kwargs)
            for subProperty in sub_properties
        ]

        if not kwargs.get("required", False):
            mapped_properties["default"] = mapped_properties.get("default")

        # By defining the type as Union of Annotated type we can use the Field validator
        # to enforce the constraints of each union type when needed.
        # We use Annotated to attach the Field validators to the type.
        field_types = [
            Annotated[t, Field(**v)] if v is not None else t for t, v in sub_types
        ]

        return Union[(*field_types,)], mapped_properties
