AnyOf Type
=================

The AnyOf type is used to specify that an object can conform to any one of the specified schemas. It allows for flexibility in the structure of the data, as it can match multiple possible schemas.


Examples
-----------------


.. code-block:: python

    from jambo import SchemaConverter


    schema = {
        "title": "Person",
        "description": "A person",
        "type": "object",
        "properties": {
            "id": {
                "anyOf": [
                    {"type": "integer"},
                    {"type": "string"},
                ]
            },
        },
    }

    Model = SchemaConverter.build(schema)

    obj1 = Model(id="1")
    print(obj1)  # Output: Person(id='1')

    obj2 = Model(id=1)
    print(obj2)  # Output: Person(id=1)

    try:
        obj3 = Model(name=1.1)  # This will raise a validation error
    except ValueError as e:
        print("Validation fails as expected:", e)  # Output: Validation fails as expected: 1 validation error for Person