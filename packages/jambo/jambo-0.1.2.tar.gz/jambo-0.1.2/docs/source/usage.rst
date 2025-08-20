Using Jambo
===================

Jambo is designed to be easy to use, it doesn't require any complex setup or configuration.
Below a example of how to use Jambo to convert a JSON Schema into a Pydantic model.


.. code-block:: python

    from jambo import SchemaConverter

    schema = {
        "title": "Person",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name"],
    }

    Person = SchemaConverter.build(schema)

    obj = Person(name="Alice", age=30)
    print(obj)
    # Output: Person(name='Alice', age=30)


The :py:meth:`SchemaConverter.build <jambo.SchemaConverter.build>` static method takes a JSON Schema dictionary and returns a Pydantic model class. You can then instantiate this class with the required fields, and it will automatically validate the data according to the schema.

If passed a description inside the schema it will also add it to the Pydantic model using the `description` field. This is useful for AI Frameworks as: LangChain, CrewAI and others, as they use this description for passing context to LLMs.


For more complex schemas and types see our documentation on

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    usage.string
    usage.numeric
    usage.bool
    usage.array
    usage.object
    usage.reference
    usage.allof
    usage.anyof
    usage.oneof
    usage.enum
    usage.const