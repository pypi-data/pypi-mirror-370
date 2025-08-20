Bool Types
=================


The Bool type has no specific properties, it has only the generic properties:

- default: Default value for the string.
- description: Description of the string field.


Examples
-----------------


.. code-block:: python

    from jambo import SchemaConverter


    schema = {
        "title": "BoolExample",
        "type": "object",
        "properties": {
            "is_active": {
                "type": "boolean",
            },
        },
        "required": ["is_active"],
    }

    Model = SchemaConverter.build(schema)

    obj = Model(is_active=True)
    print(obj) # Output: BoolExample(is_active=True)