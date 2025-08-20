OneOf Type
=================

The OneOf type is used to specify that an object must conform to exactly one of the specified schemas. Unlike AnyOf which allows matching multiple schemas, OneOf enforces that the data matches one and only one of the provided schemas.


Examples
-----------------

1. **Overlapping String Example** - A field that accepts strings with overlapping constraints:

.. code-block:: python

    from jambo import SchemaConverter

    schema = {
        "title": "SimpleExample",
        "type": "object",
        "properties": {
            "value": {
                "oneOf": [
                    {"type": "string", "maxLength": 6},
                    {"type": "string", "minLength": 4}
                ]
            }
        },
        "required": ["value"]
    }

    Model = SchemaConverter.build(schema)

    # Valid: Short string (matches first schema only)
    obj1 = Model(value="hi")
    print(obj1.value)  # Output: hi

    # Valid: Long string (matches second schema only)
    obj2 = Model(value="very long string")
    print(obj2.value)  # Output: very long string

    # Invalid: Medium string (matches BOTH schemas - violates oneOf)
    try:
        obj3 = Model(value="hello")  # 5 chars: matches maxLength=6 AND minLength=4
    except ValueError as e:
        print("Validation fails as expected:", e)


2. **Discriminator Example** - Different shapes with a type field:

.. code-block:: python

    from jambo import SchemaConverter

    schema = {
        "title": "Shape",
        "type": "object",
        "properties": {
            "shape": {
                "oneOf": [
                    {
                        "type": "object",
                        "properties": {
                            "type": {"const": "circle"},
                            "radius": {"type": "number", "minimum": 0}
                        },
                        "required": ["type", "radius"]
                    },
                    {
                        "type": "object",
                        "properties": {
                            "type": {"const": "rectangle"},
                            "width": {"type": "number", "minimum": 0},
                            "height": {"type": "number", "minimum": 0}
                        },
                        "required": ["type", "width", "height"]
                    }
                ],
                "discriminator": {
                    "propertyName": "type"
                }
            }
        },
        "required": ["shape"]
    }

    Model = SchemaConverter.build(schema)

    # Valid: Circle
    circle = Model(shape={"type": "circle", "radius": 5.0})
    print(circle.shape.type)  # Output: circle

    # Valid: Rectangle
    rectangle = Model(shape={"type": "rectangle", "width": 10, "height": 20})
    print(rectangle.shape.type)  # Output: rectangle

    # Invalid: Wrong properties for the type
    try:
        invalid = Model(shape={"type": "circle", "width": 10})
    except ValueError as e:
        print("Validation fails as expected:", e)


.. note::

    OneOf ensures exactly one schema matches. The discriminator helps Pydantic efficiently determine which schema to use based on a specific property value.

.. warning::

    If your data could match multiple schemas in a oneOf, validation will fail. Ensure schemas are mutually exclusive.

.. warning::

    The discriminator feature is not officially in the JSON Schema specification, it was introduced by OpenAPI. Use it with caution and ensure it fits your use case.
