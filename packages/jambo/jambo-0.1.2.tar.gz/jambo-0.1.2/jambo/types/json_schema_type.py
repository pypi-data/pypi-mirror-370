from typing_extensions import Dict, List, Literal, TypedDict, Union

from types import NoneType


JSONSchemaType = Literal[
    "string", "number", "integer", "boolean", "object", "array", "null"
]


JSONSchemaNativeTypes: tuple[type, ...] = (
    str, 
    int,
    float,
    bool,
    list,
    set,
    NoneType,
)


JSONType = Union[str, int, float, bool, None, Dict[str, "JSONType"], List["JSONType"]]


class JSONSchema(TypedDict, total=False):
    # Basic metadata
    title: str
    description: str
    default: JSONType
    examples: List[JSONType]

    # Type definitions
    type: Union[JSONSchemaType, List[JSONSchemaType]]

    # Object-specific keywords
    properties: Dict[str, "JSONSchema"]
    required: List[str]
    additionalProperties: Union[bool, "JSONSchema"]
    minProperties: int
    maxProperties: int
    patternProperties: Dict[str, "JSONSchema"]
    dependencies: Dict[str, Union[List[str], "JSONSchema"]]

    # Array-specific keywords
    items: Union["JSONSchema", List["JSONSchema"]]
    additionalItems: Union[bool, "JSONSchema"]
    minItems: int
    maxItems: int
    uniqueItems: bool

    # String-specific keywords
    minLength: int
    maxLength: int
    pattern: str
    format: str

    # Number-specific keywords
    minimum: float
    maximum: float
    exclusiveMinimum: float
    exclusiveMaximum: float
    multipleOf: float

    # Enum and const
    enum: List[JSONType]
    const: JSONType

    # Conditionals
    if_: "JSONSchema"  # 'if' is a reserved word in Python
    then: "JSONSchema"
    else_: "JSONSchema"  # 'else' is also a reserved word

    # Combination keywords
    allOf: List["JSONSchema"]
    anyOf: List["JSONSchema"]
    oneOf: List["JSONSchema"]
    not_: "JSONSchema"  # 'not' is a reserved word


# Fix forward references
JSONSchema.__annotations__["properties"] = Dict[str, JSONSchema]
JSONSchema.__annotations__["items"] = Union[JSONSchema, List[JSONSchema]]
JSONSchema.__annotations__["additionalItems"] = Union[bool, JSONSchema]
JSONSchema.__annotations__["additionalProperties"] = Union[bool, JSONSchema]
JSONSchema.__annotations__["patternProperties"] = Dict[str, JSONSchema]
JSONSchema.__annotations__["dependencies"] = Dict[str, Union[List[str], JSONSchema]]
JSONSchema.__annotations__["if_"] = JSONSchema
JSONSchema.__annotations__["then"] = JSONSchema
JSONSchema.__annotations__["else_"] = JSONSchema
JSONSchema.__annotations__["allOf"] = List[JSONSchema]
JSONSchema.__annotations__["anyOf"] = List[JSONSchema]
JSONSchema.__annotations__["oneOf"] = List[JSONSchema]
JSONSchema.__annotations__["not_"] = JSONSchema
