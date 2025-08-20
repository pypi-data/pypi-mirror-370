Enum Type
==================

An enum type is a special data type that enables a variable to be a set of predefined constants. The enum type is used to define variables that can only take one out of a small set of possible values.

It does not have any specific properties, but it has the generic properties:

- default: Default value for the enum.
- description: Description of the enum field.


Examples
-----------------


.. code-block:: python

    from jambo import SchemaConverter

    schema = {
        "title": "EnumExample",
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["active", "inactive", "pending"],
                "description": "The status of the object.",
                "default": "active",
            },
        },
        "required": ["status"],
    }

    Model = SchemaConverter.build(schema)

    obj = Model(status="active")
    print(obj)  # Output: EnumExample(status=status.ACTIVE)