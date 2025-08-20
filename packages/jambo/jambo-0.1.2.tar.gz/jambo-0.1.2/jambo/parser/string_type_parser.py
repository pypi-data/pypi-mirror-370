from jambo.parser._type_parser import GenericTypeParser
from jambo.types.type_parser_options import TypeParserOptions

from pydantic import AnyUrl, EmailStr
from typing_extensions import Unpack

from datetime import date, datetime, time, timedelta
from ipaddress import IPv4Address, IPv6Address
from uuid import UUID


class StringTypeParser(GenericTypeParser):
    mapped_type = str

    json_schema_type = "type:string"

    type_mappings = {
        "maxLength": "max_length",
        "minLength": "min_length",
        "pattern": "pattern",
        "format": "format",
    }

    format_type_mapping = {
        # 7.3.1. Dates, Times, and Duration
        "date": date,
        "time": time,
        "date-time": datetime,
        "duration": timedelta,
        # 7.3.2. Email Addresses
        "email": EmailStr,
        # 7.3.3. Hostnames
        "hostname": str,
        # 7.3.4. IP Addresses
        "ipv4": IPv4Address,
        "ipv6": IPv6Address,
        # 7.3.5. Resource Identifiers
        "uri": AnyUrl,
        # "iri" # Not supported by pydantic and currently not supported by jambo
        "uuid": UUID,
    }

    format_pattern_mapping = {
        "hostname": r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$",
    }

    def from_properties_impl(
        self, name, properties, **kwargs: Unpack[TypeParserOptions]
    ):
        mapped_properties = self.mappings_properties_builder(properties, **kwargs)

        format_type = properties.get("format")
        if not format_type:
            return str, mapped_properties

        if format_type not in self.format_type_mapping:
            raise ValueError(f"Unsupported string format: {format_type}")

        mapped_type = self.format_type_mapping[format_type]
        if format_type in self.format_pattern_mapping:
            mapped_properties["pattern"] = self.format_pattern_mapping[format_type]

        return mapped_type, mapped_properties
