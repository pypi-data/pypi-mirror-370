Const Type
=================

The const type is a special data type that allows a variable to be a single, fixed value.
It does not have the same properties as the other generic types, but it has the following specific properties:

- const: The fixed value that the variable must always hold.
- description: Description of the const field.


Examples
-----------------


.. code-block:: python
    
    from jambo import SchemaConverter


    schema = {
        "title": "Country",
        "type": "object",
        "properties": {
            "name": {
                "const": "United States of America",
            }
        },
        "required": ["name"],
    }

    Model = SchemaConverter.build(schema)

    obj = Model()
    self.assertEqual(obj.name, "United States of America")

    with self.assertRaises(ValueError):
        obj.name = "Canada"

    with self.assertRaises(ValueError):
        Model(name="Canada")