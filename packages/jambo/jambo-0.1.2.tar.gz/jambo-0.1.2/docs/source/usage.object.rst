Object Type
=================


The Bool type has no specific properties, it has only the generic properties:

- default: Default value for the string.
- description: Description of the string field.


Examples
-----------------


.. code-block:: python

    from jambo import SchemaConverter

    schema = {
        "title": "Person",
        "type": "object",
        "properties": {
            "address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                },
                "default": {
                    "street": "Unknown Street",
                    "city": "Unknown City",
                },
            },
        },
        "description": "A person object containing a address.",
        "required": ["address"],
    }


    Person = SchemaConverter.build(schema)

    obj = Person.model_validate({ "address": {"street": "123 Main St", "city": "Springfield"} })
    print(obj) # Output: Person(address=Address(street='123 Main St', city='Springfield'))

    obj_default = Person()  # Uses default values
    print(obj_default)  # Output: Person(address=Address(street='Unknown Street', city='Unknown City'))
