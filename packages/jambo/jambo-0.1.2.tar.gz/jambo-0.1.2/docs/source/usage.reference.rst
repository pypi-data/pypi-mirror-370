Reference Type
===================

The Reference type allows you to reference another schema by its `$ref` property. This is useful for reusing schemas across your application.

The Reference type has no specific properties, it has only the generic properties:

- default: Default value for the reference.
- description: Description of the reference field.


Examples
-----------------

1. Reference to the Root schema:

.. code-block:: python

    from jambo import SchemaConverter

    schema = {
        "title": "Person",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "emergency_contact": {
                "$ref": "#"
            }
        },
        "required": ["name"],
    }

    Model = SchemaConverter.build(schema)

    obj = Model(name="Alice", age=30, emergency_contact=Model(name="Bob", age=25))
    print(obj) # Output: Person(name='Alice', age=30, emergency_contact=Person(name='Bob', age=25))


2. Reference to a Def Schema:

.. code-block:: python

    from jambo import SchemaConverter

    schema = {
        "title": "Person",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "address": {
                "$ref": "#/$defs/Address"
            }
        },
        "required": ["name"],
        "$defs": {
            "Address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                },
                "required": ["street", "city"],
            }
        },
    }

    Model = SchemaConverter.build(schema)

    obj = Model(name="Alice", age=30, address={"street": "123 Main St", "city": "Springfield"})
    print(obj) # Output: Person(name='Alice', age=30, address=Address(street='123 Main St', city='Springfield'))


.. note::

    At the moment, Jambo doesn't have a way to expose the class definition :py:class:`Address` defined inside the `$defs` property,
    but you can access the model class by using the `Model.__fields__` attribute to get the field definitions, 
    or by using the `Model.model_fields` property to get a dictionary of field names and their types.

.. warning::

    The JSON Schema Reference specification allows for uri referneces, 
    but Jambo currently only supports root references (using the `#` symbol) 
    and def references (using the `$def` property).