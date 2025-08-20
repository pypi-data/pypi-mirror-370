Array Type
=================


The Array type has the following required properties:

- items: Schema for the items in the array, which can be a type or a schema object.

And the additional supported properties:

- maxItems: Maximum number of items in the array.
- minItems: Minimum number of items in the array.
- uniqueItems: If true, all items in the array must be unique.

And the additional generic properties:

- default: Default value for the array.
- description: Description of the array field.


Examples
-----------------


1. Basic Array with maxItems and minItems:

.. code-block:: python

    from jambo import SchemaConverter


    schema = {
        "title": "ArrayExample",
        "type": "object",
        "properties": {
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "maxItems": 5,
            },
        },
        "required": ["tags"],
    }

    Model = SchemaConverter.build(schema)

    obj = Model(tags=["python", "jambo", "pydantic"])
    print(obj) # Output: ArrayExample(tags=['python', 'jambo', 'pydantic'])


    try:
        obj = Model(tags=[])  # This will raise a validation error
    except ValueError as e:
        print("Validation fails as expected:", e)  # Output: Validation fails as expected: 1 validation error for ArrayExample


2. Array with uniqueItems:

.. code-block:: python

    from jambo import SchemaConverter


    schema = {
        "title": "UniqueArrayExample",
        "type": "object",
        "properties": {
            "unique_tags": {
                "type": "array",
                "items": {"type": "string"},
                "uniqueItems": True,
            },
        },
        "required": ["unique_tags"],
    }

    Model = SchemaConverter.build(schema)

    obj = Model(unique_tags=["python", "jambo", "pydantic"])
    print(obj)  # Output: UniqueArrayExample(unique_tags={'python', 'jambo', 'pydantic'})

    try:
        obj = Model(unique_tags=["python", "jambo", "python"])  # This will raise a validation error
    except ValueError as e:
        print("Validation fails as expected:", e)  # Output: Validation fails as expected: 1 validation error for UniqueArrayExample
