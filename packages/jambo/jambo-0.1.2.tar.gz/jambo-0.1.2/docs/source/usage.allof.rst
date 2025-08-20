AllOf Type
=================

The AllOf type is used to combine multiple schemas into a single schema. It allows you to specify that an object must conform to all of the specified schemas.


Examples
-----------------


.. code-block:: python

    from jambo import SchemaConverter

    schema = {
        "title": "Person",
        "description": "A person",
        "type": "object",
        "properties": {
            "name": {
                "allOf": [
                    {"type": "string", "maxLength": 11},
                    {"type": "string", "maxLength": 4},
                    {"type": "string", "minLength": 1},
                    {"type": "string", "minLength": 2},
                ]
            },
        },
    }

    Model = SchemaConverter.build(schema)

    obj = Model(name="J")
    print(obj)  # Output: Person(name='J')

    try:
        obj = Model(name="")  # This will raise a validation error
    except ValueError as e:
        print("Validation fails as expected:", e)  # Output: Validation fails as expected: 1 validation error for Person