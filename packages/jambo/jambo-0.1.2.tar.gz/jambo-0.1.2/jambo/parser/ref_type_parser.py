from jambo.parser import GenericTypeParser
from jambo.types.type_parser_options import TypeParserOptions

from typing_extensions import Any, ForwardRef, Literal, TypeVar, Union, Unpack


RefType = TypeVar("RefType", bound=Union[type, ForwardRef])

RefStrategy = Literal["forward_ref", "def_ref"]


class RefTypeParser(GenericTypeParser):
    json_schema_type = "$ref"

    def from_properties_impl(
        self, name: str, properties: dict[str, Any], **kwargs: Unpack[TypeParserOptions]
    ) -> tuple[RefType, dict]:
        if "$ref" not in properties:
            raise ValueError(f"RefTypeParser: Missing $ref in properties for {name}")

        context = kwargs.get("context")
        if context is None:
            raise RuntimeError(
                f"RefTypeParser: Missing `content` in properties for {name}"
            )

        ref_cache = kwargs.get("ref_cache")
        if ref_cache is None:
            raise RuntimeError(
                f"RefTypeParser: Missing `ref_cache` in properties for {name}"
            )

        mapped_properties = self.mappings_properties_builder(properties, **kwargs)

        ref_strategy, ref_name, ref_property = self._examine_ref_strategy(
            name, properties, **kwargs
        )

        ref_state = self._get_ref_from_cache(ref_name, ref_cache)
        if ref_state is not None:
            # If the reference is either processing or already cached
            return ref_state, mapped_properties

        ref_cache[ref_name] = self._parse_from_strategy(
            ref_strategy, ref_name, ref_property, **kwargs
        )

        return ref_cache[ref_name], mapped_properties

    def _parse_from_strategy(
        self,
        ref_strategy: RefStrategy,
        ref_name: str,
        ref_property: dict[str, Any],
        **kwargs: Unpack[TypeParserOptions],
    ):
        match ref_strategy:
            case "forward_ref":
                mapped_type = ForwardRef(ref_name)
            case "def_ref":
                mapped_type, _ = GenericTypeParser.type_from_properties(
                    ref_name, ref_property, **kwargs
                )
            case _:
                raise ValueError(
                    f"RefTypeParser: Unsupported $ref {ref_property['$ref']}"
                )

        return mapped_type

    def _get_ref_from_cache(
        self, ref_name: str, ref_cache: dict[str, type]
    ) -> RefType | type | None:
        try:
            ref_state = ref_cache[ref_name]

            if ref_state is None:
                # If the reference is being processed, we return a ForwardRef
                return ForwardRef(ref_name)

            # If the reference is already cached, we return it
            return ref_state
        except KeyError:
            # If the reference is not in the cache, we will set it to None
            ref_cache[ref_name] = None

    def _examine_ref_strategy(
        self, name: str, properties: dict[str, Any], **kwargs: Unpack[TypeParserOptions]
    ) -> tuple[RefStrategy, str, dict] | None:
        if properties["$ref"] == "#":
            ref_name = kwargs["context"].get("title")
            if ref_name is None:
                raise ValueError(
                    "RefTypeParser: Missing title in properties for $ref of Root Reference"
                )
            return "forward_ref", ref_name, {}

        if properties["$ref"].startswith("#/$defs/"):
            target_name, target_property = self._extract_target_ref(
                name, properties, **kwargs
            )
            return "def_ref", target_name, target_property

        raise ValueError(
            "RefTypeParser: Only Root and $defs references are supported at the moment"
        )

    def _extract_target_ref(
        self, name: str, properties: dict[str, Any], **kwargs: Unpack[TypeParserOptions]
    ) -> tuple[str, dict]:
        target_name = None
        target_property = kwargs["context"]
        for prop_name in properties["$ref"].split("/")[1:]:
            if prop_name not in target_property:
                raise ValueError(
                    f"RefTypeParser: Missing {prop_name} in"
                    " properties for $ref {properties['$ref']}"
                )
            target_name = prop_name
            target_property = target_property[prop_name]

        if target_name is None or target_property is None:
            raise ValueError(f"RefTypeParser: Invalid $ref {properties['$ref']}")

        return target_name, target_property
